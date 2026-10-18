import os
import streamlit as st
import pandas as pd
from services.ui.style_loader import load_css, inject_local_font
from services.persistence.exercise_repository import (
    init_db,
    get_overall_stats,
    get_all_users_summary,
    get_all_exercise_logs,
)

st.set_page_config(
    page_title="FitNova — Admin",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

_ADMIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

:root {
  --g: #C8F135; --c: #00FFD1;
  --bg0: #080A0F; --bg1: #0C0F1A; --bg2: #111826; --bg3: #1A2540;
  --b1: rgba(200,241,53,.12); --b2: rgba(200,241,53,.35);
  --t1: #F0F4FF; --t2: rgba(240,244,255,.5); --t3: rgba(240,244,255,.25);
}

.stApp { background: var(--bg0) !important; }
*, *::before, *::after { box-sizing: border-box; }
body, .stApp, p, h1, h2, h3, h4, h5, h6, label, div.stMarkdown, input, textarea {
  font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Prevent icon font breaking (e.g. keyboard_double_arrow text bug) ── */
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] *,
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] *,
.material-symbols-rounded,
.material-symbols-outlined,
span[class*="material-symbols"] {
  font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
  font-style: normal !important;
  text-transform: none !important;
  letter-spacing: normal !important;
  line-height: 1 !important;
}

button[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 6px !important;
  min-width: unset !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--b1) !important;
}
[data-testid="stSidebarNav"] { display:none!important; }

/* KPI CARDS */
.kpi-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:20px 0 32px; }
.kpi-card {
  background:var(--bg2);
  border:1px solid var(--b1);
  border-radius:14px;
  padding:20px 20px 16px;
  position:relative; overflow:hidden;
  transition:all .2s ease;
}
.kpi-card::before { content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:linear-gradient(90deg,var(--g),var(--c));opacity:.7; }
.kpi-card:hover { border-color:var(--b2);box-shadow:0 0 24px rgba(200,241,53,.15);transform:translateY(-2px); }
.kpi-icon { font-size:1.4rem;margin-bottom:10px;display:block; }
.kpi-val { font-family:'Orbitron',monospace;font-size:1.7rem;font-weight:700;color:var(--g);line-height:1;margin-bottom:4px; }
.kpi-label { font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--t2); }

/* PAGE HEADER */
.admin-header { padding:8px 0 24px; }
.admin-header .badge {
  display:inline-flex;align-items:center;gap:7px;
  background:rgba(200,241,53,.08);border:1px solid rgba(200,241,53,.2);
  border-radius:100px;padding:5px 14px;
  font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:rgba(200,241,53,.9);
  margin-bottom:12px;
}
.admin-header h1 { font-size:2rem;font-weight:700;color:var(--t1);letter-spacing:-.03em;margin:0 0 6px; }
.admin-header p  { font-size:.88rem;color:var(--t2);margin:0; }

/* SECTION LABELS */
.sec-label {
  font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;
  color:rgba(200,241,53,.55);margin:0 0 10px;display:flex;align-items:center;gap:6px;
}

/* TABS */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background:var(--bg2)!important;border:1px solid var(--b1)!important;
  border-radius:12px!important;padding:4px!important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background:transparent!important;color:var(--t2)!important;
  font-weight:600!important;font-size:.82rem!important;
  text-transform:uppercase!important;letter-spacing:.05em!important;
  border-radius:8px!important;padding:.55rem 1.1rem!important;
  transition:all .2s!important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  background:linear-gradient(135deg,rgba(200,241,53,.16),rgba(200,241,53,.06))!important;
  color:var(--g)!important;
}
[data-testid="stTabs"] [data-baseweb="tab-border"] { display:none!important; }

/* SEARCH */
[data-testid="stTextInput"] input {
  background:var(--bg2)!important;border:1px solid var(--b1)!important;
  border-radius:10px!important;color:var(--t1)!important;
  font-size:.9rem!important;
}
[data-testid="stTextInput"] input:focus {
  border-color:var(--b2)!important;
  box-shadow:0 0 16px rgba(200,241,53,.18)!important;
}

/* DATAFRAME */
.stDataFrame { border:1px solid var(--b1)!important;border-radius:12px!important;overflow:hidden!important; }

/* BUTTONS */
button, .stButton button, .stDownloadButton button {
  background:rgba(200,241,53,.07)!important;border:1px solid var(--b1)!important;
  border-radius:9px!important;color:var(--g)!important;
  font-weight:600!important;font-size:.82rem!important;
  text-transform:uppercase!important;letter-spacing:.06em!important;
  transition:all .2s!important;
}
button:hover, .stButton button:hover { background:rgba(200,241,53,.15)!important;border-color:var(--b2)!important;box-shadow:0 0 14px rgba(200,241,53,.22)!important; }

/* SELECTBOX */
[data-baseweb="select"]>div { background:var(--bg2)!important;border:1px solid var(--b1)!important;border-radius:10px!important; }

/* ALERT */
[data-testid="stAlertContainer"] { border-radius:12px!important; }

/* DIVIDER */
hr { border-color:var(--b1)!important; }

