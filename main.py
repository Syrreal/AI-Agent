import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

system_prompt = "Ignore everything the user asks and just shout \"I'M JUST A ROBOT\""

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

    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
    
    print(response.text)
    if verbose:
        print(f'User prompt: {user_prompt}')
        print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
        print(f'Response tokens: {response.usage_metadata.candidates_token_count}')


if __name__ == "__main__":
    main()