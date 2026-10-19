# FitNova — Next Gen Fitness

<p align="center"><strong>Real-time workout tracking and AI-powered coaching for more confident training.</strong></p>

<p align="center">
  <a href="https://fitnova-sagarjain.streamlit.app/"><img src="https://img.shields.io/badge/Live%20App-Try%20FitNova-8EDB24?style=for-the-badge&logo=streamlit&logoColor=white" alt="Try FitNova live" /></a>
  <a href="https://fitnova-landingpage.vercel.app/"><img src="https://img.shields.io/badge/Landing%20Page-visit landing page?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Landing Page — visit landing page " /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/MediaPipe-Pose%20Landmarker-4285F4?style=flat-square&logo=google&logoColor=white" alt="MediaPipe" />
  <img src="https://img.shields.io/badge/AI-Groq-F55036?style=flat-square" alt="Groq" />
  <img src="https://img.shields.io/badge/Voice-gTTS-6A5ACD?style=flat-square" alt="gTTS" />
  <a href="https://github.com/sagarjain2205/Fitnova_next-gen-fitness"><img src="https://img.shields.io/github/stars/sagarjain2205/Fitnova_next-gen-fitness?style=flat-square&color=yellow" alt="GitHub stars" /></a>
</p>

FitNova is an AI-assisted fitness training companion built with Streamlit, MediaPipe, Groq, and gTTS. It helps people follow a workout, count reps and sets, view basic form metrics, and receive coaching cues while exercising.

## The problem

Good exercise guidance is not always available at the moment someone needs it.

- **Access and follow-up can be difficult.** Physiotherapy and rehabilitation centers may be busy, appointments can require planning or waiting, and people may not have a professional beside them during every practice session.
- **Gym guidance can be inconsistent.** Beginners may receive rushed, conflicting, or informal advice. Even with a trainer, it can be hard to observe and correct every repetition across a busy floor.
- **Home workouts often lack feedback.** A video can demonstrate an exercise, but it cannot tell a person whether their movement is being tracked correctly or help them keep count. Poorly monitored technique may lead to ineffective practice or unnecessary strain.
- **Progress is easy to lose track of.** Without clear rep, set, and session records, it can be difficult to stay consistent and see how training is going.

These challenges do not mean people should avoid professional care. They show why accessible tools can help people follow basic workouts with more structure between sessions.

## Our solution

We built **FitNova** to bring lightweight, real-time workout support into a browser. Using a webcam stream, MediaPipe estimates body pose landmarks. FitNova's exercise detectors track repetitions and workout metrics, while a Groq-powered coaching layer can provide timely feedback and gTTS can speak cues aloud. Workout summaries are saved for later review.

FitNova is designed to make routine exercise practice more guided and trackable—at home or in a gym—without requiring a dedicated sensor or a full video call with a coach.

> **Important:** FitNova is a prototype fitness companion. It does not diagnose conditions, prescribe rehabilitation, or replace a physiotherapist, physician, or qualified trainer. Pose estimates and coaching cues can be imperfect; stop if you feel pain or discomfort and seek professional advice when needed.

## What FitNova can do

- Track webcam video with Streamlit WebRTC.
- Estimate body pose with MediaPipe Pose Landmarker.
- Count repetitions and show exercise-specific form metrics.
- Set workout targets for reps and sets.
- Generate coaching feedback with Groq and optional spoken cues with gTTS.
- Save workout history and show basic user and admin analytics.

## Supported exercises

- Squats
- Push-ups
- Dumbbell biceps curls
- Shoulder press
- Lunges

## How a workout works

1. Enter a username to open or create a local profile.
2. Choose an exercise and set a target for sets and reps.
3. Allow camera access and start the workout. WebRTC sends video frames to the app.
4. MediaPipe estimates pose landmarks, and the selected exercise detector calculates metrics and repetition progress.
5. Coaching events can be sent to Groq and voiced with gTTS.
6. Workout summaries are written to SQLite and shown in the history and analytics pages.

## Project structure

