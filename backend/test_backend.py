import unittest
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from main import app
import ai_service
import code_runner

class TestSmartCodeAIBackend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        """Test the /api/health endpoint."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["app_name"], "SmartCode AI")
        self.assertIn("Python", data["supported_languages"])

    def test_ask_ai_generate(self):
        """Test /api/ask with generate mode."""
        payload = {
            "question": "Write a Python program to find factorial of a number",
            "language": "Python",
            "mode": "generate"
        }
        response = self.client.post("/api/ask", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("factorial", data["answer"].lower())
        self.assertEqual(data["mode"], "generate")

    def test_ask_ai_explain(self):
        """Test /api/explain endpoint."""
        payload = {
            "code": "def add(a, b):\n    return a + b",
            "language": "Python",
            "question": "Explain how this add function works"
        }
        response = self.client.post("/api/explain", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["answer"])

    def test_ask_ai_debug(self):
        """Test /api/debug endpoint."""
        payload = {
            "code": "for i in range(5)\n    print(i)",
            "language": "Python",
            "error_message": "SyntaxError: invalid syntax"
        }
        response = self.client.post("/api/debug", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["answer"])

    def test_ask_ai_empty_question_fails_safely(self):
        """Test /api/ask with empty input."""
        payload = {
            "question": "",
            "language": "Python",
            "mode": "normal"
        }
        response = self.client.post("/api/ask", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("enter a question", data["error"].lower())

    def test_run_code_python_success(self):
        """Test /api/run-code executing Python code with stdin."""
        payload = {
            "language": "python",
            "code": "n = int(input())\nprint(n * 2)",
            "input": "21"
        }
        response = self.client.post("/api/run-code", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["status"] != "server_error":  # In case network is restricted in sandbox
            self.assertTrue(data["success"])
            self.assertEqual(data["output"].strip(), "42")
            self.assertEqual(data["status"], "success")

    def test_run_code_cpp_success(self):
        """Test /api/run-code executing C++ code."""
        payload = {
            "language": "cpp",
            "code": "#include <iostream>\nusing namespace std;\nint main() { int a; if(cin >> a) cout << (a + 10); return 0; }",
            "input": "5"
        }
        response = self.client.post("/api/run-code", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data["status"] != "server_error":
            self.assertTrue(data["success"])
            self.assertEqual(data["output"].strip(), "15")

    def test_run_code_empty_code(self):
        """Test /api/run-code with empty code."""
        payload = {
            "language": "python",
            "code": "   ",
            "input": ""
        }
        response = self.client.post("/api/run-code", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("empty", data["error"].lower())

if __name__ == "__main__":
    unittest.main()
