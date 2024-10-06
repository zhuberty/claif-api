from sqlalchemy import inspect
from models.terminal_recordings import TerminalRecordingAnnotation, TerminalRecording
from models.audio_recordings import AudioTranscription, AudioTranscriptionAnnotation, AudioFile
from models.annotation_reviews import TerminalAnnotationReview, AudioAnnotationReview
from models.deletion_requests import DeletionRequest
from models.users import User


def print_model_schema(model):
    """ Print the schema of a SQLAlchemy model in markdown format with sorted column names. """

    mapper = inspect(model)
    print(f"### {mapper.class_.__name__}")
    print("```")
    
    sorted_columns = sorted(mapper.columns, key=lambda col: col.name)
    
    for column in sorted_columns:
        print(f"{str(column.name).ljust(36)}{column.type}")
    
    if mapper.relationships:
        print("Relationships:")
        for relationship in mapper.relationships:
            print(f"- {relationship.key} (related to {relationship.mapper.class_.__name__})")
    print("```\n")

models = [
    TerminalRecording,
    TerminalRecordingAnnotation,
    AudioTranscription,
    AudioTranscriptionAnnotation,
    TerminalAnnotationReview,
    AudioAnnotationReview,
    AudioFile,
    DeletionRequest,
    User
]

for model in models:
    print_model_schema(model)
