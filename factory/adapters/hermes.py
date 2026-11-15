"""Hermes adapter — the one v1 execution binding.

Runs a sealed dispatch package headless via `hermes -z`, harvests the usage
JSON, and returns a DispatchResult. The adapter runs ONLY in the product
repo; it never receives state-repo write credentials (OC-14).

Verified invocation (2026-11-14):
    hermes --usage-file <path> -z <package-text> -m <model> -t <toolsets> \
        --in <workdir> --yolo
`--usage-file` is a TOP-LEVEL flag and only writes in `-z` one-shot mode.
The package text goes via argv (Linux limit ~2MB; packages are ~10-50KB).
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

# Linux ARG_MAX is ~2MB per argument; refuse oversized packages loudly.
MAX_PACKAGE_BYTES = 1_500_000


class AdapterError(RuntimeError):
    """The dispatch could not be launched."""


@dataclass
class DispatchResult:
    exit_code: int
    stdout: str
    stderr: str
    wall_s: float
    usage: dict = field(default_factory=dict)
    usage_path: Path | None = None

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def tokens(self) -> dict:
        u = self.usage
        return {"in": u.get("input_tokens", 0),
                "out": u.get("output_tokens", 0)}

    @property
    def model(self) -> str | None:
        return self.usage.get("model")

    @property
    def cost_usd(self) -> float | None:
        c = self.usage.get("estimated_cost_usd")
        return float(c) if c is not None else None


def build_command(package_text: str, model: str, workdir: Path,
                  usage_path: Path, toolsets: str = "terminal,file") -> list[str]:
    return [
        "hermes",
        "--usage-file", str(usage_path),
        "-z", package_text,
        "-m", model,
        "-t", toolsets,
        "--in", str(workdir),
        "--yolo",
    ]


def run(package_path: Path, *, model: str, workdir: Path,
        usage_path: Path, toolsets: str = "terminal,file",
        timeout_s: int = 900) -> DispatchResult:
    """Execute one dispatch. Returns result + harvested usage."""
    package_path = Path(package_path)
    workdir = Path(workdir)
    usage_path = Path(usage_path)

    text = package_path.read_text(encoding="utf-8")
    if len(text.encode("utf-8")) > MAX_PACKAGE_BYTES:
        raise AdapterError(
            f"package {package_path.name} exceeds {MAX_PACKAGE_BYTES} bytes; "
            "split the dispatch")
    usage_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_command(text, model, workdir, usage_path, toolsets)
    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout_s, cwd=str(workdir))
        wall = time.monotonic() - start
        exit_code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        wall = time.monotonic() - start
        exit_code = 124
        stdout = exc.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        stderr = f"TIMEOUT after {timeout_s}s"

    usage: dict = {}
    if usage_path.exists():
        try:
            usage = json.loads(usage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            usage = {}

    return DispatchResult(exit_code=exit_code, stdout=stdout, stderr=stderr,
                          wall_s=wall, usage=usage, usage_path=usage_path)