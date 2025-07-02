import os
import subprocess
from google.genai import types

schema_run_python = types.FunctionDeclaration(
    name="run_python_file",
    description=f'Runs specified file, constrained to the working directory. Can only run files that end in the ".py" extension',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of the file to run, relative to the working directory.",
            ),
        },
    ),
)

def run_python_file(working_directory, file_path):
    cwd = os.path.abspath(working_directory)
    target_file = cwd

    if file_path:
        target_file = os.path.abspath(os.path.join(cwd, file_path))
    # Check if filetype is .py first
    if not os.path.splitext(target_file)[1] == ".py":
        return f'Error: "{file_path}" is not a Python file.'
    if not target_file.startswith(cwd):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File "{file_path}" not found.'
    
    try:
        proc = subprocess.run(["python3", target_file], timeout=30, capture_output=True)
        returncode = None
        if proc.returncode:
            returncode = f"Process exited with code {proc.returncode}"
        else:
            returncode = "Process ran successfully"
        return returncode + f'\nSTDOUT: {proc.stdout if proc.stdout else "No output produced"}\nSTDERR: {proc.stderr}'
    except Exception as e:
        return f'Error: executing Python file: {e}'