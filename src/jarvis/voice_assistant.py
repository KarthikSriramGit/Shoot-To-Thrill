"""
Jarvis voice assistant: ties STT, conversation, and TTS for game commentary.
"""

import sys
import os
import threading
import queue
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .conversation import JarvisConversation


class JarvisVoiceAssistant:
    """Full conversational Jarvis: listen, respond via LLM, speak."""

    def __init__(self, game_state_callback=None):
        self.game_state_callback = game_state_callback  # () -> (health, energy, score, wave)
        self.stt = SpeechToText(language=config.JARVIS_STT_LANGUAGE, use_whisper=bool(config.OPENAI_API_KEY))
        self.tts = TextToSpeech(voice=config.JARVIS_TTS_VOICE)
        self.conversation = JarvisConversation()
        self._listening = False
        self._thread = None
        self._response_queue = queue.Queue()

    def say(self, text, async_=True):
        """Have Jarvis speak (optionally non-blocking)."""
        if async_:
            self.tts.speak_async(text)
        else:
            self.tts.speak(text)

    def on_voice_input(self, text):
        """Called when user speech is recognized."""
        if not text or not text.strip():
            return
        health, energy, score, wave = 100, 100, 0, 1
        if self.game_state_callback:
            try:
                health, energy, score, wave = self.game_state_callback()
            except Exception:
                pass
        response = self.conversation.respond(text, health=health, energy=energy, score=score, wave=wave)
        if response:
            self.say(response, async_=True)

    def start_listening(self):
        """Start background voice listener."""
        if self._listening:
            return
        self._listening = True
        self._thread = self.stt.start_listening_background(self.on_voice_input)

    def stop_listening(self):
        self._listening = False
        self.stt.stop_listening()

    def wave_started(self, wave):
        """Optional: Jarvis announces new wave."""
        line = self.conversation.commentary_wave_start(wave)
        self.say(line, async_=True)
