import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


_LOGIN_CSS = """
<style>
/* ── Hide Streamlit chrome ───────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }

/* ── Hide sidebar entirely on login ─────────────────── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
button[aria-label="Open sidebar"],
button[aria-label="Close sidebar"] {
  display: none !important;
}

/* ── Make main area full width ───────────────────────── */
.main .block-container {
  max-width: 100% !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
}

/* ── Full-page overlay ───────────────────────────────── */
.fn-login-page {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(ellipse 80% 60% at 50% -10%, rgba(200,241,53,.10) 0%, transparent 65%),
    radial-gradient(ellipse 40% 35% at 80% 80%, rgba(0,255,209,.07) 0%, transparent 60%),
    #080A0F;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

/* ── Hide Form Enter Instruction overlay ─────────────── */
[data-testid="InputInstructions"] {
  display: none !important;
}

/* ── Animated grid bg ────────────────────────────────── */
.fn-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(200,241,53,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(200,241,53,.04) 1px, transparent 1px);
  background-size: 44px 44px;
  animation: gridPan 20s linear infinite;
}
@keyframes gridPan { to { background-position: 44px 44px; } }

/* ── Orb animations ──────────────────────────────────── */
.fn-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  pointer-events: none;
}
.fn-orb-1 {
  width: 520px; height: 520px;
  background: rgba(200,241,53,.07);
  top: -200px; left: -150px;
  animation: float1 12s ease-in-out infinite;
}
.fn-orb-2 {
  width: 360px; height: 360px;
  background: rgba(0,255,209,.06);
  bottom: -120px; right: -80px;
  animation: float2 16s ease-in-out infinite;
}
@keyframes float1 {
  0%,100% { transform: translate(0,0) scale(1); }
  50%      { transform: translate(40px,30px) scale(1.06); }
}
@keyframes float2 {
  0%,100% { transform: translate(0,0) scale(1); }
  50%      { transform: translate(-30px,-20px) scale(1.08); }
}

/* ── Card ────────────────────────────────────────────── */
.fn-card {
  position: relative;
  width: 440px;
  padding: 44px 40px 36px;
  background: rgba(17,24,38,.72);
  backdrop-filter: blur(28px) saturate(140%);
  -webkit-backdrop-filter: blur(28px) saturate(140%);
  border: 1px solid rgba(200,241,53,.15);
  border-radius: 20px;
  box-shadow:
    0 0 0 1px rgba(255,255,255,.04) inset,
    0 40px 80px rgba(0,0,0,.55);
  animation: cardIn .55s cubic-bezier(.22,.68,0,1.2) both;
}
@keyframes cardIn {
  from { opacity:0; transform:translateY(28px) scale(.97); }
  to   { opacity:1; transform:translateY(0) scale(1); }
}

/* ── Logo badge ──────────────────────────────────────── */
.fn-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}
.fn-logo-icon {
  width: 46px; height: 46px;
  background: linear-gradient(135deg, #C8F135, #9BFF4E);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  box-shadow: 0 4px 18px rgba(200,241,53,.4);
}
.fn-logo-text { line-height: 1.1; }
.fn-logo-text .brand { font-family:'Space Grotesk',sans-serif; font-size:1.25rem; font-weight:700; color:#F0F4FF; }
.fn-logo-text .tagline { font-family:'Space Grotesk',sans-serif; font-size:.72rem; color:rgba(200,241,53,.75); text-transform:uppercase; letter-spacing:.1em; }

/* ── Heading ──────────────────────────────────────────── */
.fn-heading {
  font-family:'Space Grotesk',sans-serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: #F0F4FF;
  margin: 0 0 6px;
  letter-spacing: -.02em;
}
.fn-subheading {
  font-family:'Space Grotesk',sans-serif;
  font-size: .88rem;
  color: rgba(240,244,255,.5);
  margin: 0 0 28px;
}

/* ── Input override within card ──────────────────────── */
.fn-card [data-testid="stTextInput"] label,
.fn-card label {
  font-family:'Space Grotesk',sans-serif !important;
  font-size: .78rem !important;
  text-transform: uppercase !important;
  letter-spacing: .08em !important;
  color: rgba(200,241,53,.75) !important;
  margin-bottom: 4px !important;
}
.fn-card input {
  background: rgba(255,255,255,.04) !important;
  border: 1px solid rgba(200,241,53,.18) !important;
  border-radius: 10px !important;
  color: #F0F4FF !important;
  font-size: .95rem !important;
  padding: 12px 14px !important;
}
.fn-card input:focus {
  border-color: rgba(200,241,53,.55) !important;
  box-shadow: 0 0 0 3px rgba(200,241,53,.12) !important;
}

/* ── Admin divider ────────────────────────────────────── */
.fn-admin-divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 28px 0 16px;
  color: rgba(240,244,255,.2);
  font-family: 'Space Grotesk',sans-serif;
  font-size: .72rem;
  text-transform: uppercase;
  letter-spacing: .08em;
}
.fn-admin-divider::before,
.fn-admin-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255,255,255,.07);
}

/* ── Admin link badge ─────────────────────────────────── */
.fn-admin-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 10px;
  padding: 10px 16px;
  color: rgba(240,244,255,.45) !important;
  font-family: 'Space Grotesk',sans-serif;
  font-size: .82rem;
  font-weight: 500;
  text-decoration: none !important;
  transition: all .2s ease;
  cursor: pointer;
}
.fn-admin-link:hover {
  background: rgba(200,241,53,.07);
  border-color: rgba(200,241,53,.2);
  color: rgba(200,241,53,.85) !important;
}
.fn-admin-dot {
  width: 6px; height: 6px;
  background: rgba(200,241,53,.5);
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(200,241,53,.4);
}

/* ── Feature pills ────────────────────────────────────── */
.fn-features {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 20px 0 28px;
}
.fn-pill {
  font-family: 'Space Grotesk', sans-serif;
  font-size: .7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .07em;
  padding: 4px 10px;
  border-radius: 100px;
  border: 1px solid rgba(200,241,53,.2);
  background: rgba(200,241,53,.06);
  color: rgba(200,241,53,.8);
}
</style>
"""


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    # Inject premium login CSS
    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)

    # Render the hero card HTML (pure cosmetic chrome — inputs come from Streamlit below)
    st.markdown("""
    <div class="fn-login-page">
      <div class="fn-grid"></div>
      <div class="fn-orb fn-orb-1"></div>
      <div class="fn-orb fn-orb-2"></div>
    </div>
    """, unsafe_allow_html=True)

    # Center the real Streamlit widgets using columns
    _, center, _ = st.columns([1, 2.2, 1])
    with center:
        # Logo + headline
        st.markdown("""
        <div class="fn-logo" style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
          <div class="fn-logo-icon">🏋️</div>
          <div class="fn-logo-text">
            <div class="brand">FitNova</div>
            <div class="tagline">Next Generation Fitness</div>
          </div>
        </div>
        <h1 class="fn-heading">Welcome back,<br>let's get moving.</h1>
        <p class="fn-subheading">Enter your unique name to load your training profile and history.</p>
        <div class="fn-features">
          <span class="fn-pill">🤖 AI Coach</span>
          <span class="fn-pill">📡 Live Tracking</span>
          <span class="fn-pill">🎙️ Voice Cues</span>
          <span class="fn-pill">📊 Analytics</span>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Your Unique Name",
                placeholder="e.g. sagar_jain",
                label_visibility="visible"
            )
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("⚡  Start Training Session", use_container_width=True)

        if submit_button:
            if not username.strip():
                st.error("⚠️ Please enter a unique name to continue.")
                return False

            user = get_or_create_user(username.strip())
            st.session_state["user_id"] = user["id"]
            st.session_state["username"] = user["username"]
            st.rerun()

        # Admin access section
        st.markdown("""
        <div class="fn-admin-divider">Admin Access</div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/1_Admin_Dashboard.py",
            label="🛡️  Open Admin Dashboard",
            help="View platform analytics and user database"
        )

        st.markdown("""
        <div class="fn-footer" style="margin-top: 36px;">
          <p>Made with ❤️ by <strong>Sagar Jain</strong></p>
          <p class="fn-footer-email">✉️ <a href="mailto:jainsagar22105@gmail.com">jainsagar22105@gmail.com</a></p>
        </div>
        """, unsafe_allow_html=True)

    return False