import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi.testclient import TestClient
from main import app

class TestSmartCodeAIRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("SmartCode AI", res.text)
        self.assertIn("Start Coding", res.text)

    def test_assistant_page(self):
        res = self.client.get("/assistant")
        self.assertEqual(res.status_code, 200)
        self.assertIn("SmartCode AI Chat", res.text)
        self.assertIn("chat-input", res.text)

    def test_editor_page(self):
        res = self.client.get("/editor")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Editor", res.text)
        self.assertIn("Run Code", res.text)

    def test_about_page(self):
        res = self.client.get("/about")
        self.assertEqual(res.status_code, 200)
        self.assertIn("College Project Presentation", res.text)
        self.assertIn("Problem Statement", res.text)

    def test_css_static_file(self):
        res = self.client.get("/css/style.css")
        self.assertEqual(res.status_code, 200)
        self.assertIn("--bg-primary", res.text)

    def test_js_static_files(self):
        for js_file in ["config.js", "main.js", "assistant.js", "editor.js"]:
            res = self.client.get(f"/js/{js_file}")
            self.assertEqual(res.status_code, 200)

    def test_api_code_execution_python_factorial(self):
        payload = {
            "language": "python",
            "code": "def fact(n):\n    return 1 if n<=1 else n*fact(n-1)\nprint(fact(5))",
            "input": ""
        }
        res = self.client.post("/api/run-code", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["output"].strip(), "120")

    def test_api_code_execution_c_sum(self):
        payload = {
            "language": "c",
            "code": "#include <stdio.h>\nint main() { printf(\"Sum = %d\", 10 + 25); return 0; }",
            "input": ""
        }
        res = self.client.post("/api/run-code", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["output"].strip(), "Sum = 35")

    def test_api_code_execution_java_greeting(self):
        payload = {
            "language": "java",
            "code": "public class Main { public static void main(String[] args) { System.out.println(\"Java Runner OK\"); } }",
            "input": ""
        }
        res = self.client.post("/api/run-code", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("Java Runner OK", data["output"])

if __name__ == "__main__":
    unittest.main()
