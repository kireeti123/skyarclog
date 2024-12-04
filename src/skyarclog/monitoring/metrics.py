"""
Performance monitoring and metrics collection for the logging system.
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from threading import Lock
import statistics
from collections import deque
import psutil
import os

@dataclass
class LoggingMetrics:
    """Metrics for logging operations."""
    total_logs: int = 0
    failed_logs: int = 0
    total_batches: int = 0
    failed_batches: int = 0
    avg_log_size_bytes: float = 0
    avg_batch_size: float = 0
    avg_processing_time_ms: float = 0
    avg_queue_time_ms: float = 0
    memory_usage_mb: float = 0
    cpu_usage_percent: float = 0
    disk_write_bytes: int = 0
    network_bytes_sent: int = 0

class MetricsCollector:
    """
    Collects and manages logging system metrics.
    Thread-safe metrics collection with rolling windows.
    """
    
    def __init__(self, window_size: int = 1000):
        """
        Initialize metrics collector.
        
        Args:
            window_size: Number of measurements to keep for rolling averages
        """
        self._lock = Lock()
        self._window_size = window_size
        self._process = psutil.Process(os.getpid())
        
        # Metrics storage
        self._processing_times = deque(maxlen=window_size)
        self._queue_times = deque(maxlen=window_size)
        self._log_sizes = deque(maxlen=window_size)
        self._batch_sizes = deque(maxlen=window_size)
        
        # Counters
        self._total_logs = 0
        self._failed_logs = 0
        self._total_batches = 0
        self._failed_batches = 0
        
        # IO metrics
        self._last_io_counter = self._process.io_counters()
        self._last_net_counter = psutil.net_io_counters()
        self._last_check_time = time.time()
        
    def record_log(
        self,
        size_bytes: int,
        processing_time_ms: float,
        queue_time_ms: float,
        success: bool = True
    ) -> None:
        """Record metrics for a single log entry."""
        with self._lock:
            self._total_logs += 1
            if not success:
                self._failed_logs += 1
            
            self._processing_times.append(processing_time_ms)
            self._queue_times.append(queue_time_ms)
            self._log_sizes.append(size_bytes)
            
    def record_batch(
        self,
        size: int,
        success: bool = True
    ) -> None:
        """Record metrics for a batch operation."""
        with self._lock:
            self._total_batches += 1
            if not success:
                self._failed_batches += 1
            
            self._batch_sizes.append(size)
            
    def _calculate_io_metrics(self) -> tuple[int, int]:
        """Calculate IO metrics since last check."""
        current_time = time.time()
        elapsed = current_time - self._last_check_time
        
        # Get current counters
        io_counter = self._process.io_counters()
        net_counter = psutil.net_io_counters()
        
        # Calculate rates
        disk_write_bytes = (
            io_counter.write_bytes - self._last_io_counter.write_bytes
        ) / elapsed
        network_bytes = (
            net_counter.bytes_sent - self._last_net_counter.bytes_sent
        ) / elapsed
        
        # Update last values
        self._last_io_counter = io_counter
        self._last_net_counter = net_counter
        self._last_check_time = current_time
        
        return int(disk_write_bytes), int(network_bytes)
            
    def get_metrics(self) -> LoggingMetrics:
        """Get current metrics snapshot."""
        with self._lock:
            # Calculate averages
            avg_processing_time = (
                statistics.mean(self._processing_times)
                if self._processing_times else 0
            )
            avg_queue_time = (
                statistics.mean(self._queue_times)
                if self._queue_times else 0
            )
            avg_log_size = (
                statistics.mean(self._log_sizes)
                if self._log_sizes else 0
            )
            avg_batch_size = (
                statistics.mean(self._batch_sizes)
                if self._batch_sizes else 0
            )
            
            # Get system metrics
            memory_info = self._process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            cpu_percent = self._process.cpu_percent()
            
            # Get IO metrics
            disk_write_bytes, network_bytes = self._calculate_io_metrics()
            
            return LoggingMetrics(
                total_logs=self._total_logs,
                failed_logs=self._failed_logs,
                total_batches=self._total_batches,
                failed_batches=self._failed_batches,
                avg_log_size_bytes=avg_log_size,
                avg_batch_size=avg_batch_size,
                avg_processing_time_ms=avg_processing_time,
                avg_queue_time_ms=avg_queue_time,
                memory_usage_mb=memory_mb,
                cpu_usage_percent=cpu_percent,
                disk_write_bytes=disk_write_bytes,
                network_bytes_sent=network_bytes
            )
            
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._processing_times.clear()
            self._queue_times.clear()
            self._log_sizes.clear()
            self._batch_sizes.clear()
            self._total_logs = 0
            self._failed_logs = 0
            self._total_batches = 0
            self._failed_batches = 0
            
class PerformanceMonitor:
    """
    Monitors and manages logging system performance.
    Provides automatic scaling and throttling based on metrics.
    """
    
    def __init__(
        self,
        config: Dict,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        Initialize performance monitor.
        
        Args:
            config: Performance monitoring configuration
            metrics_collector: Optional metrics collector instance
        """
        self.config = config
        self.metrics = metrics_collector or MetricsCollector(
            window_size=config.get('metrics_window_size', 1000)
        )
        
        # Performance thresholds
        self.max_memory_mb = config.get('max_memory_mb', 1024)  # 1 GB
        self.max_cpu_percent = config.get('max_cpu_percent', 80)
        self.max_disk_write_mbs = config.get('max_disk_write_mbs', 50)  # 50 MB/s
        self.max_network_mbs = config.get('max_network_mbs', 50)  # 50 MB/s
        
        # Scaling configuration
        self.min_workers = config.get('min_workers', 2)
        self.max_workers = config.get('max_workers', 8)
        self.scale_up_threshold = config.get('scale_up_threshold', 0.75)
        self.scale_down_threshold = config.get('scale_down_threshold', 0.25)
        
    def should_throttle(self) -> bool:
        """
        Check if logging should be throttled based on system metrics.
        
        Returns:
            bool: True if logging should be throttled
        """
        metrics = self.metrics.get_metrics()
        
        # Check system resource usage
        if metrics.memory_usage_mb > self.max_memory_mb:
            return True
            
        if metrics.cpu_usage_percent > self.max_cpu_percent:
            return True
            
        if metrics.disk_write_bytes / (1024 * 1024) > self.max_disk_write_mbs:
            return True
            
        if metrics.network_bytes_sent / (1024 * 1024) > self.max_network_mbs:
            return True
            
        return False
        
    def get_optimal_worker_count(self) -> int:
        """
        Calculate optimal number of worker threads based on metrics.
        
        Returns:
            int: Recommended number of worker threads
        """
        metrics = self.metrics.get_metrics()
        current_workers = self.config.get('current_workers', self.min_workers)
        
        # Calculate load factors
        cpu_load = metrics.cpu_usage_percent / 100
        memory_load = metrics.memory_usage_mb / self.max_memory_mb
        io_load = (
            metrics.disk_write_bytes / (self.max_disk_write_mbs * 1024 * 1024)
        )
        network_load = (
            metrics.network_bytes_sent / (self.max_network_mbs * 1024 * 1024)
        )
        
        # Use maximum load as scaling factor
        max_load = max(cpu_load, memory_load, io_load, network_load)
        
        if max_load > self.scale_up_threshold:
            # Scale up
            return min(
                current_workers + 1,
                self.max_workers
            )
        elif max_load < self.scale_down_threshold:
            # Scale down
            return max(
                current_workers - 1,
                self.min_workers
            )
            
        return current_workers
        
    def get_performance_report(self) -> Dict:
        """
        Generate detailed performance report.
        
        Returns:
            Dict: Performance metrics and recommendations
        """
        metrics = self.metrics.get_metrics()
        
        return {
            'metrics': {
                'throughput': {
                    'logs_per_second': metrics.total_logs / (
                        metrics.avg_processing_time_ms / 1000
                    ) if metrics.avg_processing_time_ms > 0 else 0,
                    'success_rate': (
                        (metrics.total_logs - metrics.failed_logs)
                        / metrics.total_logs * 100
                    ) if metrics.total_logs > 0 else 100,
                    'batch_success_rate': (
                        (metrics.total_batches - metrics.failed_batches)
                        / metrics.total_batches * 100
                    ) if metrics.total_batches > 0 else 100
                },
                'latency': {
                    'processing_time_ms': metrics.avg_processing_time_ms,
                    'queue_time_ms': metrics.avg_queue_time_ms
                },
                'resource_usage': {
                    'memory_mb': metrics.memory_usage_mb,
                    'cpu_percent': metrics.cpu_usage_percent,
                    'disk_write_mbs': metrics.disk_write_bytes / (1024 * 1024),
                    'network_mbs': metrics.network_bytes_sent / (1024 * 1024)
                }
            },
            'recommendations': {
                'throttling_required': self.should_throttle(),
                'optimal_workers': self.get_optimal_worker_count(),
                'performance_issues': self._identify_performance_issues(metrics)
            }
        }
        
    def _identify_performance_issues(
        self,
        metrics: LoggingMetrics
    ) -> List[str]:
        """Identify potential performance issues."""
        issues = []
        
        # Check for high failure rates
        if metrics.total_logs > 0:
            failure_rate = metrics.failed_logs / metrics.total_logs
            if failure_rate > 0.05:  # More than 5% failures
                issues.append(
                    f"High log failure rate: {failure_rate:.1%}"
                )
                
        if metrics.total_batches > 0:
            batch_failure_rate = metrics.failed_batches / metrics.total_batches
            if batch_failure_rate > 0.05:
                issues.append(
                    f"High batch failure rate: {batch_failure_rate:.1%}"
                )
                
        # Check for resource usage
        if metrics.memory_usage_mb > self.max_memory_mb * 0.9:
            issues.append("Memory usage approaching limit")
            
        if metrics.cpu_usage_percent > self.max_cpu_percent * 0.9:
            issues.append("CPU usage approaching limit")
            
        # Check for latency issues
        if metrics.avg_processing_time_ms > 100:  # More than 100ms
            issues.append("High average processing time")
            
        if metrics.avg_queue_time_ms > 1000:  # More than 1 second
            issues.append("High average queue time")
            
        return issues
