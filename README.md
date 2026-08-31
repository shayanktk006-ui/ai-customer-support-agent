# 🤖 AI Customer Support Agent

An AI-powered customer support chatbot with function calling — built with Google Gemini, Flask, and vanilla JavaScript. The agent can answer questions using company knowledge, perform calculations, and remembers conversation context.

## 🚀 Features

- Real-time chat interface (Flask + HTML/CSS/JS)
- Function calling — the agent uses a **calculator tool** for math and a **search_web tool** for external info
- Conversation memory — remembers context across messages
- Grounded answers from company knowledge (products, shipping, returns, support hours)
- Multi-language support (responds in the language the user writes in)
- Clean, responsive chat UI

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **LLM:** Google Gemini (`google-genai`)
- **Frontend:** HTML, CSS, JavaScript (fetch API)
- **CORS handling:** flask-cors

## ⚙️ Setup & Installation

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/ai-support-agent.git
   cd ai-support-agent
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Add your Gemini API key
   - Copy `env.example` to `.env`
   - Add your API key from [Google AI Studio](https://aistudio.google.com)
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

4. Run the app
   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser

## 🧠 How It Works

1. User sends a message through the chat UI
2. Flask forwards it to Gemini along with company info and conversation history
3. If a calculation or external lookup is needed, Gemini triggers a **function call**
4. The corresponding Python tool runs and returns a result to Gemini
5. Gemini generates the final, grounded response

## 📝 License

Open source, for learning purposes.

---

Built by **Muhammad Shayan Khurshid**
