"""Example demonstrating Azure Application Insights logging with SkyArcLog."""

import os
import sys
import time
import uuid
import random
from datetime import datetime
from skyarclog.logger import SkyArcLogger

def simulate_web_requests(logger):
    """Simulate web application requests with telemetry."""
    for i in range(20):
        # Generate request context
        request_id = str(uuid.uuid4())
        user_id = f"user_{random.randint(1000, 9999)}"
        
        # Start request timing
        start_time = time.time()
        
        try:
            # Simulate request processing
            logger.info(
                f"Processing request {request_id}",
                operation_id=request_id,
                user_id=user_id,
                endpoint="/api/data",
                http_method="GET",
                client_ip="192.168.1." + str(random.randint(1, 255))
            )
            
            # Simulate some work
            time.sleep(random.uniform(0.1, 0.5))
            
            # Simulate random failures
            if random.random() < 0.2:
                raise ValueError("Invalid request parameters")
            
            # Log successful request
            duration = time.time() - start_time
            logger.info(
                f"Request {request_id} completed",
                operation_id=request_id,
                user_id=user_id,
                duration_ms=int(duration * 1000),
                status_code=200
            )
            
        except Exception as e:
            # Log failed request
            duration = time.time() - start_time
            logger.error(
                f"Request {request_id} failed",
                operation_id=request_id,
                user_id=user_id,
                duration_ms=int(duration * 1000),
                status_code=400,
                error_type=type(e).__name__,
                error_message=str(e)
            )

def simulate_dependency_calls(logger):
    """Simulate external dependency calls with telemetry."""
    dependencies = [
        ("sql_database", "SELECT * FROM users"),
        ("redis_cache", "GET user_preferences"),
        ("external_api", "POST /api/v1/process")
    ]
    
    for i in range(15):
        # Select random dependency
        dep_type, dep_call = random.choice(dependencies)
        operation_id = str(uuid.uuid4())
        
        # Start dependency timing
        start_time = time.time()
        
        try:
            # Log dependency call start
            logger.info(
                f"Calling {dep_type}",
                operation_id=operation_id,
                dependency_type=dep_type,
                dependency_call=dep_call,
                target=f"{dep_type}.example.com"
            )
            
            # Simulate dependency call
            time.sleep(random.uniform(0.2, 0.8))
            
            # Simulate random failures
            if random.random() < 0.15:
                raise ConnectionError(f"Failed to connect to {dep_type}")
            
            # Log successful dependency call
            duration = time.time() - start_time
            logger.info(
                f"Dependency call completed",
                operation_id=operation_id,
                dependency_type=dep_type,
                duration_ms=int(duration * 1000),
                success=True
            )
            
        except Exception as e:
            # Log failed dependency call
            duration = time.time() - start_time
            logger.error(
                f"Dependency call failed",
                operation_id=operation_id,
                dependency_type=dep_type,
                duration_ms=int(duration * 1000),
                success=False,
                error_type=type(e).__name__,
                error_message=str(e)
            )

def simulate_custom_metrics(logger):
    """Simulate custom application metrics."""
    # Simulate user session metrics
    active_sessions = random.randint(100, 500)
    logger.info(
        "Active user sessions",
        metric_name="active_sessions",
        metric_value=active_sessions,
        metric_type="gauge"
    )
    
    # Simulate response time metrics
    for endpoint in ["/api/users", "/api/orders", "/api/products"]:
        response_time = random.uniform(50, 200)
        logger.info(
            f"API response time for {endpoint}",
            metric_name="api_response_time",
            metric_value=response_time,
            metric_type="timing",
            endpoint=endpoint
        )
    
    # Simulate business metrics
    orders_processed = random.randint(10, 50)
    order_value = random.uniform(1000, 5000)
    logger.info(
        "Orders processed",
        metric_name="orders_processed",
        metric_value=orders_processed,
        metric_type="counter",
        total_value=order_value
    )

def main():
    """Run Application Insights logging example."""
    # Get the absolute path to the configuration file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'skyarclog_logging.json')

    # Initialize logger with configuration
    logger = SkyArcLogger(config_path)
    
    try:
        print("\n=== Phase 1: Web Request Telemetry ===")
        print("(Simulating web requests with success and failure scenarios)")
        simulate_web_requests(logger)
        
        print("\n=== Phase 2: Dependency Call Telemetry ===")
        print("(Simulating external dependency calls)")
        simulate_dependency_calls(logger)
        
        print("\n=== Phase 3: Custom Metrics ===")
        print("(Sending custom application metrics)")
        simulate_custom_metrics(logger)
        
        # Log final summary
        logger.info(
            "Example completed",
            timestamp=datetime.utcnow().isoformat(),
            phases_completed=[
                "web_requests",
                "dependency_calls",
                "custom_metrics"
            ]
        )
    
    finally:
        # Ensure all telemetry is sent
        logger.close()

if __name__ == "__main__":
    main()
