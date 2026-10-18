# FitNova — Next Gen Fitness

<p align="center"><strong>Your AI-powered workout companion for real-time exercise tracking and coaching.</strong></p>

<p align="center">
  <a href="https://YOUR-LIVE-APP-URL"><img src="https://img.shields.io/badge/Live%20App-URL%20Coming%20Soon-8EDB24?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live App — update URL" /></a>
  <a href="https://YOUR-LANDING-PAGE-URL"><img src="https://img.shields.io/badge/Landing%20Page-URL%20Coming%20Soon-111827?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Landing Page — update URL" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/MediaPipe-Pose%20Landmarker-4285F4?style=flat-square&logo=google&logoColor=white" alt="MediaPipe" />
  <img src="https://img.shields.io/badge/AI-Groq-F55036?style=flat-square" alt="Groq" />
  <img src="https://img.shields.io/badge/Voice-gTTS-6A5ACD?style=flat-square" alt="gTTS" />
  <a href="https://github.com/sagarjain2205/Fitnova_next-gen-fitness"><img src="https://img.shields.io/github/stars/sagarjain2205/Fitnova_next-gen-fitness?style=flat-square&color=yellow" alt="GitHub stars" /></a>
</p>

FitNova uses webcam video and MediaPipe pose landmarks to track exercise repetitions, sets, and form metrics. Groq-powered coaching provides feedback, and gTTS can turn coaching cues into spoken audio. Workout history and basic analytics are stored with SQLite.

> **Status:** Prototype. Read [Security and data notes](#security-and-data-notes) before deploying for public or real-user use.

## Features

- Real-time webcam processing with Streamlit WebRTC.
- MediaPipe Pose Landmarker body-pose estimation.
- Exercise-specific repetition counting and form metrics.
- Set and rep targets for a workout session.
- Groq AI coaching with optional gTTS voice feedback.
- Workout history, user summaries, and admin analytics.

## Supported exercises

Squats · Push-ups · Dumbbell biceps curls · Shoulder press · Lunges

## How it works

1. Enter a username to open or create a local profile.
2. Select an exercise and set targets.
3. Allow camera access and start the workout. WebRTC streams frames to the app.
4. MediaPipe estimates pose landmarks; the exercise detector calculates metrics and rep progress.
5. Coaching events can be sent to Groq and voiced with gTTS.
6. Workout summaries are saved to SQLite and shown in the history and analytics pages.

## Project structure

```text
.
├── main.py                              # Main Streamlit app
├── pages/
│   ├── 1_Admin_Dashboard.py             # Admin dashboard and analytics
│   └── 2_Workout_History.py             # Workout history and progress
├── detectors/                           # Exercise-specific pose and rep logic
├── ml_models/pose_landmarker_full.task  # MediaPipe pose model
├── services/
│   ├── auth/                            # Login UI and user lookup
│   ├── coaching/                        # Groq and gTTS pipeline
│   ├── config/                          # Exercise configuration
│   ├── persistence/                     # SQLite repository
│   ├── state/                           # Streamlit session state
│   ├── tracking/                        # Workout metrics
│   ├── ui/                              # Styles and fonts
│   └── vision/                          # Webcam frame and pose processing
├── static/                              # CSS and font assets
├── requirements.txt                     # Python dependencies
└── packages.txt                         # System packages for Streamlit Cloud
```

## Run locally

Use Python 3.11 with a webcam and a modern browser. Clone the repository, create a virtual environment, install dependencies, then run Streamlit:

```bash
git clone https://github.com/sagarjain2205/Fitnova_next-gen-fitness.git
cd Fitnova_next-gen-fitness
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux use `source .venv/bin/activate`. Then install and launch:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run main.py
```

Open the local URL printed by Streamlit. Camera access requires browser permission; deployed apps should use HTTPS.

## Configuration

For local development, create a root-level `.env` file:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

For Streamlit Community Cloud, add the key under **App settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

The app reads `GROQ_API_KEY` from the environment or Streamlit secrets. Never commit a real API key.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, choose **Create app**.
3. Select this repository, branch `main`, and entrypoint `main.py`.
4. Add `GROQ_API_KEY` in **Secrets**.
5. Deploy and check the app logs if installation or startup fails.

The repository includes `requirements.txt` and `packages.txt`. If the build fails on a system package, check that its name is available in the host's Linux environment. Free hosting may sleep and may not preserve local files.

## Security and data notes

- Login is currently **username-only**; it is not secure account authentication.
- The admin dashboard has a **default fallback passcode** in the current source. Replace it and add proper authorization before making the dashboard public.
- SQLite writes to root-level `data.db`. Local database files on free hosts may be lost on restart or redeploy; use durable managed storage for real user history.
- Do not commit `data.db`. Removing it in a new commit does not remove it from earlier Git history.
- Treat workout records as private data. If real records were exposed, remove them from Git history and use proper authentication and access controls before public use.
- AI exercise suggestions are general guidance, not medical advice or a substitute for a qualified trainer.

## Roadmap

- Add secure authentication and user-specific authorization.
- Move workout history to durable managed storage.
- Improve deployment compatibility and document production configuration.
- Expand exercises, coaching, and analytics.

## License

No license file is currently present. All rights are reserved unless the project owner adds a license.

---

<p align="center"><strong>Train smart. Move well. Keep progressing.</strong></p>
