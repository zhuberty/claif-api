from sqlalchemy import inspect
from models.recordings import TerminalRecording, AudioTranscription, AudioFile
from models.annotations import AudioTranscriptionAnnotation, TerminalRecordingAnnotation
from models.annotation_reviews import TerminalAnnotationReview, AudioAnnotationReview
from models.users import User


def get_model_schema_string(model):
    """ Return the schema of a SQLAlchemy model as a string in markdown format with sorted column names. """

    schema_string = ""
    mapper = inspect(model)
    schema_string += f"### {mapper.class_.__name__}\n"
    schema_string += "```\n"
    
    sorted_columns = sorted(mapper.columns, key=lambda col: col.name)
    
    for column in sorted_columns:
        schema_string += f"{str(column.name).ljust(36)}{column.type}\n"
    
    if mapper.relationships:
        schema_string += "Relationships:\n"
        for relationship in mapper.relationships:
            schema_string += f"- {relationship.key} (related to {relationship.mapper.class_.__name__})\n"
    
    schema_string += "```\n\n"
    return schema_string


def print_all_model_schemas():
    """ Prints the schema for all models when the script is called directly. """
    models = [
        TerminalRecording,
        TerminalRecordingAnnotation,
        AudioTranscription,
        AudioTranscriptionAnnotation,
        TerminalAnnotationReview,
        AudioAnnotationReview,
        AudioFile,
        User
    ]

    for model in models:
        print(get_model_schema_string(model))


if __name__ == "__main__":
    print_all_model_schemas()
