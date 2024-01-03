"""
This package contains the OpenAI integration for the chat app.
"""
from .chat_app import ChatApp
from .tts import create_mission_audio


class TTSException(Exception):
    """
    Exception raised for errors related to Text-to-Speech (TTS) operations.
    """


__all__ = ["ChatApp", "create_mission_audio", "TTSException"]
