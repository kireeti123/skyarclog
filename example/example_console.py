from skyarclog.logger import SkyArcLogger

logger = SkyArcLogger("skyarclog_logging.json")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")