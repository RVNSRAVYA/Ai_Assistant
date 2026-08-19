/**
 * SmartCode AI - Code Editor Logic
 * Handles: Monaco init, language switch, run code, debug with AI, ask AI to explain,
 *          receive code from assistant via sessionStorage
 */

const CODE_TEMPLATES = {
  python: `# Python 3 - Hello World
name = input("Enter your name: ")
print(f"Hello, {name}!")
`,
  cpp: `#include <iostream>
using namespace std;

int main() {
    string name;
    cout << "Enter your name: ";
    cin >> name;
    cout << "Hello, " << name << "!" << endl;
    return 0;
}
`,
  c: `#include <stdio.h>

int main() {
    char name[100];
    printf("Enter your name: ");
    scanf("%s", name);
    printf("Hello, %s!\\n", name);
    return 0;
}
`,
  java: `import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter your name: ");
        String name = sc.nextLine();
        System.out.println("Hello, " + name + "!");
    }
}
`
};

let monacoEditor = null;
let currentLang = 'python';

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadMonacoEditor();
  setupLanguageSwitch();
  setupButtons();
  loadTransferredCode();
});

// ─── Monaco Editor ───────────────────────────────────────────────────────────
function loadMonacoEditor() {
  require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
  require(['vs/editor/editor.main'], () => {
    monacoEditor = monaco.editor.create(document.getElementById('monaco-editor-container'), {
      value: CODE_TEMPLATES[currentLang],
      language: currentLang,
      theme: 'vs-dark',
      automaticLayout: true,
      fontSize: 14,
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      minimap: { enabled: false },
      wordWrap: 'on',
      scrollBeyondLastLine: false,
      tabSize: 4
    });
  });
}

// ─── Language Switcher ────────────────────────────────────────────────────────
function setupLanguageSwitch() {
  const select = document.getElementById('editor-language-select');
  if (!select) return;

  select.addEventListener('change', () => {
    currentLang = select.value;
    if (!monacoEditor) return;

    const monacoLangMap = { python: 'python', cpp: 'cpp', c: 'c', java: 'java' };
    monaco.editor.setModelLanguage(monacoEditor.getModel(), monacoLangMap[currentLang] || 'plaintext');
    monacoEditor.setValue(CODE_TEMPLATES[currentLang] || '');
    clearConsole();
  });
}

// ─── Buttons ─────────────────────────────────────────────────────────────────
function setupButtons() {
  const runBtn   = document.getElementById('run-code-btn');
  const resetBtn = document.getElementById('reset-code-btn');
  const clearBtn = document.getElementById('clear-console-btn');
  const debugBtn = document.getElementById('debug-with-ai-btn');
  const askAiBtn = document.getElementById('ask-ai-btn');

  if (runBtn)   runBtn.addEventListener('click', runCode);
  if (resetBtn) resetBtn.addEventListener('click', resetCode);
  if (clearBtn) clearBtn.addEventListener('click', clearConsole);
  if (debugBtn) debugBtn.addEventListener('click', debugWithAI);
  if (askAiBtn) askAiBtn.addEventListener('click', askAIExplain);
}

// ─── Receive Code from AI Chat ────────────────────────────────────────────────
function loadTransferredCode() {
  const code = sessionStorage.getItem('smartcode_editor_code');
  const lang = sessionStorage.getItem('smartcode_editor_lang');

  if (code) {
    sessionStorage.removeItem('smartcode_editor_code');
    sessionStorage.removeItem('smartcode_editor_lang');

    // Wait for Monaco to init
    const wait = setInterval(() => {
      if (monacoEditor) {
        clearInterval(wait);

        // Set language in select
        if (lang) {
          const normalized = normalizeLang(lang);
          const select = document.getElementById('editor-language-select');
          if (select && CODE_TEMPLATES[normalized]) {
            select.value = normalized;
            currentLang = normalized;
            monaco.editor.setModelLanguage(monacoEditor.getModel(), normalized);
          }
        }

        monacoEditor.setValue(code);
        showToast('Code opened in editor!', 'success');
      }
    }, 200);
  }
}

function normalizeLang(lang) {
  const l = (lang || '').toLowerCase();
  if (l === 'python' || l === 'py') return 'python';
  if (l === 'c++' || l === 'cpp')   return 'cpp';
  if (l === 'c')                     return 'c';
  if (l === 'java')                  return 'java';
  return 'python';
}

