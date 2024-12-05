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
        message = f"[User {user_id}] {activity}"
        
        log_func = getattr(logger, level.lower())
        try:
            if level in ["ERROR", "WARNING"]:
                try:
                    raise Exception(f"Simulated {level.lower()}: {message}")
                except Exception as e:
                    if level == "ERROR":
                        logger.error(str(e), exc_info=True)
                    else:
                        logger.warning(str(e))
            else:
                log_func(message)
        except Exception as e:
            logger.error(f"Logging failed: {str(e)}", exc_info=True)
        
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
    app_logger.info("Application starting - Version 1.0.0")
    
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
            auth_logger.info(f"User session started - {user_id}")
        
        # Monitor performance while users are active
        start_time = time.time()
        while any(t.is_alive() for t in threads):
            # Simulate performance metrics
            cpu = random.uniform(20, 80)
            memory = random.uniform(40, 90)
            active = len([t for t in threads if t.is_alive()])
            perf_logger.info(
                f"Performance metrics - CPU: {cpu:.1f}%, Memory: {memory:.1f}%, "
                f"Active threads: {active}"
            )
            time.sleep(5)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        app_logger.info("All user sessions completed")
        
    except Exception as e:
        app_logger.error(f"Application error: {str(e)}", exc_info=True)
    finally:
        # Log application shutdown
        runtime = time.time() - start_time
        app_logger.info(f"Application shutting down - Runtime: {runtime:.1f}s")

if __name__ == "__main__":
    main()
