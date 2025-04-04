# rename .env_bak to .env and add your openai api key
# run this file with uvicorn openai_chat_api:app --reload
# open http://localhost:8000/chat/hello in your browser

# Now let's write a test to override the dependency. Open the 07_openai_chat_api_test file to review the test and run pytest to see it in action.

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from openai.types.chat.chat_completion import ChatCompletion

from fastapi import FastAPI, Depends
from typing import Annotated

load_dotenv(find_dotenv())

_: bool = load_dotenv(find_dotenv())  # read local .env file

client: OpenAI = OpenAI()

def chat_completion(prompt : str )-> str | None:
 response : ChatCompletion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo-1106",
    )
# print(response)
#  print(response.choices[0].message.content)
 return response.choices[0].message.content

app = FastAPI()

@app.get("/chat/{prompt}")
def add_data(prompt: Annotated[str, Depends(chat_completion)]):

    return {"openai": prompt}
