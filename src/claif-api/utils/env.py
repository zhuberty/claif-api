import os


# Keycloak settings
KEYCLOAK_SERVER_URL = os.environ.get("KEYCLOAK_SERVER_URL", "http://localhost:8085")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "claif-api")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "claif-api-client")
OPENAPI_KEYCLOAK_SERVER_URL = os.environ.get("OPENAPI_KEYCLOAK_SERVER_URL", "http://localhost:8085")
UVI_LOG_LEVEL = os.environ.get("UVICORN_LOGGING_LEVEL", "DEBUG")
SQL_LOGGING_LEVEL = os.environ.get("SQL_LOGGING_LEVEL", "INFO")
CLAIF_API_PORT = os.environ.get("CLAIF_API_PORT", 8000)
CLAIF_API_HOST = os.environ.get("CLAIF_API_HOST", "localhost")
TEST_USER_USERNAME = os.environ.get("TEST_USER_USERNAME", "testuser")
TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD", "testpassword")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ROOT_USER = os.environ.get("MINIO_ROOT_USER", "minio-user")
MINIO_ROOT_PASSWORD = os.environ.get("MINIO_ROOT_PASSWORD", "minio-password")
MINIO_AUDIO_BUCKET = os.environ.get("MINIO_AUDIO_BUCKET", "audio")
CLAIF_TRANSCRIBER_ENDPOINT = os.environ.get("CLAIF_TRANSCRIBER_ENDPOINT", "http://localhost:8003")
CLAIF_DB_USER = os.environ.get("DB_USER", "claif_db_user")
CLAIF_DB_PASSWORD = os.environ.get("DB_PASSWORD", "claif_db_password")
CLAIF_DB_DATABASE = os.environ.get("DB_NAME", "claif_db")
