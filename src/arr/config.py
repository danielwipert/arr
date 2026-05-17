"""Runtime configuration for the ARR pipeline.

Single source of truth is `config/default.yaml`. The YAML is validated via
Pydantic so a bad config fails fast. Secrets (API keys) come from environment
variables, never from the YAML.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "default.yaml"


class ArxivConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    categories: list[str]
    lookback_hours: int = Field(gt=0)
    max_results_per_category: int = Field(gt=0)


class KeywordPrefilterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    keywords: list[str] = Field(default_factory=list)


class FilterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dedup_similarity_threshold: float = Field(ge=0.0, le=1.0)
    dedup_lookback_days: int = Field(gt=0)
    embedding_model: str
    keyword_prefilter: KeywordPrefilterConfig = Field(default_factory=KeywordPrefilterConfig)


class RankerWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    significance: float
    novelty: float
    reproducibility: float
    clarity: float
    topical_fit: float

    def as_dict(self) -> dict[str, float]:
        return self.model_dump()


class RankerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weights: RankerWeights


class SelectorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    post_worthy_threshold: float = Field(ge=0.0, le=10.0)


class LengthConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_min: int = Field(gt=0)
    target_max: int = Field(gt=0)
    hook_max: int = Field(gt=0)
    hard_min: int = Field(gt=0)
    hard_max: int = Field(gt=0)


class DrafterConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    max_retries: int = Field(ge=1, le=10)
    length: LengthConfig


class CriticConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str


class StorageConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviews_dir: str
    cache_dir: str


class LLMConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    base_url: str


class Settings(BaseModel):
    """Validated, immutable view of the YAML config plus any required secrets."""

    model_config = ConfigDict(extra="forbid")

    arxiv: ArxivConfig
    filter: FilterConfig
    ranker: RankerConfig
    selector: SelectorConfig
    drafter: DrafterConfig
    critic: CriticConfig
    cheap_model: str
    storage: StorageConfig
    llm: LLMConfig
    max_candidates_per_run: int = Field(default=10, ge=1)

    openrouter_api_key: SecretStr | None = None


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader. We avoid a python-dotenv dep for one file."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Don't clobber an explicitly-set env var.
        os.environ.setdefault(key, value)


def load_settings(config_path: Path | None = None) -> Settings:
    """Load settings from a YAML file plus environment variables."""
    _load_dotenv(REPO_ROOT / ".env")
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        raw["openrouter_api_key"] = api_key
    return Settings(**raw)
