import base64


def encode_string(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def decode_string(encoded_string):
    return base64.b64decode(encoded_string).decode('utf-8')