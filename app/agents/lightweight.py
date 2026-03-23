from __future__ import annotations

from pathlib import Path

from pydantic_ai import Agent

from app.config import settings
from app.context_hub.repo import ContextHubRepo
from app.models.event import Event


def _load_soul() -> str:
    soul_path = Path(__file__).with_name("soul.md")
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")
    return ""


agent = Agent(
    f"huggingface:{settings.llm_model}",
    instructions=_load_soul() + "\nYou are an assistant inside an AI operating system. Be concise.",
)


@agent.tool
def save_idea(title: str, body: str) -> str:
    hub = Path(settings.context_hub_path)
    inbox = hub / "inbox" / "ideas.md"
    inbox.parent.mkdir(parents=True, exist_ok=True)
    existing = ""
    if inbox.exists():
        existing = inbox.read_text(encoding="utf-8")
    new_text = existing + f"\n\n## {title.strip()}\n\n{body.strip()}\n"
    inbox.write_text(new_text.lstrip("\n"), encoding="utf-8")
    return "saved"


def run_lightweight_agent(event: Event, message_text: str | None) -> dict:
    if not settings.huggingface_api_key:
        return {"kind": "agent", "error": "HUGGINGFACE_API_KEY not configured"}

    hub_repo = ContextHubRepo()
    hub_repo.pull_latest()

    user_text = message_text or ""

    prompt = (
        "You are replying to a WhatsApp user. Provide a helpful, short response." 
        "If the message contains an idea worth saving, call save_idea(title, body)."
        f"\n\nUser message:\n{user_text}\n\nRaw event payload:\n{event.payload}"
    )
    result = agent.run_sync(prompt)
    hub_repo.commit_and_push("Agent update")
    return {"kind": "agent", "model": settings.llm_model, "reply": result.output}

