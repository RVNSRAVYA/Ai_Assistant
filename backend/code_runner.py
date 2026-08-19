import time
import re
import requests
from typing import Dict, Any, Optional

# Wandbox Free Public Sandbox API
WANDBOX_API_URL = "https://wandbox.org/api/compile.json"

# Supported language mappings and stable compilers
COMPILER_MAP = {
    "python": {"compiler": "cpython-3.12.7", "name": "Python 3.12"},
    "py": {"compiler": "cpython-3.12.7", "name": "Python 3.12"},
    "cpp": {"compiler": "gcc-13.2.0", "name": "C++ (GCC 13.2)"},
    "c++": {"compiler": "gcc-13.2.0", "name": "C++ (GCC 13.2)"},
    "c": {"compiler": "gcc-13.2.0-c", "name": "C (GCC 13.2)"},
    "java": {"compiler": "openjdk-jdk-21+35", "name": "Java (OpenJDK 21)"},
}

def execute_code(language: str, code: str, user_input: Optional[str] = "") -> Dict[str, Any]:
    """
    Executes source code safely in an isolated remote sandbox environment via Wandbox API.
    Supports Python, Java, C, and C++ with custom standard input (stdin).
    """
    norm_lang = language.strip().lower()
    lang_info = COMPILER_MAP.get(norm_lang)

    if not lang_info:
        return {
            "success": False,
            "output": "",
            "error": f"Unsupported language '{language}'. Supported languages: Python, Java, C, C++.",
            "status": "server_error",
            "language": language,
            "execution_time_ms": 0,
            "version": None
        }

    if not code or not code.strip():
        return {
            "success": False,
            "output": "",
            "error": "Source code cannot be empty.",
            "status": "client_error",
            "language": language,
            "execution_time_ms": 0,
            "version": None
        }

    # Pre-process code for single-file sandbox compatibility
    processed_code = code
    if norm_lang == "java":
        # In single-file Java compilation (prog.java), 'public class' causes a compile mismatch
        # Changing 'public class' to 'class' resolves this for any class name
        processed_code = re.sub(r'\bpublic\s+class\b', 'class', processed_code)

    payload = {
        "compiler": lang_info["compiler"],
        "code": processed_code,
        "stdin": user_input or "",
        "options": "warning,gnu++20" if norm_lang in ["cpp", "c++"] else ""
    }

    start_time = time.time()

    try:
        response = requests.post(WANDBOX_API_URL, json=payload, timeout=25)
        duration_ms = int((time.time() - start_time) * 1000)

        if response.status_code != 200:
            return {
                "success": False,
                "output": "",
                "error": f"Execution service returned status code {response.status_code}: {response.text}",
                "status": "server_error",
                "language": lang_info["name"],
                "execution_time_ms": duration_ms,
                "version": None
            }

        data = response.json()
        
        # Check for compilation errors
        compiler_error = data.get("compiler_error") or ""
        compiler_output = data.get("compiler_output") or ""
        status_code = str(data.get("status", "0"))
        signal = data.get("signal", "")
        program_output = data.get("program_output") or ""
        program_error = data.get("program_error") or ""

        # If compiler produced a fatal error
        if compiler_error and (status_code != "0" or not program_output):
            return {
                "success": False,
                "output": compiler_output,
                "error": compiler_error.strip(),
                "status": "compile_error",
                "language": lang_info["name"],
                "execution_time_ms": duration_ms,
                "version": lang_info["compiler"]
            }

        # Check for timeout / signals
        if signal in ["SIGKILL", "SIGTERM", "SIGXCPU"]:
            return {
                "success": False,
                "output": program_output,
                "error": "Time Limit Exceeded (Execution timed out). Check for infinite loops or unhandled recursion.",
                "status": "timeout",
                "language": lang_info["name"],
                "execution_time_ms": duration_ms,
                "version": lang_info["compiler"]
            }

        # Runtime errors
        if status_code != "0" and program_error:
            return {
                "success": False,
                "output": program_output,
                "error": program_error.strip(),
                "status": "runtime_error",
                "language": lang_info["name"],
                "execution_time_ms": duration_ms,
                "version": lang_info["compiler"]
            }

        # Successful execution
        output_text = program_output if program_output else "(Program executed successfully with no stdout output)"
        return {
            "success": True,
            "output": output_text,
            "error": program_error.strip() if program_error else "",
            "status": "success",
            "language": lang_info["name"],
            "execution_time_ms": duration_ms,
            "version": lang_info["compiler"]
        }

    except requests.exceptions.Timeout:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "output": "",
            "error": "Execution service timed out. Please check your internet connection and try again.",
            "status": "timeout",
            "language": lang_info["name"],
            "execution_time_ms": duration_ms,
            "version": None
        }
    except requests.exceptions.RequestException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "output": "",
            "error": f"Failed to connect to isolated code execution engine: {str(e)}",
            "status": "server_error",
            "language": lang_info["name"],
            "execution_time_ms": duration_ms,
            "version": None
        }
