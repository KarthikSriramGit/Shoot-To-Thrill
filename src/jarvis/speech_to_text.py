"""
Speech-to-text for Jarvis voice commands. Uses Whisper API or fallback.
"""

import sys
import os
import threading
import queue
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    sr = None

try:
    import openai
    OPENAI_AVAILABLE = bool(config.OPENAI_API_KEY)
except Exception:
    OPENAI_AVAILABLE = False


class SpeechToText:
    """Listen for voice and return text. Optional Whisper for accuracy."""

    def __init__(self, language="en", use_whisper=False):
        self.language = language or config.JARVIS_STT_LANGUAGE
        self.use_whisper = use_whisper and OPENAI_AVAILABLE
        self._recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self._listening = False
        self._queue = queue.Queue()

    def listen_once(self, timeout=3.0):
        """Block and return one phrase or None."""
        if not SR_AVAILABLE or self._recognizer is None:
            return None
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            if self.use_whisper and OPENAI_AVAILABLE:
                return self._whisper_transcribe(audio)
            return self._recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None
        except Exception:
            return None

    def _whisper_transcribe(self, audio):
        try:
            import io
            wav = io.BytesIO(audio.get_wav_data())
            wav.name = "audio.wav"
            client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            resp = client.audio.transcriptions.create(model="whisper-1", file=wav)
            return resp.text.strip() or None
        except Exception:
            return None

    def start_listening_background(self, callback):
        """Run listening in a thread and call callback(text) when phrase detected."""
        def run():
            while self._listening:
                text = self.listen_once(timeout=2)
                if text and callback:
                    callback(text)
        self._listening = True
        t = threading.Thread(target=run, daemon=True)
        t.start()
        return t

    def stop_listening(self):
        self._listening = False
