"""
This module contains functions for generating audio files.
"""
import os
import subprocess
import logging
import time
from api.openai_integration import create_mission_audio, TTSException


class ConversionException(Exception):
    """
    Exception raised for errors related to audio conversion.
    """


def create_directory_if_not_yet_exists():
    """
    Creates the audio directory if it does not yet exist.

    Returns:
        str: The path of the audio directory.
    """
    path = os.getenv("AUDIO_DIRECTORY_PATH", "/data/audio")
    os.makedirs(path, exist_ok=True)
    return path


def create_mp3_audio_file(path, text):
    """
    Creates an MP3 audio file from the given text.

    Args:
        path (str): The path where the MP3 audio file will be saved.
        text (str): The text to convert to audio.

    Returns:
        str: The path of the created MP3 audio file.

    Raises:
        TTSException: If failed to create the MP3 audio file.
    """
    if create_mission_audio(path, text):
        return path
    else:
        raise TTSException("Failed to create MP3 audio file")


def convert_mp3_to_wav(path):
    """
    Converts an MP3 audio file to WAV format.

    Args:
        path (str): The path of the MP3 audio file.

    Returns:
        str: The path of the converted WAV audio file.

    Raises:
        ValueError: If the provided file does not have an .mp3 extension.
        ConversionException: If an error occurs during the conversion.
    """
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
        raise ConversionException(f"Error during conversion: {e}") from e


def create_audio_file(file_name: str, script: str) -> bool:
    """
    Creates an audio file from the given script.

    Args:
        file_name (str): The name of the audio file.
        script (str): The script to convert to audio.

    Returns:
        bool: True if the audio file was successfully created, False otherwise.
    """
    max_retries = 3
    retry_delay = 20  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            path = create_directory_if_not_yet_exists()
            mp3_path = f"{path}/{file_name}.mp3"
            create_mp3_audio_file(mp3_path, script)
            wav_path = convert_mp3_to_wav(mp3_path)

            if wav_path:
                os.remove(mp3_path)
                return True
        except TTSException as e:
            logging.error(
                "Attempt %s: Error when generating audio file: %s", attempt + 1, e
            )
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
        except ConversionException as e:
            logging.error(
                "Attempt %s: Error when converting audio file: %s", attempt + 1, e
            )
        except ValueError as e:
            logging.error(
                "The provided audio file does not have an .mp3 extension: %s", e
            )
            return False

    return False
