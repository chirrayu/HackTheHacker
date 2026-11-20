import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO", log_dir: str = None) -> logging.Logger:
    """Configures structured application logging with rotating file handler and console fallback."""
    logger = logging.getLogger("hackthehacker")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    if not logger.handlers:
        log_format = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console Handler (always reliable)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(numeric_level)
        logger.addHandler(console_handler)
        
        # Rotating File Handler (optional, falls back gracefully if write restricted)
        if log_dir:
            try:
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, "hackthehacker.log")
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10 * 1024 * 1024,
                    backupCount=5,
                    encoding="utf-8"
                )
                file_handler.setFormatter(log_format)
                file_handler.setLevel(numeric_level)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.debug(f"File logging not enabled: {e}")
        
    return logger
