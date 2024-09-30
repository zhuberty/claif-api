import logging
from utils.env import UVI_LOG_LEVEL, SQL_LOGGING_LEVEL

# Determine the logging levels
uvicorn_log_level = logging.DEBUG if UVI_LOG_LEVEL == "DEBUG" else logging.INFO
sql_log_level = logging.DEBUG if SQL_LOGGING_LEVEL == "DEBUG" else logging.WARN

# Configure the root logger to the lowest level needed
logging.basicConfig(
    level=uvicorn_log_level,
    format='python:%(levelname)s:\t%(message)s',
)
