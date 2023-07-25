import os
from abc import ABC, abstractmethod
import azure.cognitiveservices.speech as speechsdk


class TTS(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, text):
        pass


class TTSAzure(TTS):
    def __init__(self):
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv('AZURE_SPEECH_KEY'), region=os.getenv('AZURE_SPEECH_REGION'))
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        connection = speechsdk.Connection.from_speech_synthesizer(self.speech_synthesizer)
        connection.open(True)

    def __call__(self, text):
        self.speech_synthesizer.speak_text_async(text).get()
