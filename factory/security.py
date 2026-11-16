"""Security gate — SEC-GATE (deterministic, discovery-driven, risk-tiered).

Closes the computable security/protocol classes that DSH-1 discovered one
at a time across 6 review rounds (DNS rebinding, path leaks, non-finite
JSON, HTTP method semantics, HEAD bodies). Each check is calibrated
fail-before/pass-after on DSH-1's real defective heads.

Network checks activate ONLY when the code binds/serves (discovery-driven
risk tiering, MEA-2): pure UI/logic skips them. The adversarial reviewer
remains the backstop for novel classes no checklist enumerates.

Checks (network surface):
  host-validation   — Host header checked against trusted authorities
  loopback-bind     — server binds 127.0.0.1/localhost, not 0.0.0.0/""
  traversal-guard   — path params validated + resolved-path containment
  json-strictness   — parse_constant/parse_float hooks reject non-finite
  error-path-leak   — error responses redact absolute source paths
  head-no-body      — HEAD responses suppress the body
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class SecurityResult:
    passed: bool
    failures: list[str] = field(default_factory=list)
    network_surface: bool = False

    def named_failures(self) -> str:
        return "; ".join(self.failures) if self.failures else "none"


_NETWORK = re.compile(
    r"(http\.server|HTTPServer|BaseHTTPRequestHandler|socket\.socket|"
    r"\.bind\(|\.listen\(|ThreadingHTTPServer|flask|fastapi|aiohttp\.web|"
    r"express\(\)|createServer|app\.listen)", re.I)


def detects_network_surface(code: str) -> bool:
    return bool(_NETWORK.search(code))


def check_host_validation(code: str) -> SecurityResult:
    """DNS-rebinding defense: the Host header must be validated."""
    has_host_read = re.search(r'headers\.get\(\s*["\']Host["\']|\.headers\[["\']Host', code)
    has_check = re.search(r'_host_allowed|host.*(allow|valid|trust|loopback)|allowed_hosts', code, re.I)
    if has_host_read and has_check:
        return SecurityResult(True)
    return SecurityResult(False, [
        "host-validation: server reads requests but never validates the Host "
        "header — DNS-rebinding exposure (DSH-1 round-3 class)"])


def check_loopback_bind(code: str) -> SecurityResult:
    """Server must bind loopback, not wildcard/empty."""
    binds = re.findall(r'(?:HTTPServer|ThreadingHTTPServer|\.bind\()\s*\(\s*\(\s*["\']([^"\']*)["\']', code)
    if not binds:
        return SecurityResult(True)  # no explicit bind found; nothing to flag
    bad = [b for b in binds if b in ("0.0.0.0", "", "::", "*")]
    if bad:
        return SecurityResult(False, [
            f"loopback-bind: server binds {bad!r} — must bind 127.0.0.1/localhost "
            "for a local-only data service"])
    return SecurityResult(True)


def check_path_traversal_guard(code: str) -> SecurityResult:
    """Path parameters need a name guard AND resolved-path containment."""
    uses_path_param = re.search(r'/\s*run|/\s*path|joinpath|/\s*\w+\s*/\s*["\'].*\.jsonl', code)
    if not uses_path_param:
        return SecurityResult(True)
    has_name_guard = re.search(r'fullmatch|RUN_ID_RE|re\.match.*run|invalid run id', code)
    has_containment = re.search(r'is_relative_to|\.resolve\(\).*startswith|commonpath', code)
    failures = []
    if not has_name_guard:
        failures.append("traversal-guard: path parameter used without a name-pattern guard")
    if not has_containment:
        failures.append("traversal-guard: no resolved-path containment check (is_relative_to)")
    return SecurityResult(not failures, failures)


def check_json_strictness(code: str) -> SecurityResult:
    """JSON parsing of untrusted files must reject non-finite values."""
    if not re.search(r'json\.loads|json\.load\(', code):
        return SecurityResult(True)
    has_hooks = re.search(r'parse_constant|parse_float', code)
    if has_hooks:
        return SecurityResult(True)
    return SecurityResult(False, [
        "json-strictness: json.loads on untrusted source without "
        "parse_constant/parse_float hooks — NaN/Infinity/overflow produce "
        "invalid JSON responses (DSH-1 round-4 class)"])


def check_error_path_leak(code: str) -> SecurityResult:
    """Error responses must redact absolute source paths."""
    sends_error = re.search(r'["\']error["\']\s*:', code)
    if not sends_error:
        return SecurityResult(True)
    has_redaction = re.search(r'_rel_error|replace\(.*factory_root|replace\(.*root|relative_to.*error|redact', code, re.I)
    if has_redaction:
        return SecurityResult(True)
    return SecurityResult(False, [
        "error-path-leak: error responses built from raw paths/exceptions "
        "without redaction — absolute filesystem paths leak (DSH-1 round-1/2 class)"])


def check_head_no_body(code: str) -> SecurityResult:
    """HEAD responses must not write a body."""
    writes_body = re.search(r'wfile\.write|self\.write\(|response\.write', code)
    if not writes_body:
        return SecurityResult(True)
    guards_head = re.search(r'command\s*!=\s*["\']HEAD["\']|command\s*==\s*["\']HEAD["\']|method\s*!=\s*["\']HEAD|HEAD.*no.body|if.*HEAD', code, re.I)
    if guards_head:
        return SecurityResult(True)
    return SecurityResult(False, [
        "head-no-body: response body written without a HEAD guard — RFC 7231 "
        "forbids bodies on HEAD (DSH-1 round-6 class)"])


_NETWORK_CHECKS = (
    check_host_validation, check_loopback_bind, check_path_traversal_guard,
    check_json_strictness, check_error_path_leak, check_head_no_body,
)


def security_gate(code: str) -> SecurityResult:
    """Run the security gate on a source file. Network checks only when the
    code has network surface (risk-tiered, discovery-driven)."""
    if not detects_network_surface(code):
        return SecurityResult(True, network_surface=False)
    failures = []
    for check in _NETWORK_CHECKS:
        r = check(code)
        failures.extend(r.failures)
    return SecurityResult(not failures, failures, network_surface=True)


def check_tree(root, glob: str = "server.py") -> SecurityResult:
    """Scan matching files under root (default: server.py at the top)."""
    from pathlib import Path
    failures = []
    any_network = False
    for p in Path(root).glob(glob):
        r = security_gate(p.read_text(encoding="utf-8"))
        any_network = any_network or r.network_surface
        failures.extend(f"{p.name}: {f}" for f in r.failures)
    return SecurityResult(not failures, failures, network_surface=any_network)
