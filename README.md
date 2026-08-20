# ⚡ SmartCode AI - Intelligent Web-Based Coding Assistant

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Monaco Editor](https://img.shields.io/badge/Editor-Monaco-blueviolet.svg)](https://microsoft.github.io/monaco-editor/)

**SmartCode AI** is a complete, working, deployable **AI Code Assistant website** designed specifically as a **college-level project**. It allows students and beginners to ask computer science questions, generate code, understand complex algorithms, debug syntax/logical errors, and run code in an isolated multi-language execution sandbox.

---

## 🎯 1. Project Overview

### 1.1 Problem Statement
Computer science students often struggle when learning to code due to:
* Cryptic compiler errors and lack of beginner-friendly explanations.
* Complex setup steps for local development environments.
* Difficulty translating algorithm logic into clean, functional code.

### 1.2 Proposed Solution
SmartCode AI bridges this gap with an intuitive, unified web portal featuring:
1. **Interactive AI Assistant**: Generates code, explains logic line-by-line, identifies bugs, and answers general CS questions.
2. **Built-in Monaco Code Editor**: Dark-themed code editor with line numbers, syntax highlighting, and starter boilerplate code.
3. **Isolated Code Execution Sandbox**: Executes Python, Java, C, and C++ safely with standard input (stdin) and instant terminal output.

---

## ⭐ 2. Core Features

* **⚡ Code Generation**: Generates full working code in Python, Java, C, and C++ with step-by-step logic, complexity analysis, and test cases.
* **📖 Code Explanation**: Breaks down code into simple terms with dry runs and concept explanations.
* **🛠️ Code Debugging**: Identifies errors (syntax, runtime, logical), explains root causes, and delivers clean fixed code.
* **💡 General CS Q&A**: Answers conceptual questions (e.g. OOP, Data Structures, Complexity) with student-friendly analogies.
* **🚀 Multi-Language Code Runner**: Run Python, Java, C, and C++ with stdin support without installing local compilers.
* **🔒 Secure Architecture**: Zero API keys exposed on frontend; all user code executes in safe isolated containers.
* **⚡ Smart Offline / Demo Mode**: Guarantees fail-safe college presentations even without an internet connection or API key.

---

## 🛠️ 3. Technology Stack

### Frontend
* **HTML5 & CSS3**: Custom responsive developer dark theme with glassmorphism effects.
* **Vanilla JavaScript (ES6+)**: Fast, lightweight, zero framework overhead (No React/Next.js).
* **Monaco Editor**: Professional VS Code editor engine loaded via CDN.
* **Marked.js & Highlight.js**: Rich Markdown and syntax-highlighted AI response rendering.

### Backend
* **Python 3.10+**
* **FastAPI**: Modern, high-performance web framework for building REST APIs.
* **Uvicorn**: Lightning-fast ASGI web server.
* **Pydantic v2**: Data validation and response serialization.

### AI Engine & Execution
* **AI Provider**: OpenRouter, Google Gemini API (free tier), Groq Cloud, or OpenAI compatible API (configurable via `.env`).
* **Code Execution**: Piston Sandbox Engine API (safe containerized execution).

---

## 📂 4. Project Directory Structure

```text
smartcode-ai/
│
├── frontend/                   # Frontend Web Application
│   ├── index.html              # Home / Landing Page
│   ├── assistant.html          # AI Assistant Page (Generate, Explain, Debug, Q&A)
│   ├── editor.html             # Code Editor & Sandbox Page
│   ├── about.html              # College Project Documentation & Viva Guide
│   │
│   ├── css/
│   │   └── style.css           # Modern Developer Dark Theme stylesheet
│   │
│   └── js/
│       ├── config.js           # API Endpoints & Base URL resolution
│       ├── main.js             # Shared helpers, toasts, health checks
│       ├── assistant.js        # AI Assistant requests & Markdown rendering
│       └── editor.js           # Monaco Editor & Code Execution Runner
│
├── backend/                    # FastAPI Backend Server
│   ├── main.py                 # App entry point, CORS, static routes, REST APIs
│   ├── ai_service.py           # Multi-provider AI interface (Gemini/Groq/OpenAI/Offline)
│   ├── code_runner.py          # Safe code execution client (Piston API)
│   ├── schemas.py              # Pydantic data schemas
│   ├── test_backend.py         # Automated test suite
│   ├── requirements.txt        # Python backend dependencies
│   ├── .env.example            # Environment configuration template
│   └── .env                    # Local environment variables
│
├── README.md                   # Complete documentation & project guide
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── run_app.bat                 # One-click startup script for Windows
├── run_app.ps1                 # PowerShell startup script
└── run_app.sh                  # Linux / macOS startup script
```

---

## 🚀 5. Quick Start & Installation

### Prerequisites
* Python 3.10 or higher ([Download Python](https://www.python.org/downloads/))
* Git ([Download Git](https://git-scm.com/))

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/smartcode-ai.git
cd smartcode-ai
```

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and set your preferred AI API key:
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=your_google_gemini_api_key_here
```
> 💡 *Note: You can get a free Google Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey). If left empty, SmartCode AI automatically runs in **Smart Offline / Demo Mode**.*

For OpenRouter, configure the backend with:
```ini
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openrouter/auto
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```
The key stays on the backend and is never sent to frontend JavaScript.

### Step 4: Run the Application
Start the FastAPI server:
```bash
python main.py
```
Or use the one-click startup script:
* **Windows**: Double-click `run_app.bat`
* **macOS / Linux**: `bash run_app.sh`

### Step 5: Open in Your Browser
Visit: **[http://localhost:8000](http://localhost:8000)**

---

## 📡 6. Backend REST API Endpoints

| Method | Endpoint | Description | Sample Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & active AI provider info | *None* |
| `POST` | `/api/ask` | Main unified AI query endpoint | `{"question": "...", "language": "Python", "mode": "generate"}` |
| `POST` | `/api/generate` | Specialized code generation | `{"prompt": "Factorial program", "language": "Python"}` |
| `POST` | `/api/explain` | Code explanation endpoint | `{"code": "def add(a,b): return a+b", "language": "Python"}` |
| `POST` | `/api/debug` | Code debugging endpoint | `{"code": "print(x", "language": "Python"}` |
| `POST` | `/api/run-code` | Multi-language sandbox execution | `{"language": "python", "code": "print(5*2)", "input": ""}` |

### Interactive Swagger API Docs:
Open **[http://localhost:8000/docs](http://localhost:8000/docs)** to test all endpoints interactively in your browser.

---

## 🧪 7. Running Automated Tests

SmartCode AI includes an automated test suite verifying all API endpoints and execution runtimes:

```bash
cd backend
python test_backend.py
```

Expected output:
```text
Ran 8 tests in 2.48s
OK
```

---

## 🌐 8. Deployment Guide

### Option A: Deploy Both Backend & Frontend on Render.com (Recommended Free Option)
1. Push your repository to GitHub.
2. Sign up on [Render.com](https://render.com/).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Set:
   * **Root Directory**: `backend`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable: `GEMINI_API_KEY = your_key`.
7. Click **Deploy Web Service**. Render provides a free `https://your-app.onrender.com` URL that serves both the API and the frontend!

### Option B: Decoupled Deployment
* **Backend**: Deploy `backend/` on Render or Railway.
* **Frontend**: Deploy `frontend/` on GitHub Pages or Vercel. In `frontend/js/config.js`, update `BASE_URL` with your live backend domain.

---

## 🎓 9. College Project Presentation & Viva Guide

### Frequently Asked Questions by Project Evaluators:

**Q1: What problem does SmartCode AI solve?**
> *Answer*: It provides computer science students with a unified educational platform to learn programming concepts, receive AI-guided explanations, fix bugs with root-cause analysis, and execute multi-language code without local compiler setup hurdles.

**Q2: Why did you choose FastAPI over Flask or Django?**
> *Answer*: FastAPI offers asynchronous concurrency, automatic interactive OpenAPI/Swagger documentation, fast execution speed with Starlette and Pydantic validation, and clean type hints.

**Q3: How does the system ensure security during code execution?**
> *Answer*: The system never runs user code on the host server. Instead, it delegates code execution to an isolated sandbox engine with strict memory, CPU, and execution timeout (5-second) constraints.

**Q4: How are AI credentials protected?**
> *Answer*: API keys are stored solely on the server in protected environment variables (`.env`) and are never exposed to client-side JavaScript.

---

## 🔮 10. Future Enhancements

* 👤 User authentication and profile management (Firebase Auth).
* 📜 Persistent question history and bookmarked solutions.
* 🎙️ Voice input for speech-to-code interaction.
* 👥 Real-time collaborative peer coding in the Monaco editor.
* 📱 Mobile application via React Native / Flutter.

---

## 📜 11. License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
