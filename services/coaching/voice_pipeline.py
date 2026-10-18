import base64
import logging
import time

import streamlit as st


logger = logging.getLogger(__name__)


class VoicePipeline:
    FORM_WARNING_VALUES = {
        "TOO HIGH",
        "POOR FORM",
        "SLIGHT BEND",
        "SAGGING",
        "PIKED UP",
        "SWINGING",
        "ELBOW DRIFTING",
        "SLIGHT ARCH",
        "EXCESSIVE ARCH",
        "OFF BALANCE",
    }
    NEUTRAL_VALUES = {"", "N/A", "NA", "NONE", "NEUTRAL", "GOOD DEPTH", "STANDING",
                      "STRAIGHT", "LEVEL", "BALANCED", "NO SWING", "STABLE",
                      "FULL EXTENSION", "NEARLY EXTENDED", "PRESSING", "START POSITION"}

    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0.0
        self.last_attempt_at = 0.0
        self.last_issue = None
        self.last_encouraged_at = 0.0
        self.last_error = None
        self._completed_event_ids = set()
        self.ISSUE_COOLDOWN = 8
        self.ENCOURAGEMENT_COOLDOWN = 10

    @classmethod
    def _find_form_issue(cls, exercise, metrics):
        """Return raw detector signals for Groq; never turn them into canned advice."""
        metrics = metrics or {}
        signals = {}
        for key, value in (metrics or {}).items():
            if key in {"reps", "pose_detected", "issue"} or value is None:
                continue
            if isinstance(value, str):
                normalized = value.strip().upper()
                if normalized in cls.NEUTRAL_VALUES:
                    continue
                if normalized in cls.FORM_WARNING_VALUES:
                    signals[key] = value
        if exercise == "Squats":
            back_angle = metrics.get("back_angle")
            if isinstance(back_angle, (int, float)) and back_angle < 130:
                signals["back_angle"] = {"value": int(back_angle), "below_form_threshold": True}
        return signals or None

    def process_event(self, event, exercise, metrics, context_info=None, event_id=None):
        metrics = metrics or {}
        now = time.monotonic()
        is_milestone = event in {"workout_started", "set_completed", "workout_completed"}
        signals = self._find_form_issue(exercise, metrics)

        if event_id and event_id in self._completed_event_ids:
            return None

        issue_key = "pose_not_detected" if event == "no_pose_detected" else signals
        if not is_milestone:
            if now - self.last_attempt_at < self.ISSUE_COOLDOWN:
                return None
            if issue_key:
                if issue_key == self.last_issue and now - self.last_spoken_at < self.ISSUE_COOLDOWN * 2:
                    return None
            else:
                if now - self.last_encouraged_at < self.ENCOURAGEMENT_COOLDOWN:
                    return None
                if now - self.last_spoken_at < self.ENCOURAGEMENT_COOLDOWN:
                    return None
                event = "good_form_encouragement"

        self.last_attempt_at = now
        coach_context = {
            "exercise": exercise,
            "metrics": {
                key: value for key, value in metrics.items()
                if key not in {"pose_detected", "issue"}
                and value is not None
                and value != "N/A"
            },
            "detected_form_signals": signals or {},
            "additional_context": context_info or {},
        }
        if event == "no_pose_detected":
            coach_context["pose_detected"] = False

        try:
            text = self.llm.give_feedback(event, None, context_info=coach_context)
            text = " ".join((text or "").replace("\x00", "").split()).strip(" \t\n\r\"'`")
            if not text:
                raise ValueError("Groq returned an empty coaching response")
            if text[-1] not in ".!?":
                text += "."
        except Exception as exc:
            self.last_error = f"Groq coaching request failed: {exc}"
            logger.exception("FitNova Groq coaching request failed")
            if event_id:
                self._remember_event(event_id)
            return None

        voice = None
        try:
            voice = self.tts.speak(text)
        except Exception:
            logger.exception("FitNova text-to-speech generation failed")

        self.last_error = None if voice else "Text-to-speech did not return audio"
        self.last_issue = issue_key
        self.last_spoken_at = time.monotonic()
        if event == "good_form_encouragement":
            self.last_encouraged_at = self.last_spoken_at
        if event_id:
            self._remember_event(event_id)

        return voice, text

    def _remember_event(self, event_id):
        self._completed_event_ids.add(event_id)
        if len(self._completed_event_ids) > 100:
            self._completed_event_ids.pop()


def autoplay_audio(audio_bytes):
    """Queue speech in the app page so camera reruns cannot destroy its player."""
    if not audio_bytes:
        return

    b64 = base64.b64encode(audio_bytes).decode("ascii")
    st.html(
        f"""
        <script>
        (() => {{
          const queue = window.__fitnovaAudioQueue || (window.__fitnovaAudioQueue = []);
          const playNext = window.__fitnovaPlayNext || (window.__fitnovaPlayNext = () => {{
            if (window.__fitnovaAudioCurrent || queue.length === 0) return;
            const audio = new Audio(queue.shift());
            window.__fitnovaAudioCurrent = audio;
            const finish = () => {{
              if (window.__fitnovaAudioCurrent === audio) window.__fitnovaAudioCurrent = null;
              window.__fitnovaPlayNext();
            }};
            audio.addEventListener("ended", finish, {{once: true}});
            audio.addEventListener("error", finish, {{once: true}});
            audio.play().catch((error) => {{
              console.warn("FitNova voice playback was blocked by the browser:", error);
              finish();
            }});
          }});
          queue.push("data:audio/mpeg;base64,{b64}");
          playNext();
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
