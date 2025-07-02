import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import call_function, available_functions

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
    # Perform first task out of the loop to create variable :) 
    response = generate_content(model, messages, verbose)

    loop_countdown = 19
    while loop_countdown:
        loop_countdown -= 1
        
    if response[1].text:
        print(response[1].text)
    print(response[0])
    if verbose:
        print(f'User prompt: {user_prompt}')
        print(f'Prompt tokens: {response[1].usage_metadata.prompt_token_count}')
        print(f'Response tokens: {response[1].usage_metadata.candidates_token_count}')

if __name__ == "__main__":
    main()