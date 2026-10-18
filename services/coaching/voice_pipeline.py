import time
import base64
import streamlit as st
import streamlit.components.v1 as components


class VoicePipeline:
    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0
        self.last_issue = None           # prevent exact same cue repeating
        self.last_encouraged_at = 0      # track last good-form nudge
        self.ISSUE_COOLDOWN = 8          # seconds between form corrections
        self.ENCOURAGEMENT_COOLDOWN = 10 # seconds between good-form pats

    def _find_form_issue(self, exercise, metrics):
        if "issue" in metrics:
            return metrics["issue"]

        if exercise == "Squats":
            depth = metrics.get("depth_status", "")
            back_angle = metrics.get("back_angle", 180)

            if depth == "TOO HIGH":
                return "Squat depth too shallow — drive your hips back and sink the knees deeper."

            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return "Torso is collapsing forward — chest up, proud posture, weight through your heels."

        elif exercise == "Push-ups":
            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")

            if alignment == "Poor Form":
                return "Body is misaligned — brace your core hard and keep a rigid plank from head to heel."

            if hip_status == "SAGGING":
                return "Hips are dropping — squeeze your glutes and brace your abs to hold the plank position."

            if hip_status == "PIKED UP":
                return "Hips are too high — lower your hips until your body forms a straight line."

        elif exercise == "Biceps Curls (Dumbbell)":
            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")

            if swing == "SWINGING":
                return "Torso is swinging — pin your elbows to your sides and isolate the bicep, no body English."

            if shoulder == "ELBOW DRIFTING":
                return "Elbow is drifting out — glue your upper arm to your torso and curl with control."

        elif exercise == "Shoulder Press":
            back_arch = metrics.get("back_arch_status", "")
            extension = metrics.get("extension_status", "")

            if back_arch == "Excessive Arch":
                return "Excessive lower-back arch — tighten your core, tuck your ribs, press straight up."

            if back_arch == "Slight Arch":
                return "Slight back arch — brace your core before the next press to protect your spine."

        elif exercise == "Lunges":
            balance = metrics.get("balance_status", "")

            if balance == "OFF BALANCE":
                return "Balance is off — step wider, engage your core, and keep your torso upright."

        return None

    def process_event(self, event, exercise, metrics, context_info=None):
        issue = self._find_form_issue(exercise, metrics)
        now = time.time()

        is_milestone = event in ["workout_started", "set_completed", "workout_completed"]

        if not is_milestone:
            if issue:
                # Cooldown between corrections
                if now - self.last_spoken_at < self.ISSUE_COOLDOWN:
                    return None
                # Skip if exact same issue just spoken (avoids broken-record effect)
                if issue == self.last_issue and now - self.last_spoken_at < self.ISSUE_COOLDOWN * 2:
                    return None
            else:
                # No form issue — give periodic good-form encouragement
                if now - self.last_encouraged_at < self.ENCOURAGEMENT_COOLDOWN:
                    return None
                if now - self.last_spoken_at < self.ENCOURAGEMENT_COOLDOWN:
                    return None
                # Use a special event so LLM knows to encourage, not correct
                event = "good_form_encouragement"
                self.last_encouraged_at = now

        self.last_issue = issue
        text = self.llm.give_feedback(event, issue, context_info=context_info)
        voice = self.tts.speak(text)
        self.last_spoken_at = now

        return voice, text


def autoplay_audio(audio_bytes):
    """Play audio via JavaScript Audio object — invisible, not cut off by Streamlit reruns."""
    if not audio_bytes:
        return

    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    js_code = f"""
    <script>
    (function() {{
        var snd = new Audio("data:audio/mp3;base64,{b64}");
        snd.play().catch(function(e) {{ console.warn('Audio play failed:', e); }});
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)
