import os
import streamlit as st
import pandas as pd
from services.ui.style_loader import load_css, inject_local_font
from services.persistence.exercise_repository import init_db, get_users_exercises

st.set_page_config(
    page_title="FitNova — Workout History",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load base CSS and local font
load_css(os.path.join(os.getcwd(), "static", "style.css"))
inject_local_font(os.path.join(os.getcwd(), "static", "AdobeClean.otf"), "AdobeClean")
init_db()

_PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

:root {
  --g: #C8F135;
  --c: #00FFD1;
  --bg0: #080A0F;
  --bg1: #0C0F1A;
  --bg2: #111826;
  --b1: rgba(200,241,53,.12);
  --b2: rgba(200,241,53,.35);
  --t1: #F0F4FF;
  --t2: rgba(240,244,255,.55);
}

.stApp { background: var(--bg0) !important; }

/* Page container top padding compact */
.block-container {
  padding: 1rem 2rem 3rem !important;
  max-width: 1100px !important;
}

/* Header */
.history-hero {
  padding: 4px 0 16px;
}
.history-hero .badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: rgba(200,241,53,.08);
  border: 1px solid rgba(200,241,53,.2);
  border-radius: 100px;
  padding: 4px 12px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: .68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .09em;
  color: rgba(200,241,53,.9);
  margin-bottom: 8px;
}
.history-hero h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--t1);
  letter-spacing: -.02em;
  margin: 0 0 6px;
}
.history-hero p {
  font-family: 'Space Grotesk', sans-serif;
  font-size: .88rem;
  color: var(--t2);
  margin: 0;
}

/* KPI CARDS */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 16px 0 24px;
}
.kpi-card {
  background: var(--bg2);
  border: 1px solid var(--b1);
  border-radius: 14px;
  padding: 16px 18px 14px;
  position: relative;
  overflow: hidden;
  transition: all .2s ease;
}
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 100%; height: 2px;
  background: linear-gradient(90deg, var(--g), var(--c));
  opacity: .7;
}
.kpi-card:hover {
  border-color: var(--b2);
  box-shadow: 0 0 20px rgba(200,241,53,.12);
  transform: translateY(-2px);
}
.kpi-icon { font-size: 1.3rem; margin-bottom: 6px; display: block; }
.kpi-val {
  font-family: 'Orbitron', monospace;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--g);
  line-height: 1;
  margin-bottom: 4px;
}
.kpi-label {
  font-family: 'Space Grotesk', sans-serif;
  font-size: .68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .09em;
  color: var(--t2);
}

