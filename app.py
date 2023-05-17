import gradio as gr

import asyncio, httpx
import async_timeout

from loguru import logger
from typing import Optional, List
from pydantic import BaseModel

import os
from dotenv import load_dotenv

from io import BytesIO
import base64

from elevenlabs import generate, set_api_key

set_api_key("42eadb3c99b3b386f886c1cab39d4839")

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
with open('system.txt', 'r') as f:
    system = f.read()


class Message(BaseModel):
    role: str
    content: str


async def make_completion(messages, nb_retries: int = 5, delay: int = 30) -> Optional[str]:
    """
    Sends a request to the ChatGPT API to retrieve a response based on a list of previous messages.
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        async with async_timeout.timeout(delay=delay):
            async with httpx.AsyncClient(headers=header) as aio_client:
                counter = 0
                keep_loop = True
                while keep_loop:
                    logger.debug(f"Chat/Completions Nb Retries : {counter}")
                    try:
                        resp = await aio_client.post(
                            url="https://api.openai.com/v1/chat/completions",
                            json={
                                "model": "gpt-3.5-turbo",
                                "messages": [{"role": "system", "content": system}] + messages
                            }
                        )
                        logger.debug(f"Status Code : {resp.status_code}")
                        if resp.status_code == 200:
                            return resp.json()["choices"][0]["message"]["content"]
                        else:
                            logger.warning(resp.content)
                            keep_loop = False
                    except Exception as e:
                        logger.error(e)
                        counter = counter + 1
                        keep_loop = counter < nb_retries
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout {delay} seconds !")
    return None


def audio_to_html(audio_bytes):
    audio_io = BytesIO(audio_bytes)
    audio_io.seek(0)
    audio_base64 = base64.b64encode(audio_io.read()).decode("utf-8")
    audio_html = f'<audio src="data:audio/mpeg;base64,{audio_base64}" controls autoplay></audio>'
    return audio_html


def text_to_speech_elevenlabs(response):
    audio_stream = generate(
        text=response,
        voice="Bella",
        model="eleven_monolingual_v1"
    )
    audio_html = audio_to_html(audio_stream)
    return audio_html


async def predict(input, history):
    """
    Predict the response of the chatbot and complete a running list of chat history.
    """
    history.append({"role": "user", "content": input})
    response = await make_completion(history)
    history.append({"role": "assistant", "content": response})
    messages = [(history[i]["content"], history[i + 1]["content"]) for i in range(0, len(history) - 1, 2)]
    audio_html = text_to_speech_elevenlabs(response)
    return messages, history, audio_html


"""
Gradio Blocks low-level API that allows to create custom web applications (here our chat app)
"""
with gr.Blocks() as demo:
    logger.info("Starting Demo...")
    chatbot = gr.Chatbot(label="Wisi")
    state = gr.State([])
    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(container=False)
        output_html = gr.HTML(label="Chat's Voice", value='')
        output_html.visible = False

    txt.submit(predict, [txt, state], [chatbot, state, output_html])

demo.launch(debug=True)
