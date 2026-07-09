const conversationId = crypto.randomUUID();

const messages = document.getElementById("messages");
const composer = document.getElementById("composer");
const input = document.getElementById("input");
const send = document.getElementById("send");

function addMessage(text, role) {
  const el = document.createElement("div");
  el.className = `message message--${role}`;
  el.textContent = text;
  messages.append(el);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(message) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!response.ok) {
    throw new Error(`Server responded ${response.status}`);
  }
  const data = await response.json();
  return data.reply;
}

composer.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";
  input.disabled = true;
  send.disabled = true;

  try {
    addMessage(await sendMessage(message), "assistant");
  } catch (error) {
    addMessage(`Could not send message: ${error.message}`, "error");
  } finally {
    input.disabled = false;
    send.disabled = false;
    input.focus();
  }
});
