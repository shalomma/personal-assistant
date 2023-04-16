import io
import os
import openai
import pyaudio
import wave
import threading
import queue
import requests
from reader import Reader
from pydub import AudioSegment
from pydub.playback import play


# Record audio
def record_audio(filename, stop_event, audio_queue):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording... Press return key to stop.")

    while not stop_event.is_set():
        data = stream.read(CHUNK)
        audio_queue.put(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(list(audio_queue.queue)))


# Transcribe audio
def transcribe_audio(filename):
    with open(filename, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]


def chat_response(text):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text},
        ]
    )

    return response['choices'][0]['message']['content']


def read_response(text):
    read = Reader()
    voice = "victoria"
    file_format = "wav"
    task = read.request_audio_task(file_format, text, voice)
    task_result = read.poll_until_finished(task['statusUrl'])
    # grab the result file
    if task_result['succeeded']:
        f = io.BytesIO(requests.get(task_result['result']).content)
        sound = AudioSegment(f)
        play(sound)
        filename = f'output_audio.{file_format}'
        # read.download_to_file(task_result['result'], filename)
        # print(f'downloaded to {filename}')
    else:
        raise Exception(task_result['message'])


def play_response():
    sound = AudioSegment.from_file("output_audio.wav", format="wave")
    play(sound)


# Main function
def main():
    audio_filename = "input_audio.wav"
    stop_event = threading.Event()
    audio_queue = queue.Queue()

    record_thread = threading.Thread(target=record_audio, args=(audio_filename, stop_event, audio_queue))
    record_thread.start()
    input("Press the return key to stop recording...\n")
    stop_event.set()
    record_thread.join()

    # transcription = transcribe_audio(audio_filename)
    transcription = "Who is the president of Morocco?"
    print("Transcription:\n", transcription)
    response = chat_response(transcription)
    print("Response:\n", response)
    read_response(response)
    play_response()


if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    main()
