from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from chain import chain

app = FastAPI(
    title="RAG Assistant",
    version="2.0",
)

# Store conversation history in memory
chat_history = []

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(q: Question):
    global chat_history
    try:
        answer = chain(q.question, chat_history)

        # Save this turn to history
        chat_history.append({
            "user": q.question,
            "assistant": answer
        })

        # Keep only last 10 turns to avoid prompt getting too long
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]

        return JSONResponse(content={"answer": answer})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/clear")
async def clear_history():
    global chat_history
    chat_history = []
    return JSONResponse(content={"message": "Conversation history cleared."})

@app.get("/")
async def root():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2563eb;
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
        }
        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }
        .header p {
            font-size: 14px;
            margin-top: 5px;
            opacity: 0.9;
        }
        #clear-btn {
            padding: 8px 16px;
            background-color: white;
            color: #2563eb;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }
        #clear-btn:hover {
            background-color: #e0e7ff;
        }
        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 16px;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .message.user {
            background-color: #2563eb;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .message.assistant {
            background-color: white;
            color: #1f2937;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .message.assistant b {
            color: #1d4ed8;
        }
        .message.loading {
            background-color: #e5e7eb;
            color: #6b7280;
        }
        #input-container {
            padding: 20px;
            background-color: white;
            border-top: 1px solid #e5e7eb;
            display: flex;
            gap: 12px;
        }
        #question {
            flex: 1;
            padding: 12px 16px;
            font-size: 16px;
            border: 1px solid #d1d5db;
            border-radius: 24px;
            outline: none;
        }
        #submit {
            padding: 12px 24px;
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
        }
        #submit:hover:not(:disabled) {
            background-color: #1d4ed8;
        }
        #submit:disabled {
            background-color: #9ca3af;
            cursor: not-allowed;
        }
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 8px 0;
        }
        .typing-indicator span {
            width: 8px;
            height: 8px;
            background-color: #9ca3af;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📚 RAG Assistant</h1>
            <p>Ask me anything about your documents!</p>
        </div>
        <button id="clear-btn">🗑 Clear Chat</button>
    </div>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="question" placeholder="Ask anything about your documents..." autocomplete="off">
        <button id="submit">Send</button>
    </div>
    <script>
        const chatContainer = document.getElementById('chat-container');
        const questionInput = document.getElementById('question');
        const submitButton = document.getElementById('submit');
        const clearButton = document.getElementById('clear-btn');

        function formatMessage(text) {
            text = text.split('**').map(function(part, i) {
                return i % 2 === 1 ? '<b>' + part + '</b>' : part;
            }).join('');
            text = text.split('\\n').join('<br>');
            return text;
        }

        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user' : 'assistant');

            if (text === 'typing') {
                messageDiv.classList.add('loading');
                messageDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
            } else if (isUser) {
                messageDiv.textContent = text;
            } else {
                messageDiv.innerHTML = formatMessage(text);
            }

            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }

        async function sendQuestion() {
            const question = questionInput.value.trim();
            if (!question) return;

            addMessage(question, true);
            questionInput.value = '';
            submitButton.disabled = true;

            const loadingMsg = addMessage('typing', false);

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ question: question })
                });

                const data = await response.json();
                loadingMsg.remove();

                if (data.error) {
                    addMessage('Error: ' + data.error, false);
                } else {
                    addMessage(data.answer, false);
                }
            } catch (error) {
                loadingMsg.remove();
                addMessage('Error: ' + error.message, false);
            }

            submitButton.disabled = false;
            questionInput.focus();
        }

        async function clearChat() {
            await fetch('/clear', { method: 'POST' });
            chatContainer.innerHTML = '';
        }

        submitButton.addEventListener('click', sendQuestion);
        clearButton.addEventListener('click', clearChat);
        questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendQuestion();
        });

        questionInput.focus();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)