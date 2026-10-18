import streamlit as st
import html
import os
import time
from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from services.persistence.exercise_repository import get_users_exercises
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline, autoplay_audio


# ── Extra page-level CSS injected via st.markdown ──────────────────────────
_PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

/* ─── Sidebar chrome ─────────────────────────────────────────────── */
.sb-brand {
  display: flex; align-items: center; gap: 11px;
  padding: 4px 0 20px;
}
.sb-brand-icon {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #C8F135, #9BFF4E);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  box-shadow: 0 3px 14px rgba(200,241,53,.35);
  flex-shrink: 0;
}
.sb-brand-text { line-height: 1.1; }
.sb-brand-text .bname { font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:700; color:#F0F4FF; }
.sb-brand-text .btag  { font-family:'Space Grotesk',sans-serif; font-size:.65rem; color:rgba(200,241,53,.7); text-transform:uppercase; letter-spacing:.09em; }

/* ─── User pill ──────────────────────────────────────────────────── */
.sb-user {
  display:flex; align-items:center; gap:9px;
  background:rgba(200,241,53,.06);
  border:1px solid rgba(200,241,53,.14);
  border-radius:10px;
  padding:8px 12px;
  margin-bottom:16px;
}
.sb-user-dot { width:8px;height:8px;border-radius:50%;background:#C8F135;box-shadow:0 0 8px rgba(200,241,53,.6);flex-shrink:0; }
.sb-user-name { font-family:'Space Grotesk',sans-serif;font-size:.82rem;font-weight:600;color:#F0F4FF;flex:1; }
.sb-user-tag  { font-family:'Space Grotesk',sans-serif;font-size:.65rem;color:rgba(200,241,53,.6);text-transform:uppercase;letter-spacing:.06em; }

/* ─── Section label ──────────────────────────────────────────────── */
.sb-section {
  font-family:'Space Grotesk',sans-serif;
  font-size:.68rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.12em;
  color:rgba(200,241,53,.55);
  margin: 8px 0 10px;
}

/* ─── Exercise selector ──────────────────────────────────────────── */
.ex-grid {
  display:grid; grid-template-columns:1fr 1fr;
  gap:8px; margin-bottom:14px;
}
.ex-card {
  background:rgba(17,24,38,.9);
  border:1px solid rgba(200,241,53,.1);
  border-radius:10px;
  padding:10px 12px;
  cursor:pointer;
  transition:all .2s ease;
  text-align:center;
}
.ex-card:hover,.ex-card.active {
  background:rgba(200,241,53,.09);
  border-color:rgba(200,241,53,.35);
  box-shadow:0 0 16px rgba(200,241,53,.18);
}
.ex-card .ex-icon { font-size:1.4rem; display:block; margin-bottom:4px; }
.ex-card .ex-name { font-family:'Space Grotesk',sans-serif;font-size:.7rem;font-weight:600;color:rgba(240,244,255,.75);text-transform:uppercase;letter-spacing:.05em; }

/* ─── Rep / Set counter row ──────────────────────────────────────── */
.counter-row { display:flex;gap:10px;margin-bottom:12px; }
.counter-box {
  flex:1;
  background:rgba(17,24,38,.8);
  border:1px solid rgba(200,241,53,.1);
  border-radius:10px;
  padding:10px 10px 8px;
  text-align:center;
  transition:all .2s ease;
}
.counter-box:hover { border-color:rgba(200,241,53,.3);box-shadow:0 0 12px rgba(200,241,53,.15); }
.counter-label { font-family:'Space Grotesk',sans-serif;font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:rgba(200,241,53,.6);margin-bottom:4px; }
.counter-val { font-family:'Orbitron',monospace;font-size:1.5rem;font-weight:700;color:#C8F135; }

/* ─── Active workout info banner ─────────────────────────────────── */
.workout-banner {
  background:linear-gradient(135deg,rgba(200,241,53,.1),rgba(200,241,53,.04));
  border:1px solid rgba(200,241,53,.22);
  border-radius:12px;
  padding:14px 16px;
  margin-bottom:14px;
}
.workout-banner .wb-label { font-family:'Space Grotesk',sans-serif;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:rgba(200,241,53,.6);margin-bottom:4px; }
.workout-banner .wb-val   { font-family:'Space Grotesk',sans-serif;font-size:.95rem;font-weight:700;color:#F0F4FF; }

/* ─── Progress ring labels ───────────────────────────────────────── */
.prog-grid { display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:12px; }
.prog-cell {
  background:rgba(17,24,38,.8);
  border:1px solid rgba(200,241,53,.09);
  border-radius:10px;
  padding:10px 6px 8px;
  text-align:center;
  position:relative;
  overflow:hidden;
  transition:all .2s ease;
}
.prog-cell::after {
  content:'';position:absolute;top:0;left:0;width:100%;height:2px;
  background:linear-gradient(90deg,#C8F135,#00FFD1);
  opacity:.5;
}
.prog-cell:hover { border-color:rgba(200,241,53,.28);box-shadow:0 0 10px rgba(200,241,53,.12); }
.prog-num { font-family:'Orbitron',monospace;font-size:1.2rem;font-weight:700;color:#C8F135;line-height:1; }
.prog-lbl { font-family:'Space Grotesk',sans-serif;font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:rgba(200,241,53,.55);margin-top:4px; }

/* ─── Metric pill cards (exercise-specific) ──────────────────────── */
.metric-pill {
  display:flex; align-items:center; justify-content:space-between;
  background:rgba(17,24,38,.7);
  border:1px solid rgba(255,255,255,.05);
  border-radius:8px;
  padding:8px 12px;
  margin-bottom:6px;
  font-family:'Space Grotesk',sans-serif;
  transition:all .2s ease;
}
.metric-pill:hover {
  border-color:rgba(200,241,53,.25);
}
.metric-pill .mp-label { font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:rgba(240,244,255,.45); }
.metric-pill .mp-value { font-family:'Orbitron',monospace;font-size:.9rem;font-weight:700;color:#C8F135; }

/* ─── Main area hero (Space-optimized) ─────────────────────────────── */
.main-hero {
  padding: 2px 0 8px;
}
.main-hero .hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(200,241,53,.08);
  border: 1px solid rgba(200,241,53,.2);
  border-radius: 100px;
  padding: 3px 10px;
  font-family: 'Space Grotesk',sans-serif;
  font-size: .68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: rgba(200,241,53,.9);
  margin-bottom: 6px;
}
.main-hero .hero-tag .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #C8F135;
  box-shadow: 0 0 6px rgba(200,241,53,.8);
  animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1}50%{opacity:.35} }
.main-hero h1 {
  font-family: 'Space Grotesk',sans-serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: #F0F4FF;
  line-height: 1.15;
  letter-spacing: -.02em;
  margin: 0 0 4px;
}
.main-hero .hero-sub {
  font-family: 'Space Grotesk',sans-serif;
  font-size: .82rem;
  color: rgba(240,244,255,.45);
  margin: 0;
  line-height: 1.4;
}

/* Compact strip for live workout session */
.compact-hero-strip {
  background: rgba(17,24,38,.75);
  border: 1px solid rgba(200,241,53,.18);
  border-radius: 10px;
  padding: 6px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

/* ─── Coach feedback card (Compact) ────────────────────────────────── */
.coach-card {
  background: linear-gradient(135deg,rgba(200,241,53,.08),rgba(0,255,209,.04));
  border: 1px solid rgba(200,241,53,.2);
  border-radius: 10px;
  padding: 8px 14px;
  margin: 6px 0 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: slideCoach .35s ease both;
}
@keyframes slideCoach { from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none} }
.coach-avatar {
  width: 30px; height: 30px; flex-shrink: 0;
  background: linear-gradient(135deg,#C8F135,#00FFD1);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
}
.coach-body .coach-label {
  font-family:'Space Grotesk',sans-serif;font-size:.65rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.1em;color:rgba(200,241,53,.7);margin-bottom:4px;
}
.coach-body .coach-text {
  font-family:'Space Grotesk',sans-serif;font-size:.95rem;font-weight:500;
  color:#F0F4FF;line-height:1.5;
}

/* ─── Idle placeholder ───────────────────────────────────────────── */
.idle-card {
  border:1px dashed rgba(200,241,53,.15);
  border-radius:16px;
  padding:56px 32px;
  text-align:center;
  margin:20px 0;
  background:radial-gradient(ellipse at 50% 0%,rgba(200,241,53,.04) 0%,transparent 70%);
}
.idle-card .idle-icon { font-size:3rem;margin-bottom:16px;display:block; }
.idle-card h3 { font-family:'Space Grotesk',sans-serif;font-size:1.2rem;font-weight:700;color:rgba(240,244,255,.7);margin:0 0 8px; }
.idle-card p  { font-family:'Space Grotesk',sans-serif;font-size:.88rem;color:rgba(240,244,255,.35);margin:0;line-height:1.6; }

/* ─── Completion celebration card ────────────────────────────────── */
.complete-card {
  background:linear-gradient(135deg,rgba(200,241,53,.12),rgba(0,255,209,.06));
  border:1px solid rgba(200,241,53,.35);
  border-radius:18px;
  padding:28px 24px;
  text-align:center;
  margin-bottom:20px;
  position:relative;
  overflow:hidden;
  animation:popIn .5s cubic-bezier(.22,.68,0,1.2) both;
}
@keyframes popIn { from{opacity:0;transform:scale(.93)} to{opacity:1;transform:none} }
.complete-card::before {
  content:'';position:absolute;top:-60px;left:50%;transform:translateX(-50%);
  width:200px;height:120px;
  background:radial-gradient(ellipse,rgba(200,241,53,.3) 0%,transparent 70%);
  pointer-events:none;
}
.complete-card .cc-icon { font-size:2.8rem;display:block;margin-bottom:10px; }
.complete-card h2 { font-family:'Space Grotesk',sans-serif;font-size:1.45rem;font-weight:700;color:#F0F4FF;margin:0 0 6px;letter-spacing:-.02em; }
.complete-card p  { font-family:'Space Grotesk',sans-serif;font-size:.88rem;color:rgba(240,244,255,.55);margin:0 0 16px;line-height:1.55; }
.complete-stats { display:flex;justify-content:center;gap:20px;flex-wrap:wrap; }
.cs-item { text-align:center; }
.cs-val   { font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:700;color:#C8F135;display:block; }
.cs-lbl   { font-family:'Space Grotesk',sans-serif;font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:rgba(200,241,53,.6); }
</style>
"""


def _metric_pill(label, value):
    st.markdown(
        f'<div class="metric-pill"><span class="mp-label">{label}</span>'
        f'<span class="mp-value">{value}</span></div>',
        unsafe_allow_html=True
    )




def main():
    st.set_page_config(
        page_icon="🏋️‍♀️",
        page_title="FitNova — Next Gen Fitness",
        initial_sidebar_state="collapsed",
        layout="centered"
    )

    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    inject_local_font(os.path.join(os.getcwd(), "static", "AdobeClean.otf"), "AdobeClean")
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    init_db()

    if not render_login_wall():
        return

    # After login, expand the sidebar so workout panel is visible
    if st.session_state.get("sidebar_expanded") is not True:
        st.session_state.sidebar_expanded = True
        st.markdown("""
        <script>
        window.parent.document.querySelectorAll('[data-testid="collapsedControl"] button, button[aria-label="Open sidebar"]')
          .forEach(b => b.click());
        </script>
        """, unsafe_allow_html=True)

    initial_session_defaults()

    if "voice_pipeline" not in st.session_state:
        try:
            api_key = os.environ.get("GROQ_API_KEY", "")
            if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
            if not api_key:
                raise ValueError("GROQ_API_KEY is not configured")
            groq_client = Groq(api_key=api_key)
            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()
            st.session_state.voice_pipeline = VoicePipeline(llm_coach, tts)
            st.session_state.voice_pipeline_error = None
        except Exception:
            st.session_state.voice_pipeline = None
            st.session_state.voice_pipeline_error = (
                "AI coaching is unavailable. Check the GROQ_API_KEY setting; rep tracking can still run."
            )

    workout_started = st.session_state.get("workout_started", False)

    # ════════════════════════════════════════════════════
    #  SIDEBAR
    # ════════════════════════════════════════════════════
    with st.sidebar:

        # Brand header
        username = st.session_state.get("username", "")
        st.markdown(f"""
        <div class="sb-brand">
          <div class="sb-brand-icon">🏋️</div>
          <div class="sb-brand-text">
            <div class="bname">FitNova</div>
            <div class="btag">Next Gen Fitness</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # User pill + logout
        if username:
            col_u, col_l = st.columns([3, 1])
            with col_u:
                st.markdown(f"""
                <div class="sb-user">
                  <div class="sb-user-dot"></div>
                  <div class="sb-user-name">{username}</div>
                  <div class="sb-user-tag">Active</div>
                </div>
                """, unsafe_allow_html=True)
            with col_l:
                st.markdown("<div style='padding-top:0px'></div>", unsafe_allow_html=True)
                if st.button("↩", key="logout_btn", help="Logout and switch user"):
                    st.session_state["user_id"] = None
                    st.session_state["username"] = None
                    st.session_state["workout_started"] = False
                    st.rerun()

        # ── Workout Plan Section ─────────────────────
        st.markdown('<div class="sb-section">⚡ Workout Plan</div>', unsafe_allow_html=True)

        EXERCISE_ICONS = {
            "Squats": "🦵",
            "Push-ups": "💪",
            "Biceps Curls (Dumbbell)": "🏋️",
            "Shoulder Press": "🔝",
            "Lunges": "🚶",
        }

        if not workout_started:
            # Exercise selectbox styled
            plan_exercise = st.selectbox(
                "Choose Exercise",
                options=EXERCISE_OPTIONS,
                key="plan_exercise",
                label_visibility="collapsed"
            )

            # Sets & Reps counter display
            col_s, col_r = st.columns(2)
            with col_s:
                plan_sets = st.number_input("Sets", min_value=1, max_value=50, key="plan_sets", step=1)
            with col_r:
                plan_reps = st.number_input("Reps / Set", min_value=1, max_value=50, key="plan_reps", step=1)

            # Live preview
            icon = EXERCISE_ICONS.get(plan_exercise, "🏋️")
            st.markdown(f"""
            <div class="counter-row" style="margin-top:6px;">
              <div class="counter-box">
                <div class="counter-label">Sets</div>
                <div class="counter-val">{int(plan_sets)}</div>
              </div>
              <div class="counter-box">
                <div class="counter-label">Reps</div>
                <div class="counter-val">{int(plan_reps)}</div>
              </div>
              <div class="counter-box">
                <div class="counter-label">Total</div>
                <div class="counter-val">{int(plan_sets) * int(plan_reps)}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")
            start_btn = st.button(
                f"{icon}  Start {plan_exercise}",
                key="start_session_button",
                use_container_width=True,
                type="primary"
            )

            if start_btn:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.workout_start_ts = time.time()
                st.session_state.workout_session_id = time.time_ns()
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0
                st.session_state.workout_completed = False
                st.session_state.just_completed_workout = False
                st.session_state.completed_summary = {}
                st.session_state.last_notified_workout_complete = False
                st.session_state.voice_pipeline_error = None

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_started",
                        exercise=plan_exercise,
                        metrics={},
                        event_id=f"{st.session_state.workout_session_id}:started",
                        context_info={"target_sets": int(plan_sets), "reps_per_set": int(plan_reps)},
                    )
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_complete = False
                st.rerun()

        else:
            exercise = st.session_state.get("exercise_type", "")
            sets = st.session_state.get("target_sets", 0)
            reps = st.session_state.get("reps_per_set", 0)
            icon = EXERCISE_ICONS.get(exercise, "🏋️")

            st.markdown(f"""
            <div class="workout-banner">
              <div class="wb-label">Currently Active</div>
              <div class="wb-val">{icon} {exercise}</div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:.75rem;color:rgba(240,244,255,.4);margin-top:4px;">{sets} Sets · {reps} Reps each</div>
            </div>
            """, unsafe_allow_html=True)

            end_btn = st.button("⏹  End Workout", key="end_session_button", use_container_width=True)

            if end_btn:
                st.session_state.workout_started = False
                curr_reps = st.session_state.get("reps", 0)
                reps_set  = st.session_state.get("reps_per_set", 1)
                last_saved = st.session_state.get("last_saved_sets_completed", 0)
                if reps_set > 0:
                    sets_done = curr_reps // reps_set
                    if sets_done > last_saved:
                        newly = sets_done - last_saved
                        user_id = st.session_state.get("user_id", 0)
                        now_ts = time.time()
                        time_taken = now_ts - st.session_state.get("set_cycle_started_at", now_ts)
                        from services.persistence.exercise_repository import add_exercise
                        add_exercise(user_id, exercise, newly * reps_set, newly, time_taken)

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics={},
                        event_id=f"{st.session_state.get('workout_session_id')}:ended",
                        context_info={
                            "sets": st.session_state.get("sets_completed", 0),
                            "reps": curr_reps,
                        },
                    )
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result
                st.rerun()

        # ── Live Progress & Metrics in Sidebar (Purana Tarika) ──────
        if workout_started:
            st.markdown('<div class="sb-section" style="margin-top:14px;">📊 Live Progress</div>', unsafe_allow_html=True)

            exercise    = st.session_state.get("exercise_type", "")
            total_reps  = st.session_state.get("reps", 0)
            cur_set_reps = st.session_state.get("current_set_reps", 0)
            reps_per_set = st.session_state.get("reps_per_set", 1)
            sets_completed = st.session_state.get("sets_completed", 0)
            target_sets = st.session_state.get("target_sets", 0)

            st.markdown(f"""
            <div class="prog-grid">
              <div class="prog-cell">
                <div class="prog-num">{total_reps}</div>
                <div class="prog-lbl">Total Reps</div>
              </div>
              <div class="prog-cell">
                <div class="prog-num">{cur_set_reps}<span style="font-size:.6em;color:rgba(200,241,53,.4)">/{reps_per_set}</span></div>
                <div class="prog-lbl">Set Reps</div>
              </div>
              <div class="prog-cell">
                <div class="prog-num">{sets_completed}<span style="font-size:.6em;color:rgba(200,241,53,.4)">/{target_sets}</span></div>
                <div class="prog-lbl">Sets Done</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Exercise-specific metrics
            st.markdown('<div class="sb-section" style="margin-top:10px;">🎯 Pose Metrics</div>', unsafe_allow_html=True)

            if exercise == "Squats":
                _metric_pill("Knee Angle", f"{st.session_state.knee_angle}°")
                _metric_pill("Back Angle", f"{st.session_state.back_angle}°")
                _metric_pill("Depth", st.session_state.depth_status)
            elif exercise == "Push-ups":
                _metric_pill("Elbow Angle", f"{st.session_state.elbow_angle}°")
                _metric_pill("Body Alignment", st.session_state.body_alignment)
                _metric_pill("Hip Position", st.session_state.hip_status)
            elif exercise == "Biceps Curls (Dumbbell)":
                _metric_pill("Elbow Angle", f"{st.session_state.elbow_angle}°")
                _metric_pill("Shoulder Stability", st.session_state.shoulder_status)
                _metric_pill("Swing", st.session_state.swing_status)
            elif exercise == "Shoulder Press":
                _metric_pill("Elbow Angle", f"{st.session_state.elbow_angle}°")
                _metric_pill("Arm Extension", st.session_state.extension_status)
                _metric_pill("Back Arch", st.session_state.back_arch_status)
            elif exercise == "Lunges":
                _metric_pill("Knee Angle", f"{st.session_state.front_knee_angle}°")
                _metric_pill("Torso Angle", f"{st.session_state.torso_angle}°")
                _metric_pill("Balance", st.session_state.balance_status)

        # ── Sidebar Navigation ───────────────────────
        st.markdown('<div class="sb-section" style="margin-top:16px;">🧭 Navigation</div>', unsafe_allow_html=True)
        st.page_link("pages/2_Workout_History.py", label="📜  Workout History & Analytics", help="View your personal workout logs and progress")
        st.page_link("pages/1_Admin_Dashboard.py", label="🛡️  Admin Dashboard", help="Platform analytics")

    # ════════════════════════════════════════════════════
    #  MAIN CONTENT
    # ════════════════════════════════════════════════════

    # Hero header
    st.markdown(f"""
    <div class="main-hero">
      <div class="hero-tag"><div class="dot"></div> AI-Powered · Real-Time</div>
      <h1>{"Train Harder,<br>Move Smarter." if not workout_started else "Workout in Progress."}</h1>
      <p class="hero-sub">{"Real-time pose detection + proactive AI voice coaching, powered by MediaPipe &amp; Groq LLM." if not workout_started else f"Camera is active · AI Coach is watching your form · Stay focused 💪"}</p>
    </div>
    """, unsafe_allow_html=True)

    # Stable placeholders to prevent component tree displacement
    audio_slot = st.empty()
    if st.session_state.get("audio_to_play"):
        with audio_slot:
            autoplay_audio(st.session_state.audio_to_play)
        st.session_state.audio_to_play = None

    coach_slot = st.empty()
    if st.session_state.get("voice_pipeline_error"):
        st.caption(st.session_state.voice_pipeline_error)
    if st.session_state.get("coach_feedback"):
        safe_coach_feedback = html.escape(str(st.session_state.coach_feedback))
        coach_slot.markdown(f"""
        <div class="coach-card">
          <div class="coach-avatar">🤖</div>
          <div class="coach-body">
            <div class="coach-label">FitNova AI Coach</div>
            <div class="coach-text">{safe_coach_feedback}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── IDLE / COMPLETED / ACTIVE states ────────────
    if not workout_started:
        # Completion celebration
        if st.session_state.get("just_completed_workout"):
            st.balloons()
            summary = st.session_state.get("completed_summary", {})
            st.markdown(f"""
            <div class="complete-card">
              <span class="cc-icon">🏆</span>
              <h2>Target Achieved!</h2>
              <p>Outstanding work, <strong>{username}</strong>! All sets completed — your session has been saved.</p>
              <div class="complete-stats">
                <div class="cs-item">
                  <span class="cs-val">{summary.get('sets', 0)}</span>
                  <span class="cs-lbl">Sets</span>
                </div>
                <div class="cs-item">
                  <span class="cs-val">{summary.get('reps', 0)}</span>
                  <span class="cs-lbl">Total Reps</span>
                </div>
                <div class="cs-item">
                  <span class="cs-val">{summary.get('time', 0)}s</span>
                  <span class="cs-lbl">Duration</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Idle call-to-action
        st.markdown("""
        <div class="idle-card">
          <span class="idle-icon">🎯</span>
          <h3>Set Your Workout Plan</h3>
          <p>Pick an exercise, set your reps &amp; sets in the sidebar,<br>then hit <strong>Start</strong> to activate the camera and AI coach.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        # WebRTC camera stream
        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 640, "max": 640},
                    "height": {"ideal": 480, "max": 480},
                    "frameRate": {"ideal": 15, "max": 15},
                },
                "audio": False,
            },
            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

        inject_webrtc_styles()

    # ── Page Footer ──────────────────────────────────
    st.markdown("""
    <div class="fn-footer">
      <p>Made with ❤️ by <strong>Sagar Jain</strong></p>
      <p class="fn-footer-email">✉️ <a href="mailto:jainsagar22105@gmail.com">jainsagar22105@gmail.com</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
