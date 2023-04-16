import requests
import zipfile
import tempfile
import os
import time


class Reader:
    def __init__(self, polling_interval=5):
        self.api_key = os.getenv('NARAKEET_API_KEY')
        self.api_url = 'https://api.narakeet.com'
        self.polling_interval = polling_interval

    def request_audio_task(self, format, text, voice):
        url = f'{self.api_url}/text-to-speech/{format}?voice={voice}'
        options = {
            'headers': {
                'Content-Type': 'text/plain',
                'x-api-key': self.api_key,
            },
            'data': text.encode('utf8')
        }
        response = requests.post(url, **options)
        response.raise_for_status()
        return response.json()

    def poll_until_finished(self, task_url, progress_callback=None):
        while True:
            response = requests.get(task_url)
            response.raise_for_status()
            data = response.json()
            if data['finished']:
                break
            if progress_callback:
                progress_callback(data)
            time.sleep(self.polling_interval)

        return data

    @staticmethod
    def download_to_file(url, file):
        with open(file, 'wb') as f:
            f.write(requests.get(url).content)
