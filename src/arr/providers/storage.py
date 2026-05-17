"""Storage provider abstraction.

Stage outputs land in `reviews/YYYY-MM-DD/` as JSON and Markdown files. The
abstraction lets the pipeline target a different backend later (cloud
bucket, content-addressed store) without touching stage code.
"""

from __future__ import annotations

from datetime import date as date_cls
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel


class StorageProvider(Protocol):
    def write_artifact(
        self, run_date: date_cls, kind: str, artifact: BaseModel
    ) -> Path:
        """Write a stage artifact as JSON. Returns the path written."""
        ...

    def write_post(self, run_date: date_cls, post_text: str) -> Path:
        """Write the human-readable post.md for the day."""
        ...

    def write_text(self, run_date: date_cls, filename: str, content: str) -> Path:
        """Write any other text file (grounding.md, etc.) into the day's folder."""
        ...

    def write_pdf(self, run_date: date_cls, pdf_bytes: bytes) -> Path:
        """Persist the source paper PDF alongside the post."""
        ...

    def write_named_artifact(
        self, run_date: date_cls, kind: str, name: str, artifact: BaseModel
    ) -> Path:
        """Write one of N artifacts of the same kind, e.g. processed/<arxiv_id>.json."""
        ...

    def write_root_artifact(
        self, run_date: date_cls, name: str, artifact: BaseModel
    ) -> Path:
        """Write a single named JSON at the day-folder root, e.g. skip.json."""
        ...

    def day_folder(self, run_date: date_cls) -> Path:
        """Return (and ensure) the per-day folder."""
        ...


class LocalFilesystemStorage:
    """Default storage backend: writes under `<reviews_dir>/YYYY-MM-DD/`.

    Layout matches Section 6.3 of the spec.
    """

    def __init__(self, reviews_dir: Path) -> None:
        self._root = Path(reviews_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    def day_folder(self, run_date: date_cls) -> Path:
        folder = self._root / run_date.isoformat()
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def write_artifact(
        self, run_date: date_cls, kind: str, artifact: BaseModel
    ) -> Path:
        path = self.day_folder(run_date) / f"{kind}.json"
        path.write_text(
            artifact.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path

    def write_post(self, run_date: date_cls, post_text: str) -> Path:
        path = self.day_folder(run_date) / "post.md"
        path.write_text(post_text, encoding="utf-8")
        return path

    def write_text(self, run_date: date_cls, filename: str, content: str) -> Path:
        path = self.day_folder(run_date) / filename
        path.write_text(content, encoding="utf-8")
        return path

    def write_pdf(self, run_date: date_cls, pdf_bytes: bytes) -> Path:
        path = self.day_folder(run_date) / "paper.pdf"
        path.write_bytes(pdf_bytes)
        return path

    def write_named_artifact(
        self, run_date: date_cls, kind: str, name: str, artifact: BaseModel
    ) -> Path:
        folder = self.day_folder(run_date) / kind
        folder.mkdir(parents=True, exist_ok=True)
        # arxiv ids contain '/'; flatten for filesystem use.
        safe_name = name.replace("/", "_")
        path = folder / f"{safe_name}.json"
        path.write_text(artifact.model_dump_json(indent=2), encoding="utf-8")
        return path

    def write_root_artifact(
        self, run_date: date_cls, name: str, artifact: BaseModel
    ) -> Path:
        path = self.day_folder(run_date) / f"{name}.json"
        path.write_text(artifact.model_dump_json(indent=2), encoding="utf-8")
        return path