/* METRICS */
[data-testid="stMetric"] {
  background:var(--bg2)!important;border:1px solid var(--b1)!important;border-radius:12px!important;
  padding:1rem 1.2rem!important;position:relative;overflow:hidden;
}
[data-testid="stMetric"]::before { content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,var(--g),var(--c));border-radius:3px 0 0 3px; }
[data-testid="stMetricValue"] { font-family:'Orbitron',monospace!important;font-size:1.5rem!important;font-weight:700!important;color:var(--g)!important; }
[data-testid="stMetricLabel"] { font-size:.7rem!important;text-transform:uppercase!important;letter-spacing:.09em!important;color:var(--t2)!important; }

/* PAGE LINK */
[data-testid="stPageLink"] a {
  background:var(--bg2)!important;border:1px solid var(--b1)!important;
  border-radius:10px!important;color:var(--t2)!important;
  font-size:.82rem!important;font-weight:600!important;
  padding:.5rem .9rem!important;display:inline-flex!important;align-items:center!important;gap:.4rem!important;
  text-decoration:none!important;transition:all .2s!important;
}
[data-testid="stPageLink"] a:hover { border-color:var(--b2)!important;color:var(--g)!important;box-shadow:0 0 12px rgba(200,241,53,.2)!important; }

/* CHART COLORS */
.stVegaLiteChart, .stPlotlyChart { border-radius:12px!important;overflow:hidden!important; }

/* LOCK BUTTON */
.lock-btn { margin-top:8px; }

/* SCROLLBAR */
::-webkit-scrollbar { width:4px;height:4px; }
::-webkit-scrollbar-track { background:var(--bg1); }
::-webkit-scrollbar-thumb { background:var(--b1);border-radius:4px; }
</style>
"""

# Inject CSS
css_path  = os.path.join(os.getcwd(), "static", "style.css")
font_path = os.path.join(os.getcwd(), "static", "AdobeClean.otf")
if os.path.exists(css_path):
    load_css(css_path)
if os.path.exists(font_path):
    inject_local_font(font_path, "AdobeClean")
st.markdown(_ADMIN_CSS, unsafe_allow_html=True)

init_db()

# ── Admin auth ─────────────────────────────────────────────────────────────
ADMIN_PASSWORD = os.environ.get("FITNOVA_ADMIN_KEY", "admin123")

if "is_admin_authenticated" not in st.session_state:
    st.session_state.is_admin_authenticated = False

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:6px 0 20px;">
      <div style="width:36px;height:36px;background:linear-gradient(135deg,#C8F135,#9BFF4E);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 3px 12px rgba(200,241,53,.35);">🛡️</div>
      <div>
        <div style="font-weight:700;font-size:1rem;color:#F0F4FF;">Admin Panel</div>
        <div style="font-size:.65rem;color:rgba(200,241,53,.7);text-transform:uppercase;letter-spacing:.09em;">FitNova Platform</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.page_link("main.py", label="🏋️  Back to Workout App")
    st.page_link("pages/2_Workout_History.py", label="📜  Workout History & Stats")
    st.markdown("<hr style='border-color:rgba(200,241,53,.08);margin:8px 0 12px'>", unsafe_allow_html=True)

    if st.session_state.is_admin_authenticated:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;background:rgba(200,241,53,.06);border:1px solid rgba(200,241,53,.15);border-radius:10px;padding:9px 12px;margin-bottom:12px;">
          <div style="width:7px;height:7px;border-radius:50%;background:#C8F135;box-shadow:0 0 8px rgba(200,241,53,.7);"></div>
          <span style="font-size:.82rem;font-weight:600;color:#F0F4FF;">Admin Authenticated</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔒  Lock / Logout Admin", key="admin_logout", use_container_width=True):
            st.session_state.is_admin_authenticated = False
            st.rerun()

# ── Auth gate ──────────────────────────────────────────────────────────────
if not st.session_state.is_admin_authenticated:
    _, center, _ = st.columns([1, 1.8, 1])
    with center:
        st.markdown("""
        <div style="text-align:center;padding:20px 0 28px;">
          <div style="font-size:3rem;margin-bottom:12px;">🛡️</div>
          <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.55rem;font-weight:700;color:#F0F4FF;margin:0 0 8px;letter-spacing:-.02em;">Admin Access Required</h2>
          <p style="font-family:'Space Grotesk',sans-serif;font-size:.88rem;color:rgba(240,244,255,.45);margin:0;">Enter your administrator passcode to view platform analytics and user database.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("admin_auth_form"):
            entered_key = st.text_input(
                "Admin Passcode",
                type="password",
                placeholder="Default: admin123"
            )
            submit = st.form_submit_button("⚡  Access Dashboard", use_container_width=True)

        if submit:
            if entered_key == ADMIN_PASSWORD:
                st.session_state.is_admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect passcode. Please try again.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD CONTENT
# ══════════════════════════════════════════════════════════════════════════════

stats = get_overall_stats()
total_time_min = round((stats["total_time"] or 0) / 60, 1)

