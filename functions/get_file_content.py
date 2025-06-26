import os

# Max amount of characters allowed to be read from a file
MAX_CHARS = 10000

def get_file_content(working_directory, file_path):
    cwd = os.path.abspath(working_directory)
    target_file = cwd

    if file_path:
        target_file = os.path.abspath(os.path.join(cwd, file_path))
    if not target_file.startswith(cwd):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        with open(target_file, "+r") as f:
            file_content = f.read(MAX_CHARS)
            if len(file_content) == MAX_CHARS:
                return f'{file_content}\n[...File "{file_path}" truncated at 10000 characters]'
            else:
                return file_content
    except Exception as e:
        return f'Error: {e}'