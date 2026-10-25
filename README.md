# MathQuest AI — Gamified Mathematics Learning Platform

## Project Overview
MathQuest AI is an interactive, AI-powered mathematics learning platform inspired by platforms like IXL and Khan Academy, built specifically for Grade 5 and Grade 6 students. The platform aligns with core Georgia Mathematics Standards and integrates real-time Gemini AI tutoring, adaptive multi-tier quizzes, interactive visual infographics, gamified achievement tracking, and speech-enabled video narration.

## Main Features
1. **Topic Selection & Learning Content**: Tailored modules for Grade 5 and Grade 6 covering fractions, decimals, ratios, and geometry.
2. **AI-Generated Explanations**: Uses Google Gemini API (`gemini-2.5-flash`) to deliver structured, age-appropriate concept guides, step-by-step breakdowns, and real-world examples.
3. **Interactive Visual Infographic**: Dynamic SVG fraction bar visualizer allowing students to interactively manipulate numerators and denominators.
4. **Adaptive Multi-Tier Practice Tests**: Multi-choice quiz arena that adjusts difficulty (**Easy** ⇄ **Medium** ⇄ **Hard**) based on rule-based consecutive answer patterns.
5. **Gamification & Achievements**: Persistent SQLite-backed XP awarding (+25 XP per correct answer), learning streaks, score calculations, and unlockable achievement badges.
6. **Video-Style Audio Narration**: Built-in Web Speech API text-to-speech player enabling narrated slide-style explanations for accessibility.
7. **AI Formula & Smart Solver**: On-demand assistant where students can query any math problem and receive step-by-step guidance.
8. **Secure Authentication**: Fully functional Sign In & Sign Up portal with persistent database storage.

## 🚀 Technologies Used
* **Backend:** Python, Flask, Flask-SQLAlchemy, SQLite
* **Frontend:** Tailwind CSS, HTML5, JavaScript, Lucide Icons, Web Speech API
* **AI Integration:** Google GenAI SDK (`gemini-2.5-flash` model for intelligent tutoring, adaptive questioning, and step-by-step problem solving)
- **Data Storage**: SQLite (`mathquest.db`).
- **Deployment Ready**: Render / Vercel compatible with `gunicorn` and `requirements.txt`.

## Local Setup Instructions
1. **Clone or Download the Repository** into your local environment.
2. **Create a Python Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate