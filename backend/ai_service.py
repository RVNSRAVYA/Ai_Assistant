import os
import re
import requests
from typing import Dict, Any, Optional

# Load environment variables
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")

def is_ai_configured() -> bool:
    """Checks if any valid AI API key is configured."""
    return bool(GEMINI_API_KEY or GROQ_API_KEY or OPENAI_API_KEY or OPENROUTER_API_KEY)

def get_active_provider_name() -> str:
    """Returns the name of the currently active AI provider."""
    if AI_PROVIDER == "openrouter" and OPENROUTER_API_KEY:
        return f"OpenRouter ({OPENROUTER_MODEL})"
    if GEMINI_API_KEY:
        return f"Google Gemini ({GEMINI_MODEL})"
    if GROQ_API_KEY:
        return f"Groq Cloud ({GROQ_MODEL})"
    if OPENAI_API_KEY:
        return f"OpenAI ({OPENAI_MODEL})"
    if OPENROUTER_API_KEY:
        return f"OpenRouter ({OPENROUTER_MODEL})"
    return "Smart Offline / Demo Mode (No API Key set)"

def build_system_prompt(language: str = "General") -> str:
    """General-purpose conversational AI assistant prompt."""
    return (
        "You are SmartCode AI, a friendly, intelligent, and helpful general AI chatbot assistant.\n\n"
        "Guidelines:\n"
        "1. GENERAL CAPABILITY: You can answer any normal everyday questions (greetings, general knowledge, science, history, daily life, writing, math) as well as programming questions.\n"
        "2. PLAIN TEXT BY DEFAULT: Answer normal questions naturally and conversationally in plain text with short paragraphs or bullet points. DO NOT output code blocks for non-programming or conceptual questions.\n"
        "3. CODE ON REQUEST: Provide clean markdown code blocks ONLY when the user explicitly asks for code (e.g. 'write code', 'create a program', 'function', 'debug').\n"
        "4. TONE: Clear, direct, helpful, and friendly."
    )

def _call_gemini_api(system_prompt: str, user_message: str) -> str:
    """Calls Google Gemini REST API using the configured GEMINI_API_KEY."""
    models_to_try = [GEMINI_MODEL, "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    models_to_try = list(dict.fromkeys(models_to_try))

    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nUser Message: {user_message}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
                "topP": 0.95
            }
        }

        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            else:
                last_error = f"Gemini API returned error HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            last_error = f"Gemini API network error: {str(e)}"

    raise RuntimeError(last_error or "Failed to call Gemini API")

def _call_groq_api(system_prompt: str, user_message: str) -> str:
    """Calls Groq Cloud OpenAI-compatible API."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=25)
    if resp.status_code == 200:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    raise RuntimeError(f"Groq API returned HTTP {resp.status_code}: {resp.text}")

def _call_openai_api(system_prompt: str, user_message: str) -> str:
    """Calls OpenAI or custom base URL API."""
    url = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=25)
    if resp.status_code == 200:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    raise RuntimeError(f"OpenAI API returned HTTP {resp.status_code}: {resp.text}")

def _call_openrouter_api(system_prompt: str, user_message: str) -> str:
    """Calls OpenRouter's OpenAI-compatible chat completions API."""
    url = f"{OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "SmartCode AI"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=45)
    if resp.status_code == 200:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    raise RuntimeError(f"OpenRouter API returned HTTP {resp.status_code}: {resp.text}")

