import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=f'Writes to specified file, constrained to the working directory. If file does not exist, a new file is created. Files are cleared completely before being written',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of the file write to or create, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file"
            )
        },
    ),
)

def write_file(working_directory, file_path, content):
    cwd = os.path.abspath(working_directory)
    target_file = cwd

    if file_path:
        target_file = os.path.abspath(os.path.join(cwd, file_path))
    if not target_file.startswith(cwd):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        # Create file if it does not exist
        open(target_file, "x").close()
    
    # Open with "w" write mode which truncates file
    with open(target_file, "w") as f:
        f.write(content)
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'