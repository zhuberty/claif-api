import os


# Keycloak settings
KEYCLOAK_SERVER_URL = os.environ.get("KEYCLOAK_SERVER_URL", "http://localhost:8085")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "fastapi")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "fastapi-client")
OPENAPI_KEYCLOAK_SERVER_URL = os.environ.get("OPENAPI_KEYCLOAK_SERVER_URL", "http://localhost:8085")
UVI_LOG_LEVEL = os.environ.get("UVICORN_LOGGING_LEVEL", "DEBUG")
SQL_LOGGING_LEVEL = os.environ.get("SQL_LOGGING_LEVEL", "INFO")