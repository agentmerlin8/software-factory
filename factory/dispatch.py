"""Dispatch packages — the universal execution interface (v0).

One deterministic markdown package per role dispatch: role instruction,
inputs pinned at a recorded SHA, expected outputs, stop rules, resume
preamble. Same inputs -> same bytes -> same sha256 (content-addressed).
A human can paste it into any chat; the adapter feeds it to an agent.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

RESUME_PREAMBLE = (
    "RESUME PROTOCOL: First check `git status` and `git log --oneline -5` in "
    "the working repo. Prior artifacts are READ-ONLY. If work is partially "
    "done, continue from where it stopped; do not restart. Make your first "
    "edit within 10 tool calls. If anything needed is missing, STOP and "
    "report — do not invent."
)

STOP_RULES = (
    "- Do NOT touch files outside the declared manifest.\n"
    "- Do NOT write to any state/control repo; you work ONLY in the product repo.\n"
    "- Do NOT merge, force-push, or rewrite main.\n"
    "- If a required input is missing or contradictory, STOP and report.\n"
    "- Max 2 revision loops; after that, escalate (do not spin)."
)


@dataclass
class Package:
    story: str
    role: str
    model: str
    body: str
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        self.sha256 = hashlib.sha256(self.body.encode("utf-8")).hexdigest()

    def write(self, directory: Path, seq: int) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.story}-{self.role}-{seq:02d}.md"
        path.write_text(self.body, encoding="utf-8")
        return path


def seal(*, story: str, role: str, model: str, instruction: str,
         inputs: dict[str, str], expected_outputs: list[str],
         repo: str, sha: str, manifest: list[str]) -> Package:
    """Assemble a deterministic dispatch package.

    `inputs` maps label -> pinned content (story text, design slice, ...).
    Order is fixed by sorted keys so the bytes are deterministic.
    """
    lines: list[str] = []
    lines.append(f"# Dispatch package — {story} / {role}")
    lines.append("")
    lines.append(f"- model: `{model}`")
    lines.append(f"- product repo: `{repo}` @ `{sha}`")
    lines.append(f"- schema: 0")
    lines.append("")
    lines.append("## Role instruction")
    lines.append(instruction.strip())
    lines.append("")
    lines.append("## Pinned inputs")
    for label in sorted(inputs):
        lines.append(f"### {label}")
        lines.append("```")
        lines.append(inputs[label].rstrip())
        lines.append("```")
        lines.append("")
    lines.append("## Manifest (files you may touch)")
    for m in manifest:
        lines.append(f"- `{m}`")
    lines.append("")
    lines.append("## Expected outputs")
    for o in expected_outputs:
        lines.append(f"- {o}")
    lines.append("")
    lines.append("## Stop rules")
    lines.append(STOP_RULES)
    lines.append("")
    lines.append("## Resume preamble")
    lines.append(RESUME_PREAMBLE)
    lines.append("")
    body = "\n".join(lines)
    return Package(story=story, role=role, model=model, body=body)