from api_requests import api_request

def create_audio_file(base_url, audio_filepath):
    files = {
        "file": open(audio_filepath, "rb"),
    }
    response = api_request(base_url, "/recordings/audio_files/create", method="POST", files=files)
    if "message" in response:
        print(response["message"])
    else:
        print("An error occurred while creating the audio file.")