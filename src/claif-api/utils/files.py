import base64


def read_and_encode_file(file_path):
    file_content = read_file(file_path)
    return base64.b64encode(file_content.encode('utf-8')).decode('utf-8')

def read_file(file_path):
    with open(file_path, "r") as f:
        file_content = f.read()
    return file_content