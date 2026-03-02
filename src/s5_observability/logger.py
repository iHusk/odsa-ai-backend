"""Structured logging for pipeline observability.

Each query gets a PipelineLogger instance that collects timing and metadata
from every stage (embed, retrieve, generate). When the query is done, call
finalize() to append a single JSON object to logs/pipeline.jsonl.

Usage:
    from src.s5_observability.logger import PipelineLogger, StageTimer

    logger = PipelineLogger(query="What is RAG?")

    with StageTimer() as t:
        embedding = embed(query)
    logger.log_embed(latency_ms=t.elapsed_ms, model="voyage-3", input_chars=len(query))

    with StageTimer() as t:
        results = retrieve(embedding, n=5)
    logger.log_retrieve(
        latency_ms=t.elapsed_ms,
        n_results=len(results),
        scores=[r["score"] for r in results],
        sources=[r["source"] for r in results],
    )

    with StageTimer() as t:
        answer = generate(query, results)
    logger.log_generate(
        latency_ms=t.elapsed_ms,
        model="claude-sonnet-4-5",
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        stop_reason=response.stop_reason,
    )

    log_entry = logger.finalize()  # writes to logs/pipeline.jsonl

Reading logs back:
    from src.s5_observability.logger import load_logs

    entries = load_logs()  # list of dicts, one per query
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path


class StageTimer:
    """Context manager for timing pipeline stages.

    Captures wall-clock elapsed time in milliseconds. Use one StageTimer
    per stage, then pass elapsed_ms to the corresponding log method.

    Example:
        with StageTimer() as t:
            result = some_operation()
        print(f"Took {t.elapsed_ms}ms")
    """

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.elapsed_ms = int((self.end - self.start) * 1000)


class PipelineLogger:
    """Structured logger for a single query through the RAG pipeline.

    Collects timing, token counts, retrieval scores, and source metadata
    for each stage. Call finalize() to write the complete log entry to
    a JSONL file.
    """

    def __init__(self, query: str):
        self.query_id = str(uuid.uuid4())[:8]
        self.query = query
        self.stages: dict[str, dict] = {}
        self.timestamp = datetime.now().isoformat()

    def log_embed(self, latency_ms: int, model: str, input_chars: int) -> None:
        """Log the embedding stage."""
        self.stages["embed"] = {
            "latency_ms": latency_ms,
            "model": model,
            "input_chars": input_chars,
        }

    def log_retrieve(
        self,
        latency_ms: int,
        n_results: int,
        scores: list[float],
        sources: list[str],
        filter_applied: dict | None = None,
    ) -> None:
        """Log the retrieval stage."""
        self.stages["retrieve"] = {
            "latency_ms": latency_ms,
            "n_results": n_results,
            "top_score": max(scores) if scores else 0.0,
            "low_score": min(scores) if scores else 0.0,
            "score_spread": round(max(scores) - min(scores), 4) if scores else 0.0,
            "sources": sources,
            "unique_sources": len(set(sources)),
            "filter_applied": filter_applied,
        }

    def log_generate(
        self,
        latency_ms: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
        stop_reason: str,
    ) -> None:
        """Log the generation stage."""
        self.stages["generate"] = {
            "latency_ms": latency_ms,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "stop_reason": stop_reason,
        }

    def to_dict(self) -> dict:
        """Convert the log entry to a dictionary for inspection or serialization."""
        total_latency = sum(
            stage.get("latency_ms", 0) for stage in self.stages.values()
        )
        return {
            "query_id": self.query_id,
            "query": self.query,
            "timestamp": self.timestamp,
            "stages": self.stages,
            "total_latency_ms": total_latency,
        }

    def finalize(self, log_dir: str = "logs") -> dict:
        """Write log entry to JSONL file and return the dict.

        Writes to {log_dir}/pipeline.jsonl, one JSON object per line.
        Creates the directory if it doesn't exist.
        """
        log_entry = self.to_dict()
        log_path = Path(log_dir) / "pipeline.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return log_entry


def load_logs(log_dir: str = "logs") -> list[dict]:
    """Read all pipeline log entries from the JSONL file.

    Returns a list of dicts, one per logged query. If the log file
    does not exist, returns an empty list.
    """
    log_path = Path(log_dir) / "pipeline.jsonl"

    if not log_path.exists():
        return []

    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    return entries
