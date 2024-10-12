import io
from minio import Minio
from minio.error import S3Error
from utils.env import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_AUDIO_BUCKET

# Initialize MinIO Client
minio_client = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # Set to True if using https
)

# Ensure bucket exists
def ensure_bucket_exists(bucket_name: str = MINIO_AUDIO_BUCKET):
    """Ensures the given bucket exists in MinIO."""
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
    except S3Error as e:
        raise RuntimeError(f"Failed to ensure bucket: {str(e)}")


# Upload file to MinIO
def upload_file_to_minio(file_data: bytes, file_name: str, content_type: str, bucket_name: str = MINIO_AUDIO_BUCKET):
    """Uploads a file to MinIO."""
    try:
        # Use io.BytesIO to create a file-like object from bytes
        file_stream = io.BytesIO(file_data)
        file_size = len(file_data)
        
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=file_name,
            data=file_stream,
            length=file_size,
            content_type=content_type
        )
        return {"message": "File uploaded successfully", "file_name": file_name}
    except S3Error as e:
        raise RuntimeError(f"Error uploading file: {str(e)}")
