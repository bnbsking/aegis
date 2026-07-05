const accountInput = document.getElementById("account-id");
const sessionList = document.getElementById("session-list");
const newSessionBtn = document.getElementById("new-session");
const titleInput = document.getElementById("title-input");
const messagesEl = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

let currentSessionId = null;
let currentHistory = [];

function accountId() {
  return accountInput.value.trim() || "demo";
}

async function api(path, options) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`${options?.method || "GET"} ${path} -> ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

function setChatEnabled(enabled) {
  chatInput.disabled = !enabled;
  sendBtn.disabled = !enabled;
  titleInput.disabled = !enabled;
}

async function loadSessions() {
  const sessions = await api(`/api/sessions?account_id=${encodeURIComponent(accountId())}`);
  sessionList.innerHTML = "";
  for (const s of sessions) {
    const li = document.createElement("li");
    li.className = s.session_id === currentSessionId ? "active" : "";
    li.textContent = s.title || "(untitled)";
    li.onclick = () => selectSession(s.session_id);

    const delBtn = document.createElement("button");
    delBtn.className = "delete-btn";
    delBtn.textContent = "✕";
    delBtn.onclick = async (e) => {
      e.stopPropagation();
      await api(`/api/sessions/${s.session_id}?account_id=${encodeURIComponent(accountId())}`, { method: "DELETE" });
      if (currentSessionId === s.session_id) {
        currentSessionId = null;
        currentHistory = [];
        renderMessages();
        setChatEnabled(false);
      }
      loadSessions();
    };
    li.appendChild(delBtn);
    sessionList.appendChild(li);
  }
}

async function selectSession(sessionId) {
  currentSessionId = sessionId;
  currentHistory = await api(`/api/sessions/${sessionId}/history?account_id=${encodeURIComponent(accountId())}`);
  setChatEnabled(true);
  const sessions = await api(`/api/sessions?account_id=${encodeURIComponent(accountId())}`);
  titleInput.value = sessions.find((s) => s.session_id === sessionId)?.title || "";
  renderMessages();
  loadSessions();
}

function renderMessages() {
  messagesEl.innerHTML = "";
  currentHistory.forEach((msg, idx) => {
    const div = document.createElement("div");
    div.className = `msg ${msg.role}`;
    div.textContent = msg.content;

    if (msg.role === "user") {
      const editBtn = document.createElement("button");
      editBtn.className = "edit-btn";
      editBtn.textContent = "edit & regenerate";
      editBtn.onclick = () => editAndRegenerate(idx);
      div.appendChild(editBtn);
    }
    messagesEl.appendChild(div);
  });
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function editAndRegenerate(idx) {
  const original = currentHistory[idx].content;
  const edited = prompt("Edit message (everything after it will be discarded):", original);
  if (edited === null) return;

  const truncated = currentHistory.slice(0, idx + 1);
  truncated[idx] = { role: "user", content: edited };

  const { reply } = await api(`/api/sessions/${currentSessionId}/edit_regenerate`, {
    method: "POST",
    body: JSON.stringify({ account_id: accountId(), history: truncated }),
  });
  currentHistory = [...truncated, { role: "assistant", content: reply }];
  renderMessages();
  loadSessions();
}

newSessionBtn.onclick = async () => {
  const { session_id } = await api(`/api/sessions?account_id=${encodeURIComponent(accountId())}`, { method: "POST" });
  await loadSessions();
  selectSession(session_id);
};

chatForm.onsubmit = async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text || !currentSessionId) return;
  chatInput.value = "";
  currentHistory.push({ role: "user", content: text });
  renderMessages();

  const { reply } = await api(`/api/sessions/${currentSessionId}/chat`, {
    method: "POST",
    body: JSON.stringify({ account_id: accountId(), text }),
  });
  currentHistory.push({ role: "assistant", content: reply });
  renderMessages();
  loadSessions();
};

titleInput.onchange = async () => {
  if (!currentSessionId) return;
  await api(`/api/sessions/${currentSessionId}/title`, {
    method: "PATCH",
    body: JSON.stringify({ account_id: accountId(), new_title: titleInput.value }),
  });
  loadSessions();
};

accountInput.onchange = () => {
  currentSessionId = null;
  currentHistory = [];
  renderMessages();
  setChatEnabled(false);
  loadSessions();
};

loadSessions();
