"""Provider abstractions — the model-independence boundary.

Anything that could vary by AI vendor (semantic error analysis, embeddings)
is isolated behind these interfaces. The system ships deterministic local
implementations so it runs offline and tests stay reproducible; plugging a
real provider means implementing one class and registering it, with no
changes to pipeline code.

Example (adding OpenAI-style analysis):

    class MyLLM(LLMProvider):
        def analyze_error(self, raw_message: str, context: dict) -> dict:
            ...call your API...
            return {"category": "db_migration", "summary": "..."}

    pipeline = Pipeline(store, llm=MyLLM())
"""
from __future__ import annotations

import hashlib
import re
import zlib
from abc import ABC, abstractmethod
from typing import Dict, List


class LLMProvider(ABC):
    """Optional semantic layer for error analysis.

    Implementations MUST be optional: the deterministic analyzer in
    analysis.py covers the MVP; an LLM can only *enrich* results
    (categories/summaries), never gate them.
    """

    name = "abstract"

    @abstractmethod
    def analyze_error(self, raw_message: str, context: Dict) -> Dict:
        """Return {'category': str|None, 'summary': str|None}."""


class NullLLM(LLMProvider):
    """Deterministic no-op: signals that no semantic enrichment is active."""

    name = "null"

    def analyze_error(self, raw_message: str, context: Dict) -> Dict:
        return {"category": None, "summary": None}


class EmbeddingProvider(ABC):
    """Text -> dense vector, used optionally to improve retrieval."""

    name = "abstract"
    dim = 0

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        ...


class HashingEmbedder(EmbeddingProvider):
    """Deterministic local embedder (feature hashing).

    Not semantically deep — it captures token overlap structure so retrieval
    works offline. Swap for a real embedding provider when quality matters
    more than reproducibility.
    """

    name = "hashing-v1"

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for tok in re.findall(r"[a-z]{3,}", text.lower()):
            h = int.from_bytes(
                hashlib.md5(tok.encode()).digest()[:4], "little")
            idx = h % self.dim
            sign = 1.0 if (zlib.crc32(tok.encode()) & 1) else -1.0
            vec[idx] += sign
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))
