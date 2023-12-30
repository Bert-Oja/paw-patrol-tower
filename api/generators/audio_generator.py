from openai_integration import TTS
import subprocess
import os


def create_directory_if_not_yet_exists():
    path = "data/audio"
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def create_mp3_audio_file(path, text):
    client = TTS()
    if client.create_mission_audio(path, text):
        return path
    else:
        raise Exception("Failed to create MP3 audio file")


def convert_mp3_to_wav(path):
    if not path.lower().endswith(".mp3"):
        raise ValueError("The provided file does not have an .mp3 extension.")

    # Replace .mp3 with .wav for the output file
    output_file = os.path.splitext(path)[0] + ".wav"

    try:
        command = [
            "ffmpeg",
            "-i",
            path,  # Input file
            "-acodec",
            "pcm_s16le",  # Convert to PCM 16-bit little-endian
            "-ar",
            "44100",  # Set the sample rate to 44100 Hz
            "-ac",
            "2",  # Set number of audio channels to 2
            output_file,  # Output file
        ]
        subprocess.run(command, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error during conversion: {e}")


def create_audio_file(file_name: str, script: str) -> bool:
    try:
        path = create_directory_if_not_yet_exists()
        mp3_path = f"{path}/{file_name}.mp3"
        create_mp3_audio_file(mp3_path, script)
        wav_path = convert_mp3_to_wav(mp3_path)

        # Delete the original MP3 file after successful conversion
        if wav_path:
            os.remove(mp3_path)
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