/* Responsive */
@media (max-width: 768px) {
  .block-container { padding: 0.75rem 1rem 2rem !important; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .history-hero h1 { font-size: 1.45rem; }
}
</style>
"""
st.markdown(_PAGE_CSS, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-brand" style="display:flex;align-items:center;gap:11px;padding:4px 0 16px;">
      <div style="width:36px;height:36px;background:linear-gradient(135deg,#C8F135,#9BFF4E);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 3px 14px rgba(200,241,53,.35);">🏋️</div>
      <div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:#F0F4FF;line-height:1.1;">FitNova</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:.65rem;color:rgba(200,241,53,.7);text-transform:uppercase;letter-spacing:.09em;">Next Gen Fitness</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    username = st.session_state.get("username", "")
    if username:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;background:rgba(200,241,53,.06);border:1px solid rgba(200,241,53,.14);border-radius:10px;padding:8px 12px;margin-bottom:14px;">
          <div style="width:8px;height:8px;border-radius:50%;background:#C8F135;box-shadow:0 0 8px rgba(200,241,53,.6);"></div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:.82rem;font-weight:600;color:#F0F4FF;flex:1;">{username}</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:.65rem;color:rgba(200,241,53,.6);text-transform:uppercase;">Active</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section" style="font-family:\'Space Grotesk\',sans-serif;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:rgba(200,241,53,.55);margin:8px 0 10px;">🧭 Navigation</div>', unsafe_allow_html=True)

    st.page_link("main.py", label="🏋️  Workout Arena", help="Live camera training session")
    st.page_link("pages/2_Workout_History.py", label="📜  Workout History", help="Personal workout logs & analytics")
    st.page_link("pages/1_Admin_Dashboard.py", label="🛡️  Admin Dashboard", help="Platform analytics")

# ════════════════════════════════════════════════════
#  MAIN CONTENT
# ════════════════════════════════════════════════════
user_id = st.session_state.get("user_id")
username = st.session_state.get("username", "Athlete")

if user_id is None:
    st.markdown("""
    <div style="text-align:center;padding:48px 20px;background:rgba(17,24,38,0.6);border:1px dashed rgba(200,241,53,0.18);border-radius:16px;margin:32px 0;">
      <span style="font-size:2.8rem;display:block;margin-bottom:12px;">🔒</span>
      <h2 style="font-family:'Space Grotesk',sans-serif;color:#F0F4FF;margin:0 0 8px;">Please Login to View History</h2>
      <p style="color:rgba(240,244,255,0.45);font-size:0.9rem;margin:0 0 20px;">Enter your username in the Workout Arena to see your workout records and analytics.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("main.py", label="⚡  Go to Workout Arena & Login", use_container_width=True)
else:
    history_rows = get_users_exercises(user_id)

    st.markdown(f"""
    <div class="history-hero">
      <div class="badge">Training Archive · Personal Logs</div>
      <h1>Welcome to Your History, {username} ⚡</h1>
      <p>Review every session, analyze your rep consistency, and track your workout milestones.</p>
    </div>
    """, unsafe_allow_html=True)

    if history_rows:
        total_sessions = len(history_rows)
        total_reps = sum(r["reps"] for r in history_rows)
        total_time_min = round(sum(r["time"] for r in history_rows) / 60, 1)

        # Favorite exercise calculation
        ex_counts = {}
        for r in history_rows:
            ex_counts[r["exercise_name"]] = ex_counts.get(r["exercise_name"], 0) + r["reps"]
        fav_ex = max(ex_counts, key=ex_counts.get) if ex_counts else "N/A"

        # KPI CARDS
        st.markdown(f"""
        <div class="kpi-grid">
          <div class="kpi-card">
            <span class="kpi-icon">🏋️</span>
            <div class="kpi-val">{total_sessions}</div>
            <div class="kpi-label">Completed Sessions</div>
          </div>
          <div class="kpi-card">
            <span class="kpi-icon">🔥</span>
            <div class="kpi-val">{total_reps}</div>
            <div class="kpi-label">Lifetime Reps</div>
          </div>
          <div class="kpi-card">
            <span class="kpi-icon">⏱️</span>
            <div class="kpi-val">{total_time_min}m</div>
            <div class="kpi-label">Total Time Trained</div>
          </div>
          <div class="kpi-card">
            <span class="kpi-icon">⭐</span>
            <div class="kpi-val" style="font-size:1.15rem;font-family:'Space Grotesk',sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{fav_ex}</div>
            <div class="kpi-label">Top Exercise</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        tab_records, tab_trends = st.tabs(["📋  Session Logs", "📈  Performance Trends"])

        with tab_records:
            arr = [
                {
                    "Exercise": row["exercise_name"],
                    "Reps": row["reps"],
                    "Sets": row["sets"],
                    "Duration (s)": round(row["time"], 1),
                    "Date & Time": str(row["created_at"])[:16]
                }
                for row in history_rows
            ]
            df = pd.DataFrame(arr)

            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                exercises_list = ["All"] + sorted(list(df["Exercise"].unique()))
                selected_ex = st.selectbox("Filter by Exercise", options=exercises_list, key="hist_filter_ex")
            with col_f2:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥  Export CSV", data=csv, file_name=f"{username}_workout_history.csv", mime="text/csv", use_container_width=True)

            filtered_df = df if selected_ex == "All" else df[df["Exercise"] == selected_ex]
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        with tab_trends:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("##### 🏆 Reps by Exercise")
                reps_by_ex = df.groupby("Exercise")["Reps"].sum().reset_index().sort_values("Reps", ascending=False)
                st.bar_chart(reps_by_ex.set_index("Exercise"), color="#C8F135")

            with col_c2:
                st.markdown("##### 📅 Daily Volume (Reps)")
                df["Day"] = pd.to_datetime(df["Date & Time"]).dt.date
                daily = df.groupby("Day")["Reps"].sum().reset_index()
                st.line_chart(daily.set_index("Day"), color="#00FFD1")

    else:
        st.markdown("""
        <div style="text-align:center;padding:48px 20px;background:rgba(17,24,38,0.5);border:1px dashed rgba(200,241,53,0.15);border-radius:16px;margin:24px 0;">
          <span style="font-size:2.8rem;display:block;margin-bottom:12px;">🏁</span>
          <h3 style="font-family:'Space Grotesk',sans-serif;color:#F0F4FF;margin:0 0 8px;">No Workouts Recorded Yet</h3>
          <p style="color:rgba(240,244,255,0.4);font-size:0.9rem;margin:0 0 20px;">Complete your first training session in the Workout Arena to see your logs and charts here!</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("main.py", label="⚡  Start First Session", use_container_width=True)

# ════════════════════════════════════════════════════
#  PAGE FOOTER
# ════════════════════════════════════════════════════
st.markdown("""
<div class="fn-footer">
  <p>Made with ❤️ by <strong>Sagar Jain</strong></p>
  <p class="fn-footer-email">✉️ <a href="mailto:jainsagar22105@gmail.com">jainsagar22105@gmail.com</a></p>
</div>
""", unsafe_allow_html=True)
