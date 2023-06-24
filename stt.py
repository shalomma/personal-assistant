import os
from abc import ABC, abstractmethod
import azure.cognitiveservices.speech as speechsdk


class STT(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self):
        pass


class STTAzure(STT):
    def __init__(self):
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv('AZURE_SPEECH_KEY'), region=os.getenv('AZURE_SPEECH_REGION'))
        speech_config.speech_recognition_language = "en-US"
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    def __call__(self):
        print('<<<  ', end="")
        text = self.speech_recognizer.recognize_once_async().get().text
        print(text)
        return text
