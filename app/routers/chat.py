import logging
import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.agent import ask

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(
        None,
        description="Pass the same id to continue a conversation.",
    )


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    session_id = payload.session_id or str(uuid.uuid4())
    try:
        reply = ask(payload.message, session_id)
    except Exception as exc:
        cause = exc.__cause__ or exc.__context__
        detail = str(exc)
        if cause:
            detail = f"{exc} ({type(cause).__name__}: {cause})"
        logger.exception("Chat agent failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Chat agent failed: {detail}",
        ) from exc
    return ChatResponse(reply=reply, session_id=session_id)


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Q&A Agent</title>
  <style>
    body { font-family: sans-serif; max-width: 720px; margin: 2rem auto; }
    #log { border: 1px solid #ccc; min-height: 240px; padding: 1rem; white-space: pre-wrap; }
    form { display: flex; gap: 0.5rem; margin-top: 0.75rem; }
    input { flex: 1; padding: 0.5rem; }
  </style>
</head>
<body>
  <h1>Q&A Agent</h1>
  <div id="log"></div>
  <form id="f">
    <input id="msg" autocomplete="off" placeholder="Ask a question" />
    <button>Send</button>
  </form>
  <script>
    let sessionId = null;
    const log = document.getElementById("log");
    document.getElementById("f").addEventListener("submit", async (e) => {
      e.preventDefault();
      const input = document.getElementById("msg");
      const message = input.value.trim();
      if (!message) return;
      log.textContent += "You: " + message + "\\n";
      input.value = "";
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId }),
      });
      const data = await res.json();
      if (!res.ok) {
        log.textContent += "Error: " + (data.detail || res.status) + "\\n";
        return;
      }
      sessionId = data.session_id;
      log.textContent += "Agent: " + data.reply + "\\n\\n";
    });
  </script>
</body>
</html>
"""
