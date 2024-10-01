import os


# Keycloak settings
KEYCLOAK_SERVER_URL = os.environ.get("KEYCLOAK_SERVER_URL", "http://localhost:8085")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "fastapi")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "fastapi-client")
OPENAPI_KEYCLOAK_SERVER_URL = os.environ.get("OPENAPI_KEYCLOAK_SERVER_URL", "http://localhost:8085")
UVI_LOG_LEVEL = os.environ.get("UVICORN_LOGGING_LEVEL", "DEBUG")
SQL_LOGGING_LEVEL = os.environ.get("SQL_LOGGING_LEVEL", "INFO")
CLAIF_API_PORT = os.environ.get("CLAIF_API_PORT", 8000)
CLAIF_API_HOST = os.environ.get("CLAIF_API_HOST", "localhost")
TEST_USER_USERNAME = os.environ.get("TEST_USER_USERNAME", "testuser")
TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD", "testpassword")