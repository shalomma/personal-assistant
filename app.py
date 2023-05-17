import os
import base64
from io import BytesIO
from typing import Optional
import async_timeout
import gradio as gr
from dotenv import load_dotenv
from elevenlabs import generate, set_api_key
from loguru import logger
from pydantic import BaseModel
import openai

load_dotenv()

set_api_key(os.getenv("ELEVENLABS_API_KEY"))
API_KEY = os.getenv("OPENAI_API_KEY")


async def make_completion(messages, instruct, nb_retries: int = 5, delay: int = 30) -> Optional[str]:
    """
    Sends a request to the ChatGPT API to retrieve a response based on a list of previous messages.
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    async with async_timeout.timeout(delay=delay):
        counter = 0
        keep_loop = True
        while keep_loop:
            logger.debug(f"Chat/Completions Nb Retries : {counter}")
            try:
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": instruct}] + messages
                )
            except openai.error.APIError as e:
                # Handle API error here, e.g. retry or log
                print(f"OpenAI API returned an API Error: {e}")
                pass
            except openai.error.APIConnectionError as e:
                # Handle connection error here
                print(f"Failed to connect to OpenAI API: {e}")
                pass
                logger.error(e)
            else:
                return resp["choices"][0]["message"]["content"]
            finally:
                counter += 1
                keep_loop = counter < nb_retries
    return ''


def init_system_role():
    with open('system.txt', 'r') as f:
        return f.read()


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


async def predict(input, history, instruct):
    """
    Predict the response of the chatbot and complete a running list of chat history.
    """
    history.append({"role": "user", "content": input})
    response = await make_completion(history, instruct)
    history.append({"role": "assistant", "content": response})
    messages = [(history[i]["content"], history[i + 1]["content"]) for i in range(0, len(history) - 1, 2)]
    audio_html = text_to_speech_elevenlabs(response)
    return messages, history, audio_html


"""
Gradio Blocks low-level API that allows to create custom web applications (here our chat app)
"""
with gr.Blocks() as demo:
    logger.info("Starting Demo...")
    system_instruct = gr.Textbox(label='System Instructions', value=init_system_role)
    chatbot = gr.Chatbot(label="Wisi")
    state = gr.State([])
    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter")  # .style(container=False)
        output_html = gr.HTML(label="Chat's Voice", value='')
        output_html.visible = False

    txt.submit(predict, [txt, state, system_instruct], [chatbot, state, output_html])
    txt.submit(lambda x: gr.update(value=''), [txt],[txt])

demo.launch(debug=True)
