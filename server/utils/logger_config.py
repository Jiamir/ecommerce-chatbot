import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """Setup application logging"""
    try:
        if not os.path.exists("logs"):
            os.makedirs("logs")
    except OSError as e:
        print(f"Error creating logs directory: {e}")
        sys.exit(1)

    if app.config.get("DEBUG"):
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = RotatingFileHandler(
        "logs/ecommerce_chatbot.log", maxBytes=10240000, backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging_level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Configure app.logger to inherit from root (no duplicate handlers)
    app.logger.setLevel(logging_level)

    loggers = [
        "services.chat_service",
        "services.vector_service",
        "services.product_service",
        "services.auth_service",
        "routes.auth_routes",
        "routes.product_routes",
        "routes.chat_routes",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging_level)

    # Suppress noisy third-party logs
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)  # Reduce MongoDB heartbeat noise

    app.logger.info("Logging configured successfully")