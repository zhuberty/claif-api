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

# # Configure the uvicorn logger  
# logging = logging.getLogger("uvicorn.error")
# logging.setLevel(uvicorn_log_level)
# logging.name = "uvicorn"

# # Optionally, add a handler if not already present
# if not logging.handlers:
#     uvi_handler = logging.StreamHandler()
#     uvi_handler.setLevel(uvicorn_log_level)
#     uvi_formatter = logging.Formatter('%(name)s:%(levelname)s:\t%(message)s')
#     uvi_handler.setFormatter(uvi_formatter)
#     logging.addHandler(uvi_handler)

# Configure the SQLAlchemy logger
# sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
# sqlalchemy_logger.setLevel(sql_log_level)
# sqlalchemy_logger.name = "sqlalchemy"

# Optionally, add a handler if not already present
# if not sqlalchemy_logger.handlers:
#     sql_handler = logging.StreamHandler()
#     sql_handler.setLevel(sql_log_level)
#     sql_formatter = logging.Formatter('%(name)s:%(levelname)s:\t%(message)s')
#     sql_handler.setFormatter(sql_formatter)
#     sqlalchemy_logger.addHandler(sql_handler)
