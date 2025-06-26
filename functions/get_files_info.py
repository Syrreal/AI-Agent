import os
import sys

def get_files_info(working_directory, directory=None):
    cwd = os.path.abspath(working_directory)
    target_dir = cwd

    if directory:
        target_dir = os.path.abspath(os.path.join(cwd, directory))
    if not target_dir.startswith(cwd):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'
    
    dir_contents = []
    try:
        with os.scandir(os.path.join(os.path.abspath(working_directory), directory)) as dir:
            for entry in dir:
                dir_contents.append(f'- {entry.name}: file_size={entry.stat().st_size}, is_dir={entry.is_dir()}')
        return "\n".join(dir_contents)
    except Exception as e:
        return f'Error: {e}'
    