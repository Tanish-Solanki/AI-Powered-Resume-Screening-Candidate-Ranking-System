import logging
import sys

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Configure specific loggers if needed
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
