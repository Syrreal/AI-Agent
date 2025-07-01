import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions import get_file_content, get_files_info, write_file, run_python

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f'Reads the content of the specified file, constrained to the working directory. File content truncated at 10000 chars',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path of the file to read, relative to the working directory.",
            ),
        },
    ),
)

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


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python
    ]
)


def call_function(function_call, verbose=False):
    # Hard coded working dir to ensure AI agent operates within bounds
    cwd = "./calculator"

    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    functions = {
        "get_files_info": get_files_info.get_files_info,
        "get_file_content": get_file_content.get_file_content,
        "write_file": write_file.write_file,
        "run_python_file": run_python.run_python_file
        }

    try:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": functions[function_call.name](cwd, **function_call.args)}
                )
            ]
        )
    except KeyError:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"error": f"Unknown function: {function_call.name}"},
                )
            ],
        )

def generate_content(model, contents, verbose=False):
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )
    
    content_response = []
    if response.function_calls:
        for function_call in response.function_calls:
            print(f'Calling function: {function_call.name}{function_call.args}')
            result = call_function(function_call)
            if result.parts[0].function_response.response:
                if verbose:
                    print(f"-> {result.parts[0].function_response.response}")
                
                content_response.append(result.parts[0].function_response.response["result"])
            else:
                raise RuntimeError(f"Function {function_call.name} had no result")
    
    return ("/n".join(content_response), response)


def main():
    model = "gemini-2.0-flash-001"
    if len(sys.argv) < 2:
        print("error: prompt not provided")
        exit(1)
    user_prompt = sys.argv[1]

    verbose = False
    if len(sys.argv) == 3:
        if sys.argv[2] == "--verbose":
            verbose = True

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]

    # Return tuple (response text, response object)
    response = generate_content(model, messages, verbose)

    print(response[0])
    if verbose:
        print(f'User prompt: {user_prompt}')
        print(f'Prompt tokens: {response[1].usage_metadata.prompt_token_count}')
        print(f'Response tokens: {response[1].usage_metadata.candidates_token_count}')

if __name__ == "__main__":
    main()