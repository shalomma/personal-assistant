from sounds import Sounds
from conversation import Conversation
from tts import TTSAzure
from stt import STTAzure
from wake_word import WakeWord

Sounds.boot.play()

transcribe = STTAzure()
speech = TTSAzure()
converse = Conversation()
wake = WakeWord()
wake.reset()

if __name__ == '__main__':
    try:
        while True:
            print('Wizi is waiting...')
            if wake.listen():
                Sounds.start.play()
                print('Speak to Wizi!')
                while True:
                    text_user = transcribe()
                    if text_user == '':
                        print('break')
                        Sounds.stop.play()
                        wake.reset()
                        break
                    text_chat = converse(text_user)
                    print('>>>', text_chat)
                    speech(text_chat)
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        wake.stop()