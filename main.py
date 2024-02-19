from typing import AsyncGenerator, NoReturn
import os
import uvicorn
import openai
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set the OpenAI API key using the client object
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# No need to set openai.api_key separately

with open("index.html") as f:
    html = f.read()

async def get_ai_response(message: str) -> AsyncGenerator[str, None]:
    """
    OpenAI Response
    """
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Provide the top attractions of the following city:"
                    "Provide 5 attractions."
                    "Provide the public transportation options in the city:"
                    "Provide 5 public transportation options."
                    "Provide 5 restaurants in the city that are well reviewed:"
                    "Show a list of events in the city:"
                    "Provide a list of important phone numbers in the city:"
                    "Give tourist tips and advice from the city:"
                    "Provide the output in a nice looking format. the headers should be bold and have a whitespace between them and the content."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        stream=True,
    )

    all_content = ""
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            all_content += content
            yield all_content

@app.get("/")
async def web_app() -> HTMLResponse:
    """
    Web App
    """
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> NoReturn:
    """
    Websocket for AI responses
    """
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        async for text in get_ai_response(message):
            await websocket.send_text(text)


