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


class ScriptedLLM(LLMProvider):
    """Deterministic mock LLM for demos/tests: maps message substrings to
    categories/summaries. Proves the enrichment seam end-to-end without
    any network."""

    name = "scripted"

    def __init__(self, rules):
        # rules: list of (substring, {"category": ..., "summary": ...})
        self.rules = list(rules)

    def analyze_error(self, raw_message: str, context: Dict) -> Dict:
        low = raw_message.lower()
        for needle, result in self.rules:
            if needle.lower() in low:
                return dict(result)
        return {"category": None, "summary": None}


class OpenAICompatLLM(LLMProvider):
    """Real provider for any OpenAI-compatible /chat/completions endpoint
    (OpenAI, Anthropic-compatible gateways, vLLM, Ollama, LM Studio...).
    Uses only the stdlib; failures raise so the pipeline can fall back.

    Example:
        llm = OpenAICompatLLM(base_url="http://localhost:11434/v1",
                              api_key="ollama", model="llama3.2")
        Pipeline(store, llm=llm)
    """

    name = "openai-compat"

    def __init__(self, base_url: str, api_key: str, model: str,
                 timeout_s: int = 20):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_s = timeout_s

    def analyze_error(self, raw_message: str, context: Dict) -> Dict:
        import json as _json
        import urllib.request

        prompt = (
            "Classify this AI-agent failure log line. Reply ONLY with JSON "
            '{"category": "<one of: database_migration, api_rate_limit, '
            'authentication, network_timeout, dependency, other>", '
            '"summary": "<max 12 words>".}\n'
            f"Agent: {context.get('agent','?')}\nLog: {raw_message[:400]}")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=_json.dumps({
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            }).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.api_key}"})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            payload = _json.loads(resp.read())
        text = payload["choices"][0]["message"]["content"].strip()
        start, end = text.find("{"), text.rfind("}") + 1
        parsed = _json.loads(text[start:end])
        cat = parsed.get("category")
        return {"category": cat if cat != "other" else None,
                "summary": parsed.get("summary")}


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
