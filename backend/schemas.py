from pydantic import BaseModel, Field
from typing import Optional, List

class AskRequest(BaseModel):
    question: str = Field(..., description="The user's question, prompt, or instruction")
    language: Optional[str] = Field("General", description="Target programming language (e.g. Python, Java, C, C++, General)")
    mode: Optional[str] = Field("normal", description="Operation mode: 'generate', 'explain', 'debug', or 'normal'")
    code: Optional[str] = Field(None, description="Optional source code snippet for explain or debug modes")

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Description of the program to generate")
    language: str = Field("Python", description="Target programming language")

class ExplainRequest(BaseModel):
    code: str = Field(..., description="Source code to explain")
    language: Optional[str] = Field("Python", description="Programming language of the code")
    question: Optional[str] = Field("", description="Specific question about the code")

class DebugRequest(BaseModel):
    code: str = Field(..., description="Buggy or broken source code to debug")
    language: Optional[str] = Field("Python", description="Programming language")
    error_message: Optional[str] = Field("", description="Error message or unexpected behavior observed")

class CodeRunRequest(BaseModel):
    language: str = Field(..., description="Programming language: python, java, c, cpp")
    code: str = Field(..., description="Source code to execute")
    input: Optional[str] = Field("", description="Standard input (stdin) for the program")

class AIResponse(BaseModel):
    success: bool
    answer: str
    mode: str
    language: Optional[str] = None
    provider: Optional[str] = None
    error: Optional[str] = None

class CodeRunResponse(BaseModel):
    success: bool
    output: str
    error: str = ""
    status: str = "success"  # 'success', 'compile_error', 'runtime_error', 'timeout', 'server_error'
    execution_time_ms: Optional[int] = None
    language: str
    version: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    ai_configured: bool
    ai_provider: str
    supported_languages: List[str]
