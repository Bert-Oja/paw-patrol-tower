import openai


class TTS:
    def create_mission_audio(self, path, text):
        try:
            response = openai.audio.speech.create(
                model="tts-1", voice="nova", input=text
            )
            response.stream_to_file(path)
            return True
        except Exception as e:
            print(f"An error occured when creating the audio file: {e}")
            return False
