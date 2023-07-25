import asyncio

from stt import STTAzure
from tts import TTSAzure
from sounds import Sounds
from wake_word import WakeWord
from conversation import Conversation
from send import Sender, TextMessages


username = 'Naomi'

Sounds.boot.play()

transcribe = STTAzure()
speech = TTSAzure()
converse = Conversation(username=username)
wake = WakeWord()
wake.reset()

send = Sender()
messages = TextMessages()


async def main():
    try:
        while True:
            print('Wizi is waiting...')
            if wake.listen():
                Sounds.start.play()
                print('Speak to Wizi!')
                while True:
                    text_user = transcribe()
                    messages.add(text_user, username)
                    if text_user == '':
                        print('break')
                        Sounds.stop.play()
                        wake.reset()
                        break
                    text_chat = converse(text_user)
                    print('>>>', text_chat)
                    speech(text_chat)
                    messages.add(text_user, 'Wizi')
    except KeyboardInterrupt:
        print('Stopping ...')
        await send.send(messages)
    finally:
        wake.stop()


if __name__ == '__main__':
    asyncio.run(main())
