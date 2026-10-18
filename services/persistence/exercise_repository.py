import sqlite3
import streamlit as st
import os
from pathlib import Path

_DB_PATH = os.environ.get(
    "FITNOVA_DB_PATH",
    str(Path(__file__).parent.parent.parent / "data.db"),
)


@st.cache_resource
def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_connection()

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL REFERENCES users(id),
                exercise_name TEXT    NOT NULL,
                reps          INTEGER NOT NULL DEFAULT 0,
                sets          INTEGER NOT NULL DEFAULT 0,
                time          INTEGER NOT NULL DEFAULT 0,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_user(username: str) -> sqlite3.Row:
    conn = _get_connection()

    return conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def create_user(username: str) -> sqlite3.Row:
    conn = _get_connection()
    
    with conn:
        conn.execute(
            "INSERT INTO users (username) VALUES (?)", (username,)
        )

    return get_user(username) 


def get_or_create_user(username: str) -> sqlite3.Row:
    user = get_user(username)

    if user is None:
        user = create_user(username)
    
    return user


def add_exercise(user_id, exercise_name, reps, sets, time):
    conn = _get_connection()

    with conn:
        existing = conn.execute("""
            SELECT * FROM exercises 
            WHERE user_id = ? AND exercise_name = ? AND Date('created_at') = Date('now')
        """, (user_id, exercise_name)).fetchone()

        if existing:
            conn.execute("""
                UPDATE exercises 
                SET reps = reps + ?, sets = sets + ?, time = time + ?
                WHERE id = ?
            """, (reps, sets, time, existing['id']))
        else:
            conn.execute("""
                INSERT INTO exercises (user_id, exercise_name, sets, reps, time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, exercise_name, sets, reps, time))


def get_users_exercises(user_id):
    conn = _get_connection()

    return conn.execute("""
        SELECT * FROM exercises 
        WHERE user_id = ?
    """, (user_id,)).fetchall()


def get_all_users_summary():
    conn = _get_connection()
    return conn.execute("""
        SELECT 
            u.id,
            u.username,
            u.created_at,
            COUNT(e.id) AS total_exercise_entries,
            COALESCE(SUM(e.reps), 0) AS total_reps,
            COALESCE(SUM(e.sets), 0) AS total_sets,
            COALESCE(SUM(e.time), 0) AS total_time_sec
        FROM users u
        LEFT JOIN exercises e ON u.id = e.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()


def get_all_exercise_logs():
    conn = _get_connection()
    return conn.execute("""
        SELECT 
            e.id,
            u.username,
            e.exercise_name,
            e.reps,
            e.sets,
            e.time,
            e.created_at
        FROM exercises e
        JOIN users u ON e.user_id = u.id
        ORDER BY e.created_at DESC
    """).fetchall()


def get_overall_stats():
    conn = _get_connection()
    users_row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    users_count = users_row["count"] if users_row else 0

    stats = conn.execute("""
        SELECT 
            COUNT(*) AS total_records,
            COALESCE(SUM(reps), 0) AS total_reps,
            COALESCE(SUM(sets), 0) AS total_sets,
            COALESCE(SUM(time), 0) AS total_time
        FROM exercises
    """).fetchone()

    return {
        "total_users": users_count,
        "total_records": stats["total_records"] if stats else 0,
        "total_reps": stats["total_reps"] if stats else 0,
        "total_sets": stats["total_sets"] if stats else 0,
        "total_time": stats["total_time"] if stats else 0,
    }