```text
.
├── main.py                              # Main Streamlit app and workout flow
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
│   ├── tracking/                        # Workout metric synchronization
│   ├── ui/                              # Styles and fonts
│   └── vision/                          # Webcam frame and pose processing
├── static/                              # CSS and font assets
├── requirements.txt                     # Python dependencies
└── packages.txt                         # System packages for Streamlit Cloud
```

## Run locally

### Requirements

- Python 3.11 recommended (MediaPipe wheels vary by Python version).
- A webcam and a modern browser.
- A Groq API key for AI coaching.

### Install

```bash
git clone https://github.com/sagarjain2205/Fitnova_next-gen-fitness.git
cd Fitnova_next-gen-fitness
python -m venv .venv
```

Activate the environment in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux, run `source .venv/bin/activate`. Then install dependencies and launch the app:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run main.py
```

Open the local URL printed by Streamlit. Allow camera access when the browser asks.

## Configure Groq

For local development, create a root-level `.env` file:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

For Streamlit Community Cloud, add the key under **App settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

The app reads `GROQ_API_KEY` from the environment or Streamlit secrets. Never commit a real key.

## Deploy to Streamlit Community Cloud

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, select **Create app**.
3. Choose this repository, the `main` branch, and `main.py` as the entrypoint.
4. Add `GROQ_API_KEY` in the app's **Secrets** settings.
5. Deploy and check the app logs if dependency installation or startup fails.

This repository includes `requirements.txt` and `packages.txt`. Confirm system-package compatibility if the build reports a missing Linux package. Deployed camera access requires HTTPS. Free hosting plans may sleep and may not preserve local database files.

### Optional TURN relay for camera networks

FitNova uses Google's public STUN server by default. If a device can access its camera but cannot establish the WebRTC stream on a restrictive network, configure a TURN relay. TURN can help the connection succeed, but relayed video may have more latency than a direct connection. Create TURN credentials with a provider such as [Metered Open Relay](https://www.metered.ca/tools/openrelay/) and use the exact TURN URLs, username, and credential provided for your account.

For local development, add these keys to `.env` (use comma-separated URLs):

```dotenv
FITNOVA_TURN_URLS=turn:your-turn-host:80,turns:your-turn-host:443?transport=tcp
FITNOVA_TURN_USERNAME=your_turn_username
FITNOVA_TURN_CREDENTIAL=your_turn_credential
```

For Streamlit Community Cloud, add the provider's actual values under **App settings → Secrets**:

```toml
FITNOVA_TURN_URLS = ["turn:your-turn-host:80", "turns:your-turn-host:443?transport=tcp"]
FITNOVA_TURN_USERNAME = "your_turn_username"
FITNOVA_TURN_CREDENTIAL = "your_turn_credential"
```

Do not commit TURN credentials. If the three TURN settings are absent, FitNova continues to use STUN only.

## Security and data considerations

- **Prototype login:** the current login is username-only and does not securely verify a person's identity.
- **Admin access:** the current source includes a default fallback passcode. Replace it with a securely managed secret and proper authorization before exposing the dashboard.
- **Database durability:** SQLite writes to root-level `data.db`. Many free hosts can lose local files on restart or redeploy. Use durable managed storage for real user history.
- **Do not commit private data:** keep `data.db`, secrets, and user records out of Git. Removing a database in a later commit does not erase it from earlier Git history.
- **Privacy and camera use:** explain clearly how workout data and camera frames are processed before inviting real users.

## Roadmap

- Add secure authentication and user-specific access controls.
- Move workout history to durable managed storage.
- Improve deployment compatibility and production configuration.
- Expand exercise coverage, coaching, and progress analytics.

## License

No license file is currently included. All rights are reserved unless the project owner adds a license.

---

<p align="center"><strong>Train smart. Move well. Keep progressing.</strong></p>


---

© 2026 Sagar Jain. All rights reserved.

Created with ❤️ by Sagar Jain

Email: [jainsagar22105@gmail.com](mailto:jainsagar22105@gmail.com)
