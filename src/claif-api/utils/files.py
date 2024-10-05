def read_first_line_of_file(file_path):
    return read_file(file_path).split("\n")[0]


def read_file(file_path):
    with open(file_path, "r") as f:
        file_content = f.read()
    return file_content