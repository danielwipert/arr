"""Paper source provider abstraction.

The default implementation will wrap the `arxiv` Python package: list recent
submissions in the configured categories, then fetch PDFs on demand. The
concrete implementation lands in Phase 2 alongside the ingestor stage.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Protocol

from arr.models import RawPaper


class PaperSourceProvider(Protocol):
    def fetch_recent(
        self, categories: list[str], since: datetime
    ) -> list[RawPaper]:
        ...

    def fetch_pdf(self, arxiv_id: str) -> Path:
        ...