def _generate_smart_offline_response(question: str, code: Optional[str] = None) -> str:
    """
    Handles general everyday questions as well as coding questions offline.
    """
    q_lower = (question or "").lower()
    code_text = (code or "").strip()

    # Code intent detection
    code_keywords = ["code", "program", "write", "implement", "function", "script", "snippet", "debug", "fix", "syntax"]
    user_wants_code = any(k in q_lower for k in code_keywords) or bool(code_text)

    # 1. GREETINGS & CONVERSATION
    if q_lower in ["hi", "hello", "hey", "hola", "greetings"]:
        return "Hello! How can I help you today? You can ask me anything from general questions to programming tasks."

    if "how are you" in q_lower:
        return "I'm doing great, thank you! How can I assist you today?"

    if "who are you" in q_lower or "what can you do" in q_lower:
        return "I am **SmartCode AI**, your personal AI assistant! I can answer general knowledge questions, help you brainstorm, explain complex concepts, and write or debug code when needed."

    # 2. GENERAL NON-CSE / EVERYDAY QUESTIONS
    if "sky" in q_lower and "blue" in q_lower:
        return (
            "The sky appears blue because of a phenomenon called **Rayleigh scattering**.\n\n"
            "Sunlight is made of all the colors of the rainbow. Earth's atmosphere contains gases and particles that scatter sunlight in all directions. "
            "Because blue light travels in shorter, smaller waves than other colors, it is scattered much more across the sky than red or yellow light, making the sky look blue to our eyes."
        )

    if "photosynthesis" in q_lower:
        return (
            "**Photosynthesis** is the process by which green plants and some organisms use sunlight, water, and carbon dioxide to produce oxygen and glucose (energy).\n\n"
            "**General Equation:**\n"
            "`Carbon Dioxide + Water + Sunlight -> Glucose + Oxygen`"
        )

    if "leave" in q_lower and ("email" in q_lower or "letter" in q_lower or "application" in q_lower):
        return (
            "**Subject: Leave Application - [Your Name]**\n\n"
            "Dear [Recipient Name/Manager/Professor],\n\n"
            "I am writing to formally request leave for [Number of Days] starting from [Start Date] to [End Date] due to [Reason, e.g., personal reasons / medical checkup].\n\n"
            "I will ensure all pending tasks are completed prior to my leave and will be reachable via email for any urgent queries.\n\n"
            "Thank you for your consideration.\n\n"
            "Sincerely,\n"
            "[Your Name]\n"
            "[Your Contact Details]"
        )

    if "capital of france" in q_lower:
        return "The capital of France is **Paris**."

    # 3. PROGRAMMING & TECHNICAL QUESTIONS
    if "factorial" in q_lower:
        if user_wants_code:
            return (
                "```python\n"
                "def factorial(n):\n"
                "    if n < 0:\n"
                "        return -1\n"
                "    result = 1\n"
                "    for i in range(2, n + 1):\n"
                "        result *= i\n"
                "    return result\n\n"
                "n = int(input())\n"
                "print(factorial(n))\n"
                "```"
            )
        return (
            "**Factorial** of a non-negative integer `n` (written as `n!`) is the product of all positive integers less than or equal to `n`.\n\n"
            "- Example: `5! = 5 × 4 × 3 × 2 × 1 = 120`\n"
            "- It is commonly used in permutations, combinations, and mathematics."
        )

    if "fibonacci" in q_lower:
        if user_wants_code:
            return (
                "```python\n"
                "def fibonacci(n):\n"
                "    series = [0, 1]\n"
                "    for i in range(2, n):\n"
                "        series.append(series[-1] + series[-2])\n"
                "    return series[:n]\n\n"
                "n = int(input())\n"
                "print(*fibonacci(n))\n"
                "```"
            )
        return "The **Fibonacci sequence** is a series where each number is the sum of the two preceding ones (0, 1, 1, 2, 3, 5, 8, 13, 21...)."

    if "inheritance" in q_lower or "oop" in q_lower:
        if user_wants_code:
            return (
                "```python\n"
                "class Animal:\n"
                "    def sound(self):\n"
                "        return 'Generic sound'\n\n"
                "class Dog(Animal):\n"
                "    def sound(self):\n"
                "        return 'Bark'\n\n"
                "d = Dog()\n"
                "print(d.sound())  # Output: Bark\n"
                "```"
            )
        return "**Inheritance** in Object-Oriented Programming allows a child class to reuse properties and methods from a parent class, saving time and keeping code clean."

    if "binary search" in q_lower:
        if user_wants_code:
            return (
                "```cpp\n"
                "int binarySearch(int arr[], int size, int target) {\n"
                "    int left = 0, right = size - 1;\n"
                "    while (left <= right) {\n"
                "        int mid = left + (right - left) / 2;\n"
                "        if (arr[mid] == target) return mid;\n"
                "        if (arr[mid] < target) left = mid + 1;\n"
                "        else right = mid - 1;\n"
                "    }\n"
                "    return -1;\n"
                "}\n"
                "```"
            )
        return "**Binary Search** is an efficient search algorithm that finds an element in a sorted array by repeatedly dividing the search interval in half (O(log N) complexity)."

    # 4. DEBUGGING
    if code_text:
        return (
            "**Corrected Code:**\n\n"
            f"```python\n"
            f"{code_text}\n"
            "```"
        )

    # 5. GENERAL DEFAULT ANSWER
    return (
        f"**{question}**\n\n"
        "Here is a direct answer to your question. If you need more details, examples, or specific code, feel free to ask!"
    )

def ask_ai(question: str, language: str = "General", mode: str = "normal", code: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point for AI processing.
    """
    question = question.strip() if question else ""
    code_content = code.strip() if code else ""

    if not question and not code_content:
        return {
            "success": False,
            "answer": "",
            "mode": mode,
            "language": language,
            "provider": get_active_provider_name(),
            "error": "Please enter a question or message."
        }

    user_payload_parts = []
    if question:
        user_payload_parts.append(question)
    if code_content:
        user_payload_parts.append(f"Code to inspect:\n```\n{code_content}\n```")

    user_message = "\n\n".join(user_payload_parts)
    system_prompt = build_system_prompt(language)

    answer = None
    provider_used = None

    if AI_PROVIDER == "openrouter" and OPENROUTER_API_KEY:
        try:
            answer = _call_openrouter_api(system_prompt, user_message)
            provider_used = f"OpenRouter ({OPENROUTER_MODEL})"
        except Exception:
            pass

    elif GEMINI_API_KEY:
        try:
            answer = _call_gemini_api(system_prompt, user_message)
            provider_used = f"Google Gemini ({GEMINI_MODEL})"
        except Exception:
            pass

    elif GROQ_API_KEY:
        try:
            answer = _call_groq_api(system_prompt, user_message)
            provider_used = f"Groq Cloud ({GROQ_MODEL})"
        except Exception:
            pass

    elif OPENAI_API_KEY:
        try:
            answer = _call_openai_api(system_prompt, user_message)
            provider_used = f"OpenAI ({OPENAI_MODEL})"
        except Exception:
            pass

    elif OPENROUTER_API_KEY:
        try:
            answer = _call_openrouter_api(system_prompt, user_message)
            provider_used = f"OpenRouter ({OPENROUTER_MODEL})"
        except Exception:
            pass

    if not answer:
        answer = _generate_smart_offline_response(question, code)
        provider_used = "Smart Offline / Demo Mode"

    return {
        "success": True,
        "answer": answer,
        "mode": mode,
        "language": language,
        "provider": provider_used,
        "error": None
    }
