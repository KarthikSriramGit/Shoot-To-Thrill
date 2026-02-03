"""
Text-to-speech for Jarvis. Uses Edge TTS (free) or fallback.
"""

import sys
import os
import asyncio
import threading
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX_AVAILABLE = True
except ImportError:
    PYTTSX_AVAILABLE = False


def _run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    return loop.run_until_complete(coro)


class TextToSpeech:
    """Speak text with Jarvis-style voice."""

    def __init__(self, voice=None):
        self.voice = voice or config.JARVIS_TTS_VOICE
        self._engine = None
        if PYTTSX_AVAILABLE and not EDGE_AVAILABLE:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", 160)
            except Exception:
                self._engine = None

    def speak(self, text):
        """Synchronous speak (blocks until done or async in thread)."""
        if not text or not text.strip():
            return
        if EDGE_AVAILABLE:
            self._speak_edge(text)
        elif self._engine:
            self._engine.say(text)
            self._engine.runAndWait()
        else:
            print(f"[Jarvis] {text}")

    def _speak_edge(self, text):
        async def _do():
            communicate = edge_tts.Communicate(text, self.voice)
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            await communicate.save(path)
            return path
        try:
            path = _run_async(_do())
            try:
                from pygame import mixer
                mixer.init()
                mixer.music.load(path)
                mixer.music.play()
                while mixer.music.get_busy():
                    pass
            except Exception:
                pass
            try:
                os.unlink(path)
            except Exception:
                pass
        except Exception:
            if self._engine:
                self._engine.say(text)
                self._engine.runAndWait()
            else:
                print(f"[Jarvis] {text}")

    def speak_async(self, text):
        """Non-blocking: run speak in a thread."""
        t = threading.Thread(target=self.speak, args=(text,), daemon=True)
        t.start()
