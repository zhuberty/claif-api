import subprocess
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from minio import Minio
from minio.error import S3Error
import os
import io
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
whisper_path = os.getenv("WHISPER_PATH", "whisper")
tinydiarize_model_path = os.getenv(
    "TINYDIARIZE_MODEL_PATH",
    "/app/whisper.cpp/models/ggml-small.en-tdrz.bin"
)

# Initialize MinIO client
minio_client = Minio(
    os.getenv("MINIO_SERVER_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_SERVER_ACCESS_KEY", "minio-user"),
    secret_key=os.getenv("MINIO_SERVER_SECRET_KEY", "minio-password"),
    secure=False
)

class TranscriptionRequest(BaseModel):
    filepath: str


@app.post("/transcribe")
async def transcribe_audio(request: TranscriptionRequest):
    logger.info(f"Received transcription request for {request.filepath}")
    try:
        # Download the audio file from MinIO bucket
        audio_bucket = "audio"
        audio_path = request.filepath
        logger.info(f"Fetching audio from MinIO: bucket={audio_bucket}, path={audio_path}")
        response = minio_client.get_object(audio_bucket, audio_path)

        # Save the file locally for processing
        local_audio_path = f"/tmp/{audio_path.split('/')[-1]}"
        with open(local_audio_path, "wb") as file_data:
            for data in response.stream(32*1024):
                file_data.write(data)
        logger.info(f"Audio saved locally: {local_audio_path}")

        # Run Whisper.cpp with diarization
        whisper_cmd = [
            whisper_path, "-f", local_audio_path,
            "-m", tinydiarize_model_path,
            "--tinydiarize"
        ]
        logger.info(f"Running Whisper.cpp with command: {' '.join(whisper_cmd)}")

        try:
            result = subprocess.run(whisper_cmd, capture_output=True, text=True, check=True)
            transcription_result = result.stdout

            # Process transcription_result for speaker turns and segments
            transcription_list = []
            lines = transcription_result.strip().replace("\n", "").split("[")

            for line in lines:
                line = line.strip()  # Remove any leading or trailing whitespace/newline characters
                if line and "]" in line:  # Ensure the line has a closing timestamp bracket
                    try:
                        # Extract timestamp and text by splitting only once at the closing bracket
                        segments, text = line.split("]", 1)
                        text = text.strip()  # Clean up leading/trailing spaces from text

                        # Split the timestamps into start and end
                        if " --> " in segments:
                            start, end = segments.split(" --> ")
                        else:
                            logger.warning(f"Skipped line without valid timestamps: {line}")
                            continue

                        # Append the cleaned data to the transcription list
                        transcription_list.append({"start": start, "end": end, "text": text})

                    except ValueError as e:
                        logger.warning(f"Skipped malformed line: {line}, error: {e}")
                        continue  # Skip lines that don't match expected format

            # Convert to JSON
            transcription_result_json = json.dumps(transcription_list)  # Pretty-print for easier debugging

            logger.info(f"Transcription result processed successfully.")

            # Define the transcription bucket and key
            transcription_bucket = "transcriptions"
            transcription_key = f"{audio_path.split('/')[-1]}.json"

            # Check if the transcription bucket exists, and create it if not
            if not minio_client.bucket_exists(transcription_bucket):
                logger.info(f"Bucket '{transcription_bucket}' does not exist, creating it.")
                minio_client.make_bucket(transcription_bucket)

            # Upload the transcription result to MinIO
            transcription_bytes = io.BytesIO(transcription_result_json.encode())
            minio_client.put_object(
                transcription_bucket,
                transcription_key,
                data=transcription_bytes,
                length=len(transcription_result_json),
                content_type="application/json"
            )
            logger.info(f"Transcription uploaded to MinIO: /{transcription_bucket}/{transcription_key}")

            return {"message": "Transcription successful", "transcription_path": f"/{transcription_bucket}/{transcription_key}"}

        except subprocess.CalledProcessError as e:
            logger.error(f"Whisper.cpp subprocess error: {e.stderr}")
            raise HTTPException(status_code=500, detail=f"Whisper.cpp error: {e.stderr}")

    except S3Error as e:
        logger.error(f"S3 error: {e}")
        raise HTTPException(status_code=500, detail=f"S3 error: {e}")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