// ─── Run Code ────────────────────────────────────────────────────────────────
async function runCode() {
  if (!monacoEditor) return showToast('Editor not ready yet!', 'warning');

  const code  = monacoEditor.getValue().trim();
  const stdin = document.getElementById('stdin-input')?.value || '';
  const runBtn = document.getElementById('run-code-btn');

  if (!code) return showToast('Write some code first!', 'warning');

  setStatus('running');
  setOutput('Running your code...', 'muted');
  document.getElementById('debug-with-ai-btn').style.display = 'none';

  if (runBtn) {
    runBtn.disabled = true;
    runBtn.textContent = '⏳ Running...';
  }

  const start = Date.now();

  try {
    const res = await fetch(`${getApiBase()}/api/run-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, language: currentLang, stdin })
    });

    const elapsed = Date.now() - start;
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Server error');

    const output = data.output || data.stdout || '';
    const error  = data.error  || data.stderr || '';
    const combined = [output, error].filter(Boolean).join('\n').trim();

    if (error && !output) {
      setStatus('error');
      setOutput(combined, 'error');
      document.getElementById('debug-with-ai-btn').style.display = 'inline-flex';
      sessionStorage.setItem('smartcode_debug_error', error);
    } else {
      setStatus('success');
      setOutput(combined || '(No output)', 'success');
    }

    const timeEl = document.getElementById('execution-time-badge');
    if (timeEl) timeEl.textContent = `${elapsed} ms`;
  } catch (err) {
    setStatus('error');
    setOutput(`Connection error: ${err.message}\n\nMake sure the backend server is running.`, 'error');
    document.getElementById('debug-with-ai-btn').style.display = 'inline-flex';
  } finally {
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.innerHTML = '▶ Run Code';
    }
  }
}

// ─── Debug With AI ────────────────────────────────────────────────────────────
function debugWithAI() {
  if (!monacoEditor) return;
  const code  = monacoEditor.getValue().trim();
  const error = sessionStorage.getItem('smartcode_debug_error') ||
                document.getElementById('console-output')?.textContent || '';

  sessionStorage.setItem('smartcode_transfer_code',  code);
  sessionStorage.setItem('smartcode_transfer_lang',  currentLang);
  sessionStorage.setItem('smartcode_transfer_mode',  'debug');
  sessionStorage.setItem('smartcode_transfer_error', error);

  window.location.href = 'assistant.html';
}

// ─── Ask AI to Explain current code ──────────────────────────────────────────
function askAIExplain() {
  if (!monacoEditor) return;
  const code = monacoEditor.getValue().trim();
  if (!code) return showToast('Write some code first!', 'warning');

  sessionStorage.setItem('smartcode_transfer_code', code);
  sessionStorage.setItem('smartcode_transfer_lang', currentLang);
  sessionStorage.setItem('smartcode_transfer_mode', 'explain');

  window.location.href = 'assistant.html';
}

// ─── Reset Code ───────────────────────────────────────────────────────────────
function resetCode() {
  if (!monacoEditor) return;
  monacoEditor.setValue(CODE_TEMPLATES[currentLang] || '');
  clearConsole();
  showToast('Code reset to default template', 'info');
}

// ─── Console Helpers ──────────────────────────────────────────────────────────
function clearConsole() {
  setOutput('Press ▶ Run Code to execute your program.', 'muted');
  setStatus('ready');
  const timeEl = document.getElementById('execution-time-badge');
  if (timeEl) timeEl.textContent = '-- ms';
  document.getElementById('debug-with-ai-btn').style.display = 'none';
}

function setOutput(text, type = 'default') {
  const el = document.getElementById('console-output');
  if (!el) return;
  el.textContent = text;
  el.className = 'console-output';
  if (type === 'error')   el.classList.add('console-error');
  if (type === 'success') el.classList.add('console-success');
  if (type === 'muted')   el.style.color = 'var(--text-dim)';
  else                    el.style.color = '';
}

function setStatus(status) {
  const badge = document.getElementById('execution-status-badge');
  if (!badge) return;
  const map = {
    ready:   ['● Ready',   'badge-ready'],
    running: ['● Running', 'badge-running'],
    success: ['● Success', 'badge-success'],
    error:   ['● Error',   'badge-error']
  };
  const [label, cls] = map[status] || map.ready;
  badge.textContent = label;
  badge.className = `status-badge ${cls}`;
}
