"""Crash recovery snapshots keyed by absolute document path."""
from __future__ import annotations

import hashlib
import json
import time
import traceback
from pathlib import Path
from typing import Optional

from .config import atomic_write, config_home
from .editor import Buffer


def recovery_path(path: Optional[Path]) -> Path:
    """Return a stable per-document recovery filename."""
    key = str(path.resolve()) if path else "sans_titre"
    digest = hashlib.sha256(key.encode()).hexdigest()[:24]
    return config_home() / "recover" / (digest + ".recover")


def snapshot(buffer: Buffer) -> None:
    """Store a modified buffer without modifying the original file."""
    if buffer.modified:
        path = recovery_path(buffer.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(path, json.dumps({"path": str(buffer.path), "text": buffer.text,
                                      "timestamp": time.time()}, ensure_ascii=False))


def restore(path: Optional[Path]) -> Optional[str]:
    """Read an available recovery snapshot."""
    file = recovery_path(path)
    if file.exists():
        data = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("text"), str):
            raise ValueError(f"Récupération invalide : {file}")
        return data["text"]
    return None


def clear(path: Optional[Path]) -> None:
    """Remove a snapshot after saving or explicitly discarding changes."""
    recovery_path(path).unlink(missing_ok=True)


def purge() -> None:
    """Discard recovery files older than thirty days."""
    directory = config_home() / "recover"
    if directory.exists():
        for path in directory.glob("*.recover"):
            if path.stat().st_mtime < time.time() - 30 * 86400:
                path.unlink()


def log_crash() -> None:
    """Write a bounded exception log without including document content."""
    directory = config_home()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "crash.log"
    old = path.read_text(encoding="utf-8")[-500000:] if path.exists() else ""
    atomic_write(path, old + "\n" + time.ctime() + "\n" + traceback.format_exc())
