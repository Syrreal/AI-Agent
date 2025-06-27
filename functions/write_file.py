import os

def write_file(working_directory, file_path, content):
    cwd = os.path.abspath(working_directory)
    target_file = cwd

    if file_path:
        target_file = os.path.abspath(os.path.join(cwd, file_path))
        print(f'Current working dir: {cwd}\n'
              f'Target file path: {target_file}')
    if not target_file.startswith(cwd):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        # Create file if it does not exist
        open(target_file, "x").close()
    
    # Open with "w" write mode which truncates file
    with open(target_file, "w") as f:
        f.write(content)
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'