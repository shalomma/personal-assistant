import os
from langchain.chat_models import AzureChatOpenAI
from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import azure.cognitiveservices.speech as speechsdk


speech_config = speechsdk.SpeechConfig(
    subscription=os.getenv('AZURE_SPEECH_KEY'), region=os.getenv('AZURE_SPEECH_REGION'))
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

model = speechsdk.KeywordRecognitionModel("./models/0b2b7d58-99ab-48d5-908d-5e00120f8e40.table")
keyword_recognizer = speechsdk.KeywordRecognizer()
keyword_recognition = keyword_recognizer.recognize_once_async(model)

with open('system.txt', 'r') as f:
    template = f.read()

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=template,
)

llm = AzureChatOpenAI(
    openai_api_type="azure",
    deployment_name="chatgpt",
    openai_api_version="2023-03-15-preview",
    temperature=0.7,
)
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
conversation = ConversationChain(
    llm=llm,
    verbose=False,
    prompt=prompt,
    memory=memory
)


def get_user_stt():
    print('<<<  ', end="")
    text = speech_recognizer.recognize_once_async().get().text
    print(text)
    return text


def get_chat_tts(text):
    speech_synthesizer.speak_text_async(text).get()


if __name__ == '__main__':
    try:
        print('Wizi is waiting...')
        while True:
            if keyword_recognition.get():
                print('Speak to Wizi!')
                while True:
                    text_user = get_user_stt()
                    if text_user == '':
                        print('break')
                        break
                    text_chat = conversation.predict(input=text_user)
                    print('>>>', text_chat)
                    get_chat_tts(text_chat)
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        stop_future = keyword_recognizer.stop_recognition_async()
        stop_future.get()
