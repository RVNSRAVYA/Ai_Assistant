/**
 * SmartCode AI - Assistant Chat Logic
 * Handles: send message, AI response, copy code, open in editor, URL prompt params
 */

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('chat-send-btn');
const clearBtn = document.getElementById('clear-chat-btn');

let isWaiting = false;

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupSuggestionChips();
  setupInputBehavior();
  checkTransferParams();   // Handle URL ?prompt= or sessionStorage transfers

  if (sendBtn) sendBtn.addEventListener('click', handleSendMessage);
  if (clearBtn) clearBtn.addEventListener('click', clearChat);

  // Configure marked + highlight.js
  if (typeof marked !== 'undefined') {
    marked.setOptions({
      highlight: (code, lang) => {
        if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
          return hljs.highlight(code, { language: lang }).value;
        }
        return typeof hljs !== 'undefined' ? hljs.highlightAuto(code).value : code;
      },
      breaks: true,
      gfm: true
    });
  }
});

// ─── Suggestion chips ────────────────────────────────────────────────────────
function setupSuggestionChips() {
  document.querySelectorAll('.prompt-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      if (chatInput) {
        chatInput.value = btn.dataset.prompt;
        handleSendMessage();
      }
    });
  });
}

// ─── Input auto-resize + Enter to send ───────────────────────────────────────
function setupInputBehavior() {
  if (!chatInput) return;
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 160) + 'px';
  });
}

// ─── URL + sessionStorage transfer params ───────────────────────────────────
function checkTransferParams() {
  // 1. URL query param: assistant.html?prompt=...
  const urlParams = new URLSearchParams(window.location.search);
  const urlPrompt = urlParams.get('prompt');

  // 2. sessionStorage: from Code Editor (debug/explain)
  const transferCode  = sessionStorage.getItem('smartcode_transfer_code');
  const transferLang  = sessionStorage.getItem('smartcode_transfer_lang') || 'python';
  const transferMode  = sessionStorage.getItem('smartcode_transfer_mode') || 'debug';
  const transferError = sessionStorage.getItem('smartcode_transfer_error') || '';

  if (transferCode) {
    // Clear storage first
    sessionStorage.removeItem('smartcode_transfer_code');
    sessionStorage.removeItem('smartcode_transfer_lang');
    sessionStorage.removeItem('smartcode_transfer_mode');
    sessionStorage.removeItem('smartcode_transfer_error');

    const action = transferMode === 'explain' ? 'Explain this' : 'Debug this';
    const errorPart = transferError ? `\n\nError:\n${transferError}` : '';
    const prompt = `${action} ${transferLang} code:${errorPart}\n\`\`\`${transferLang}\n${transferCode}\n\`\`\``;

    if (chatInput) {
      chatInput.value = prompt;
      handleSendMessage();
    }
    return;
  }

  if (urlPrompt && chatInput) {
    chatInput.value = decodeURIComponent(urlPrompt);
    handleSendMessage();
  }
}

// ─── Send Message ────────────────────────────────────────────────────────────
async function handleSendMessage() {
  if (!chatInput || isWaiting) return;

  const text = chatInput.value.trim();
  if (!text) return;

  appendUserMessage(text);
  chatInput.value = '';
  chatInput.style.height = 'auto';

  const typingId = appendTypingIndicator();
  isWaiting = true;
  if (sendBtn) {
    sendBtn.disabled = true;
    sendBtn.textContent = '...';
  }

  try {
    const response = await fetch(`${getApiBase()}/api/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, context: 'chat' })
    });

    removeTypingIndicator(typingId);

    if (!response.ok) {
      throw new Error(`Server error ${response.status}`);
    }

    const data = await response.json();
    appendAIMessage(data.response || 'No response received.');
  } catch (err) {
    removeTypingIndicator(typingId);
    appendAIMessage(`⚠️ Could not reach the server. Make sure the backend is running.\n\n_Error: ${err.message}_`);
  } finally {
    isWaiting = false;
    if (sendBtn) {
      sendBtn.disabled = false;
      sendBtn.textContent = '⚡ Send';
    }
  }
}

// ─── Render Messages ─────────────────────────────────────────────────────────
function appendUserMessage(text) {
  const div = document.createElement('div');
  div.className = 'message-row user';
  div.innerHTML = `
    <div class="msg-content user-msg">${escapeHtml(text)}</div>
    <div class="msg-avatar user-avatar">You</div>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
}

function appendAIMessage(markdown) {
  const div = document.createElement('div');
  div.className = 'message-row ai';

  let html = markdown;
  if (typeof marked !== 'undefined') {
    html = marked.parse(markdown);
  } else {
    html = escapeHtml(markdown).replace(/\n/g, '<br>');
  }

  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-content ai-msg">${html}</div>
  `;
  chatMessages.appendChild(div);

  // Attach action buttons to each code block
  div.querySelectorAll('pre code').forEach(codeEl => {
    const pre = codeEl.parentElement;
    const lang = [...codeEl.classList].find(c => c.startsWith('language-'))?.replace('language-', '') || 'python';
    const code = codeEl.innerText;

    const toolbar = document.createElement('div');
    toolbar.className = 'code-toolbar';
    toolbar.innerHTML = `
      <span class="code-lang-badge">${lang}</span>
      <div style="display:flex;gap:6px;">
        <button class="code-action-btn" title="Copy code">📋 Copy</button>
        <button class="code-action-btn code-editor-btn" title="Open in Code Editor">💻 Open in Editor</button>
      </div>
    `;

    toolbar.querySelector('.code-action-btn').addEventListener('click', () => {
      navigator.clipboard.writeText(code).then(() => {
        showToast('Code copied!', 'success');
      });
    });

    toolbar.querySelector('.code-editor-btn').addEventListener('click', () => {
      sessionStorage.setItem('smartcode_editor_code', code);
      sessionStorage.setItem('smartcode_editor_lang', lang);
      window.location.href = 'editor.html';
    });

    pre.insertBefore(toolbar, codeEl);
  });

  // Syntax highlight
  if (typeof hljs !== 'undefined') {
    div.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));
  }

  scrollToBottom();
}

function appendTypingIndicator() {
  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.className = 'message-row ai';
  div.id = id;
  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-content ai-msg typing-indicator">
      <span></span><span></span><span></span>
    </div>
  `;
  chatMessages.appendChild(div);
  scrollToBottom();
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ─── Clear Chat ───────────────────────────────────────────────────────────────
function clearChat() {
  if (!chatMessages) return;
  chatMessages.innerHTML = `
    <div class="message-row ai">
      <div class="msg-avatar">⚡</div>
      <div class="msg-content">
        <strong>Chat cleared!</strong>
        <p style="margin-top:6px;color:var(--text-muted);">Ask me anything — coding, general knowledge, or say hi!</p>
      </div>
    </div>
  `;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function scrollToBottom() {
  if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}