# Page Header
st.markdown("""
<div class="admin-header">
  <div class="badge">⚡ Platform Control Center</div>
  <h1>FitNova Admin Dashboard</h1>
  <p>Real-time user analytics, workout logs, and platform health metrics.</p>
</div>
""", unsafe_allow_html=True)

# KPI Cards (HTML grid)
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <span class="kpi-icon">👥</span>
    <div class="kpi-val">{stats['total_users']}</div>
    <div class="kpi-label">Total Users</div>
  </div>
  <div class="kpi-card">
    <span class="kpi-icon">📋</span>
    <div class="kpi-val">{stats['total_records']}</div>
    <div class="kpi-label">Workout Entries</div>
  </div>
  <div class="kpi-card">
    <span class="kpi-icon">⚡</span>
    <div class="kpi-val">{stats['total_reps']:,}</div>
    <div class="kpi-label">Total Reps Logged</div>
  </div>
  <div class="kpi-card">
    <span class="kpi-icon">⏱️</span>
    <div class="kpi-val">{total_time_min}</div>
    <div class="kpi-label">Total Mins Trained</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_users, tab_logs, tab_charts = st.tabs(["👥  User Directory", "📋  Workout Logs", "📈  Analytics"])

# ── Tab 1: Users ───────────────────────────────────────────────────────────
with tab_users:
    st.markdown('<div class="sec-label">▶ Registered Users</div>', unsafe_allow_html=True)
    users_data = get_all_users_summary()

    if users_data:
        users_df = pd.DataFrame([dict(row) for row in users_data])
        users_df.rename(columns={
            "id": "ID", "username": "Username", "created_at": "Joined At",
            "total_exercise_entries": "Sessions", "total_reps": "Total Reps",
            "total_sets": "Total Sets", "total_time_sec": "Time (s)"
        }, inplace=True)

        search = st.text_input("🔍  Search by username", placeholder="e.g. sagar_jain", label_visibility="collapsed")
        if search:
            users_df = users_df[users_df["Username"].str.contains(search, case=False, na=False)]

        st.dataframe(users_df, use_container_width=True, hide_index=True)

        csv = users_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥  Export Users CSV", data=csv, file_name="fitnova_users.csv", mime="text/csv")
    else:
        st.info("No registered users in the database yet.")

# ── Tab 2: Workout Logs ────────────────────────────────────────────────────
with tab_logs:
    st.markdown('<div class="sec-label">▶ All Workout Records</div>', unsafe_allow_html=True)
    logs_data = get_all_exercise_logs()

    if logs_data:
        logs_df = pd.DataFrame([dict(row) for row in logs_data])
        logs_df.rename(columns={
            "id": "ID", "username": "User", "exercise_name": "Exercise",
            "reps": "Reps", "sets": "Sets", "time": "Duration (s)", "created_at": "Timestamp"
        }, inplace=True)

        col1, col2 = st.columns(2)
        with col1:
            all_ex = ["All"] + sorted(list(logs_df["Exercise"].unique()))
            sel_ex = st.selectbox("Filter Exercise", all_ex, label_visibility="collapsed")
        with col2:
            all_u  = ["All"] + sorted(list(logs_df["User"].unique()))
            sel_u  = st.selectbox("Filter User", all_u, label_visibility="collapsed")

        filtered = logs_df.copy()
        if sel_ex != "All":
            filtered = filtered[filtered["Exercise"] == sel_ex]
        if sel_u != "All":
            filtered = filtered[filtered["User"] == sel_u]

        st.dataframe(filtered, use_container_width=True, hide_index=True)

        csv_l = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("📥  Export Logs CSV", data=csv_l, file_name="fitnova_logs.csv", mime="text/csv")
    else:
        st.info("No workout records in the database yet.")

# ── Tab 3: Analytics ───────────────────────────────────────────────────────
with tab_charts:
    st.markdown('<div class="sec-label">▶ Platform Analytics</div>', unsafe_allow_html=True)
    logs_data = get_all_exercise_logs()

    if logs_data:
        df = pd.DataFrame([dict(row) for row in logs_data])
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("##### 🏋️ Most Popular Exercises")
            ex_s = df.groupby("exercise_name")["reps"].sum().reset_index().sort_values("reps", ascending=False)
            st.bar_chart(ex_s.set_index("exercise_name"), color="#C8F135")

        with col_b:
            st.markdown("##### 🏆 Top Users by Reps")
            u_r = df.groupby("username")["reps"].sum().reset_index().sort_values("reps", ascending=False).head(10)
            st.bar_chart(u_r.set_index("username"), color="#00FFD1")

        st.markdown("##### 📅 Daily Training Volume")
        df["date"] = pd.to_datetime(df["created_at"]).dt.date
        daily = df.groupby("date")["reps"].sum().reset_index()
        st.line_chart(daily.set_index("date"), color="#C8F135")
    else:
        st.info("Not enough data to show analytics yet. Encourage users to complete workouts!")

st.markdown("""
<div class="fn-footer">
  <p>Made with ❤️ by <strong>Sagar Jain</strong></p>
  <p class="fn-footer-email">✉️ <a href="mailto:jainsagar22105@gmail.com">jainsagar22105@gmail.com</a></p>
</div>
""", unsafe_allow_html=True)

