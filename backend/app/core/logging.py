import logging
import sys

def setup_logging(debug: bool = False):
    """
    Setup structured logging for the application.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Basic configuration
    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Set levels for third party libraries to avoid spam
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    logger = logging.getLogger("basma_api")
    logger.setLevel(log_level)
    
    return logger

# Create a default logger instance
logger = logging.getLogger("basma_api")
