"""Markdown document loading for the local RAG knowledge base."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Document:
    """A source document and the metadata required to trace its origin."""

    id: str
    content: str
    metadata: dict[str, Any]


class MarkdownLoader:
    """Load every Markdown file in the repository knowledge directory."""

    def __init__(self, knowledge_dir: Path | None = None) -> None:
        default_directory = Path(__file__).resolve().parent.parent / "knowledge"
        self.knowledge_dir = knowledge_dir or default_directory

    def load(self) -> list[Document]:
        """Return UTF-8 Markdown files in deterministic filename order."""
        if not self.knowledge_dir.is_dir():
            raise FileNotFoundError(f"Knowledge directory not found: {self.knowledge_dir}")

        documents = []
        for path in sorted(self.knowledge_dir.glob("*.md")):
            documents.append(
                Document(
                    id=path.stem,
                    content=path.read_text(encoding="utf-8").strip(),
                    metadata={"source": path.name, "path": str(path)},
                )
            )
        return documents
