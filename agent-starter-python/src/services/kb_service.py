from pathlib import Path

KB_FILE = Path(__file__).parent.parent / "data" / "knowledge_base.md"


def get_knowledge_base() -> str:
    with open(KB_FILE, encoding="utf-8") as f:
        return f.read()