import time

import streamlit as st

from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise


def _store_coach_result(result, pipeline):
    if result:
        audio, text = result
        st.session_state.audio_to_play = audio
        st.session_state.coach_feedback = text
        st.session_state.voice_pipeline_error = (
            "Voice playback is unavailable; the AI coaching text is shown above."
            if not audio else None
        )
    elif pipeline and getattr(pipeline, "last_error", None):
        st.session_state.voice_pipeline_error = (
            "AI Coach could not connect to Groq. Rep tracking will continue."
        )


def sync_metrics_update(context):
    if not context or not hasattr(context, "state"):
        return

    processor = getattr(context, "video_processor", None)
    if processor is None:
        return

    exercise = st.session_state.get("exercise_type")
    if not exercise:
        return

    processor.set_exercise(exercise)

    reps_per_set = int(st.session_state.get("reps_per_set", 0) or 0)
    target_sets = int(st.session_state.get("target_sets", 0) or 0)
    total_target_reps = reps_per_set * target_sets if reps_per_set > 0 and target_sets > 0 else None

    if st.session_state.get("workout_started"):
        session_id = st.session_state.get("workout_session_id")
        if session_id is not None and hasattr(processor, "begin_workout"):
            processor.begin_workout(exercise, total_target_reps, session_id)

    if not context.state.playing:
        return

    latest_metrics = processor.get_latest_metrics()
    if not latest_metrics:
        return

    raw_reps = latest_metrics.get("reps", 0)
    reps = max(0, int(raw_reps or 0))
    if total_target_reps is not None:
        reps = min(reps, total_target_reps)

    st.session_state.reps = reps

    fields = METRICS_FIELDS.get(exercise)
    if not fields:
        return

    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(key, default)

    if total_target_reps is not None:
        sets_completed = min(reps // reps_per_set, target_sets)
        current_set_reps = 0 if reps >= total_target_reps else reps % reps_per_set
        workout_completed = reps >= total_target_reps
    else:
        sets_completed = 0
        current_set_reps = reps
        workout_completed = False

    st.session_state.sets_completed = sets_completed
    st.session_state.current_set_reps = current_set_reps
    st.session_state.workout_completed = workout_completed
    st.session_state.workout_complete = workout_completed

    last_saved_sets = int(st.session_state.get("last_saved_sets_completed", 0) or 0)
    newly_completed_sets = max(0, sets_completed - last_saved_sets)

    if newly_completed_sets:
        now_ts = time.time()
        started_at = st.session_state.get("set_cycle_started_at", now_ts)
        time_taken = max(0.0, now_ts - started_at)
        user_id = st.session_state.get("user_id", 0)

        add_exercise(
            user_id,
            exercise,
            newly_completed_sets * reps_per_set,
            newly_completed_sets,
            time_taken,
        )
        st.session_state.set_cycle_started_at = now_ts
        st.session_state.last_saved_sets_completed = sets_completed

    pipeline = st.session_state.get("voice_pipeline")

    # The final set is also the workout milestone; emit one completion cue only.
    if workout_completed and st.session_state.get("workout_started"):
        st.session_state.workout_started = False
        st.session_state.last_notified_workout_complete = True
        st.session_state.just_completed_workout = True
        start_ts = st.session_state.get("workout_start_ts", time.time())
        duration = max(0, int(time.time() - start_ts))
        summary = {
            "exercise": exercise,
            "sets": target_sets,
            "reps": total_target_reps,
            "time": duration,
        }
        st.session_state.completed_summary = summary

        if pipeline:
            result = pipeline.process_event(
                event="workout_completed",
                exercise=exercise,
                metrics=latest_metrics,
                event_id=f"{st.session_state.get('workout_session_id')}:completed",
                context_info=summary,
            )
            _store_coach_result(result, pipeline)
        return

    if newly_completed_sets and pipeline:
        result = pipeline.process_event(
            event="set_completed",
            exercise=exercise,
            metrics=latest_metrics,
            event_id=f"{st.session_state.get('workout_session_id')}:set:{sets_completed}",
            context_info={"set_number": sets_completed, "target_sets": target_sets},
        )
        _store_coach_result(result, pipeline)
        return

    if not pipeline:
        return

    if not latest_metrics.get("pose_detected", True):
        result = pipeline.process_event(
            event="no_pose_detected",
            exercise=exercise,
            metrics={"pose_detected": False},
            event_id=None,
        )
    else:
        result = pipeline.process_event(
            event="ongoing_form_check",
            exercise=exercise,
            metrics=latest_metrics,
        )

    _store_coach_result(result, pipeline)
