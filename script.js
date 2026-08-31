const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const messages = document.getElementById("messages");
const sendBtn = document.getElementById("send-btn");

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  const p = document.createElement("p");
  p.textContent = text;
  div.appendChild(p);
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return div;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const userText = input.value.trim();
  if (!userText) return;

  addMessage(userText, "user");
  input.value = "";
  sendBtn.disabled = true;

  const typingEl = addMessage("Typing...", "typing");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: userText })
    });

    if (!response.ok) {
      throw new Error(`Server responded with status ${response.status}`);
    }

    const data = await response.json();
    typingEl.remove();
    addMessage(data.reply, "agent");

  } catch (error) {
    console.error("Chat error:", error);
    typingEl.remove();
    addMessage("Sorry, I am unable to connect to the AI Agent.", "agent");
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
});
