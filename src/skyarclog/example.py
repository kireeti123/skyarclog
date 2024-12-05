import os
import time
from pathlib import Path
from dotenv import load_dotenv
from logger import SkyArcLogger
import logging
import random
import threading
from datetime import datetime

def simulate_user_activity(logger: logging.Logger, user_id: str, duration: int = 60):
    """Simulate user activity generating various log levels."""
    activities = [
        ("Viewing product catalog", "INFO"),
        ("Adding item to cart", "INFO"),
        ("Failed login attempt", "WARNING"),
        ("Payment processing", "INFO"),
        ("Database connection timeout", "ERROR"),
        ("Cache miss", "DEBUG"),
        ("Order completed", "INFO"),
        ("Session expired", "WARNING")
    ]
    
    start_time = time.time()
    while time.time() - start_time < duration:
        activity, level = random.choice(activities)
        extra = {
            'user_id': user_id,
            'session_id': f"sess_{random.randint(1000, 9999)}",
            'client_ip': f"192.168.1.{random.randint(1, 255)}",
            'timestamp': datetime.utcnow().isoformat()
        }
        
        log_func = getattr(logger, level.lower())
        try:
            if level in ["ERROR", "WARNING"]:
                try:
                    raise Exception(f"Simulated {level.lower()}: {activity}")
                except Exception as e:
                    if level == "ERROR":
                        logger.error(str(e), extra=extra, exc_info=True)
                    else:
                        logger.warning(str(e), extra=extra)
            else:
                log_func(f"User Activity: {activity}", extra=extra)
        except Exception as e:
            logger.error(f"Logging failed: {str(e)}", extra=extra, exc_info=True)
        
        time.sleep(random.uniform(0.1, 2.0))

def main():
    # Initialize logger with environment file from the current directory
    env_path = Path(__file__).parent / '.env'
    logger = SkyArcLogger(env_path=str(env_path))
    
    # Get different loggers for different components
    app_logger = logger.get_logger('app')
    auth_logger = logger.get_logger('auth')
    perf_logger = logger.get_logger('performance')
    
    # Log application startup
    app_logger.info("Application starting", extra={
        'version': '1.0.0',
        'environment': 'production',
        'startup_time': datetime.utcnow().isoformat()
    })
    
    try:
        # Simulate multiple users
        threads = []
        for i in range(3):
            user_id = f"user_{random.randint(1000, 9999)}"
            thread = threading.Thread(
                target=simulate_user_activity,
                args=(app_logger, user_id),
                name=f"UserSimulation-{user_id}"
            )
            threads.append(thread)
            thread.start()
            
            # Log user session start
            auth_logger.info(f"User session started", extra={
                'user_id': user_id,
                'thread_id': thread.ident
            })
        
        # Monitor performance while users are active
        start_time = time.time()
        while any(t.is_alive() for t in threads):
            # Simulate performance metrics
            perf_logger.info("Performance metrics", extra={
                'cpu_usage': random.uniform(20, 80),
                'memory_usage': random.uniform(40, 90),
                'active_threads': len([t for t in threads if t.is_alive()]),
                'uptime': time.time() - start_time
            })
            time.sleep(5)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        app_logger.info("All user sessions completed")
        
    except Exception as e:
        app_logger.error("Application error", exc_info=True, extra={
            'error_type': type(e).__name__,
            'error_details': str(e)
        })
    finally:
        # Log application shutdown
        app_logger.info("Application shutting down", extra={
            'shutdown_time': datetime.utcnow().isoformat(),
            'total_runtime': time.time() - start_time
        })

if __name__ == "__main__":
    main()
