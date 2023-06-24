import azure.cognitiveservices.speech as speechsdk


class WakeWord:
    def __init__(self):
        self.model = speechsdk.KeywordRecognitionModel("./models/0b2b7d58-99ab-48d5-908d-5e00120f8e40.table")
        self.keyword_recognizer = speechsdk.KeywordRecognizer()
        self.keyword_recognition = None

    def reset(self):
        self.keyword_recognition = self.keyword_recognizer.recognize_once_async(self.model)

    def listen(self):
        return self.keyword_recognition.get()

    def stop(self):
        self.keyword_recognizer.stop_recognition_async().get()
