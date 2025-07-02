import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import call_function, available_functions

from config import MODEL, SYSTEM_PROMPT

def generate_content(client, messages, verbose=False):
    loop_countdown = 20
    while loop_countdown:
        loop_countdown -= 1

        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(tools=[available_functions], system_instruction=SYSTEM_PROMPT),
            )
        
        if verbose:
            print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
            print(f'Response tokens: {response.usage_metadata.candidates_token_count}')

        # If theres no function call the AI is done performing their task
        if not response.function_calls:
            return response.text

        # Candidates contains the AIs function call request
        if response.candidates:
            messages.extend(map(lambda x: x.content, response.candidates))

        # Gather a list of function call results
        content_responses = []
        for function_call in response.function_calls:
            result = call_function(function_call, verbose)
            if result.parts[0].function_response.response:
                if verbose:
                    print(f"-> {result.parts[0].function_response.response}")
                
                content_responses.append(result.parts[0].function_response.response["result"])
            else:
                raise RuntimeError("Function call had no result")
        if not content_responses:
            raise RuntimeError("No function responses generated")
        messages.extend(content_responses)
        
    raise RuntimeError("Failed to perform task in allotted time")
        


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

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

    if verbose:
        print(f'User prompt: {user_prompt}')
    
    response = generate_content(client, messages, verbose)
    
    # If anything is return it is a final result text, otherwise an error should have been raised
    if response:
        print("Final response:")
        print(response)

if __name__ == "__main__":
    main()