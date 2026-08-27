import os

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver

_agent = None
_checkpointer = InMemorySaver()


def _anthropic_api_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip().strip('"').strip("'")
    if key.upper().startswith("ANTHROPIC_API_KEY="):
        key = key.split("=", 1)[1].strip().strip('"').strip("'")
    return key


def get_agent():
    global _agent
    if _agent is None:
        api_key = _anthropic_api_key()
        if not api_key:
            raise RuntimeError("Set ANTHROPIC_API_KEY to use the chat agent.")
        os.environ["ANTHROPIC_API_KEY"] = api_key

        model_name = os.getenv("CHAT_MODEL", "anthropic:claude-sonnet-4-5")
        if model_name.startswith("anthropic:"):
            model_name = model_name.split(":", 1)[1]

        _agent = create_agent(
            model=ChatAnthropic(
                model=model_name,
                api_key=api_key,
                timeout=60.0,
            ),
            system_prompt=(
                "You are a concise Q&A assistant. "
                "Answer clearly and directly. If you do not know, say so."
            ),
            checkpointer=_checkpointer,
        )
    return _agent


def ask(message: str, session_id: str) -> str:
    result = get_agent().invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": session_id}},
    )
    last = result["messages"][-1]
    content = last.content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content)
