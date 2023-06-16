import os
import pvporcupine
from pvrecorder import PvRecorder
from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import azure.cognitiveservices.speech as speechsdk


speech_config = speechsdk.SpeechConfig(
    subscription=os.getenv('AZURE_SPEECH_KEY'), region=os.getenv('AZURE_SPEECH_REGION'))
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = "en-US-SaraNeural"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

porcupine = pvporcupine.create(access_key=os.getenv('PICOVOICE_ACCESS_KEY'), keywords=["jarvis"])
recorder = PvRecorder(device_index=-1, frame_length=512)
recorder.start()

with open('system.txt', 'r') as f:
    template = f.read()

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=template,
)

llm = OpenAI(temperature=0)
conversation = ConversationChain(
    llm=llm,
    verbose=False,
    prompt=prompt,
    memory=ConversationBufferMemory()
)


def is_waked():
    pcm = recorder.read()
    result = porcupine.process(pcm)
    if result >= 0:
        recorder.stop()
        print('Detected')
        return True
    else:
        return False


def get_user_stt():
    print('<<<  ', end ="")
    text = speech_recognizer.recognize_once_async().get().text
    print(text)
    return text


def get_chat_tts():
    speech_synthesizer.speak_text_async(text_chat).get()


if __name__ == '__main__':
    try:
        print('Waiting for wake word: Jarvis')
        while True:
            if is_waked():
                while True:
                    text_user = get_user_stt()
                    if text_user == '':
                        recorder.start()
                        break
                    text_chat = conversation.predict(input=text_user)
                    print('>>>', text_chat)
                    get_chat_tts()
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        recorder.delete()
        porcupine.delete()
