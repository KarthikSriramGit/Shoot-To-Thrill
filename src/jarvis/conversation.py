"""
Jarvis conversation: LLM integration for natural dialogue and game commentary.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

try:
    import openai
    OPENAI_AVAILABLE = bool(config.OPENAI_API_KEY)
except Exception:
    OPENAI_AVAILABLE = False


class JarvisConversation:
    """Generate Jarvis responses from game context and user speech."""

    def __init__(self, system_prompt=None):
        self.system_prompt = system_prompt or config.JARVIS_SYSTEM_PROMPT
        self._client = None
        if OPENAI_AVAILABLE:
            try:
                self._client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            except Exception:
                self._client = None
        self._messages = []

    def set_game_context(self, health, energy, score, wave):
        """Update context string for the LLM."""
        self._game_context = (
            f"Current game state: health={health}, energy={energy}, score={score}, wave={wave}. "
        )

    def respond(self, user_text, health=None, energy=None, score=None, wave=None):
        """Get Jarvis reply to user_text. Optional game state for context."""
        if health is not None:
            self.set_game_context(health, energy or 0, score or 0, wave or 1)
        context = getattr(self, "_game_context", "")
        if not self._client:
            return self._fallback_response(user_text)
        try:
            messages = [
                {"role": "system", "content": self.system_prompt + " " + context},
                {"role": "user", "content": user_text},
            ]
            resp = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=80,
                temperature=0.7,
            )
            text = resp.choices[0].message.content.strip() if resp.choices else None
            return text or self._fallback_response(user_text)
        except Exception:
            return self._fallback_response(user_text)

    def _fallback_response(self, user_text):
        t = (user_text or "").lower()
        if "status" in t or "health" in t:
            return "All systems nominal, sir."
        if "help" in t:
            return "Open your palms to aim. Pull your hand back then release to fire. Close your fist to recharge."
        if "wave" in t:
            return "Focus on the incoming hostiles."
        return "I'm here, sir. How may I assist?"

    def commentary_wave_start(self, wave):
        """Short line for wave start."""
        if self._client:
            try:
                r = self._client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt + " Reply in one short sentence."},
                        {"role": "user", "content": f"Wave {wave} is starting. Give a brief Jarvis-style line."},
                    ],
                    max_tokens=30,
                )
                if r.choices:
                    return r.choices[0].message.content.strip()
            except Exception:
                pass
        return f"Wave {wave} incoming, sir."
