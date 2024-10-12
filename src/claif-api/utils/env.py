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
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio-user")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minio-password")
MINIO_AUDIO_BUCKET = os.environ.get("MINIO_AUDIO_BUCKET", "audio")
