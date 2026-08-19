import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from schemas import (
    AskRequest,
    GenerateRequest,
    ExplainRequest,
    DebugRequest,
    CodeRunRequest,
    AIResponse,
    CodeRunResponse,
    HealthResponse
)
import ai_service
import code_runner

# Initialize FastAPI App
app = FastAPI(
    title="SmartCode AI - Backend API",
    description="A student-friendly AI Code Assistant REST API for code generation, explanation, debugging, and execution.",
    version="1.0.0"
)

# Configure CORS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")] if allowed_origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Returns server status, active AI provider, and supported languages."""
    return HealthResponse(
        status="healthy",
        app_name="SmartCode AI",
        version="1.0.0",
        ai_configured=ai_service.is_ai_configured(),
        ai_provider=ai_service.get_active_provider_name(),
        supported_languages=["Python", "Java", "C", "C++", "General"]
    )

@app.post("/api/ask", response_model=AIResponse, tags=["AI Assistant"])
def ask_assistant(req: AskRequest):
    """
    Main unified endpoint for asking SmartCode AI.
    Accepts question, language, mode ('generate', 'explain', 'debug', 'normal'), and optional code.
    """
    try:
        result = ai_service.ask_ai(
            question=req.question,
            language=req.language or "General",
            mode=req.mode or "normal",
            code=req.code
        )
        return AIResponse(**result)
    except Exception as e:
        return AIResponse(
            success=False,
            answer="",
            mode=req.mode or "normal",
            language=req.language,
            error=f"AI service error: {str(e)}"
        )

@app.post("/api/generate", response_model=AIResponse, tags=["AI Assistant"])
def generate_code(req: GenerateRequest):
    """Specialized endpoint for generating programming code."""
    try:
        result = ai_service.ask_ai(
            question=req.prompt,
            language=req.language or "Python",
            mode="generate"
        )
        return AIResponse(**result)
    except Exception as e:
        return AIResponse(
            success=False,
            answer="",
            mode="generate",
            language=req.language,
            error=f"Code generation error: {str(e)}"
        )

@app.post("/api/explain", response_model=AIResponse, tags=["AI Assistant"])
def explain_code(req: ExplainRequest):
    """Specialized endpoint for explaining code and programming concepts."""
    try:
        prompt = req.question if req.question else "Please explain this code in detail."
        result = ai_service.ask_ai(
            question=prompt,
            language=req.language or "Python",
            mode="explain",
            code=req.code
        )
        return AIResponse(**result)
    except Exception as e:
        return AIResponse(
            success=False,
            answer="",
            mode="explain",
            language=req.language,
            error=f"Code explanation error: {str(e)}"
        )

@app.post("/api/debug", response_model=AIResponse, tags=["AI Assistant"])
def debug_code(req: DebugRequest):
    """Specialized endpoint for identifying errors and providing corrected code."""
    try:
        prompt = f"Debug this code. Error observed: {req.error_message}" if req.error_message else "Find and fix bugs in this code."
        result = ai_service.ask_ai(
            question=prompt,
            language=req.language or "Python",
            mode="debug",
            code=req.code
        )
        return AIResponse(**result)
    except Exception as e:
        return AIResponse(
            success=False,
            answer="",
            mode="debug",
            language=req.language,
            error=f"Code debugging error: {str(e)}"
        )

@app.post("/api/run-code", response_model=CodeRunResponse, tags=["Code Runner"])
def run_code(req: CodeRunRequest):
    """
    Executes user code in an isolated sandbox for Python, Java, C, and C++.
    Supports custom standard input (stdin).
    """
    try:
        result = code_runner.execute_code(
            language=req.language,
            code=req.code,
            user_input=req.input
        )
        return CodeRunResponse(**result)
    except Exception as e:
        return CodeRunResponse(
            success=False,
            output="",
            error=f"Execution error: {str(e)}",
            status="server_error",
            language=req.language
        )

# -------------------------------------------------------------
# Frontend Static Files & Page Routing
# -------------------------------------------------------------
FRONTEND_DIR = BASE_DIR.parent / "frontend"

if FRONTEND_DIR.exists():
    # Mount static assets (CSS, JS, images)
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/", response_class=FileResponse, tags=["Frontend"])
    def serve_home():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/assistant", response_class=FileResponse, tags=["Frontend"])
    def serve_assistant():
        return FileResponse(FRONTEND_DIR / "assistant.html")

    @app.get("/editor", response_class=FileResponse, tags=["Frontend"])
    def serve_editor():
        return FileResponse(FRONTEND_DIR / "editor.html")

    @app.get("/about", response_class=FileResponse, tags=["Frontend"])
    def serve_about():
        return FileResponse(FRONTEND_DIR / "about.html")

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error occurred.", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f">> Starting SmartCode AI server on http://localhost:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
