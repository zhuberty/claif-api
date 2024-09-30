from models.terminal_recordings import TerminalRecordingAnnotation, TerminalRecording
from models.audio_recordings import AudioTranscription, AudioTranscriptionAnnotation, AudioFile
from models.deletion_requests import DeletionRequest
from models.users import User
from sqlalchemy import inspect


def print_model_schema(model):
    mapper = inspect(model)
    print(f"Model: {mapper.class_.__name__}")
    
    print("Columns:")
    for column in mapper.columns:
        print(f"- {column.name} ({column.type})")

    if mapper.relationships:
        print("Relationships:")
        for relationship in mapper.relationships:
            print(f"- {relationship.key} (related to {relationship.mapper.class_.__name__})")

# Example usage
models = [
    TerminalRecording,
    TerminalRecordingAnnotation,
    AudioTranscription,
    AudioTranscriptionAnnotation,
    AudioFile,
    DeletionRequest,
    User
]
for model in models:
    print_model_schema(model)
