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

# Linux MAX_ARG_STRLEN is 128KiB PER ARGUMENT (not the ~2MB ARG_MAX total).
# A 151KB reviewer package died with E2BIG at spawn (TOD-5). Packages above
# the safe inline limit are passed BY REFERENCE: the argv prompt instructs
# the agent to read the sealed package file first. The package on disk stays
# the canonical, content-addressed artifact either way.
MAX_INLINE_BYTES = 100_000
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

    if len(text.encode("utf-8")) > MAX_INLINE_BYTES:
        # By-reference dispatch: argv carries a compact pointer, the agent
        # reads the full sealed package from disk (it has file tools).
        prompt = (
            "Your complete dispatch package is the file "
            f"{package_path.resolve()} — read it FIRST, in full, and follow "
            "it exactly: role instruction, pinned inputs, scope contract, "
            "manifest, stop rules, resume preamble. The pinned inputs are "
            "also embedded in that file; do not skip any section. Begin now.")
    else:
        prompt = text
    cmd = build_command(prompt, model, workdir, usage_path, toolsets)
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