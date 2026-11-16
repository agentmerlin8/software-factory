"""Security gate tests — SEC-GATE, calibrated on DSH-1's real review history.

Each check must FAIL on the actual defective head that Copilot/cross-family
caught, and PASS on the fixed head. Network-surface detection is
discovery-driven: only code that binds/serves gets the network checks.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.security import (
    detects_network_surface, check_host_validation, check_loopback_bind,
    check_path_traversal_guard, check_json_strictness, check_error_path_leak,
    check_head_no_body, security_gate, SecurityResult,
)

DASH = Path("/home/merlin/.hermes/cache/scratch/factory-exp/factory-dashboard")


def _server_at(sha):
    import subprocess
    if not DASH.exists():
        return None
    p = subprocess.run(["git", "show", f"{sha}:server.py"], cwd=DASH,
                       capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


# --- network surface detection ---

def test_detects_http_server():
    assert detects_network_surface("from http.server import HTTPServer\nx=1") is True

def test_detects_socket_bind():
    assert detects_network_surface("import socket\ns.bind(('0.0.0.0', 80))") is True

def test_no_network_in_pure_ui():
    assert detects_network_surface("export function Card(){return <div/>}") is False

def test_no_network_in_pure_logic():
    assert detects_network_surface("def add(a,b): return a+b") is False


# --- Host validation (DSH-1 round 3: DNS rebinding) ---

def test_host_validation_present_passes():
    code = 'def do_GET(self):\n    if not self._host_allowed():\n        return\n    host = self.headers.get("Host")'
    assert check_host_validation(code).passed is True

def test_host_validation_absent_fails():
    code = 'def do_GET(self):\n    parsed = urlparse(self.path)\n    self._runs()'
    r = check_host_validation(code)
    assert r.passed is False
    assert any("Host" in f for f in r.failures)


# --- loopback bind ---

def test_loopback_bind_passes():
    assert check_loopback_bind('ThreadingHTTPServer(("127.0.0.1", port), h)').passed is True

def test_wildcard_bind_fails():
    r = check_loopback_bind('HTTPServer(("0.0.0.0", port), h)')
    assert r.passed is False

def test_empty_bind_fails():
    r = check_loopback_bind('HTTPServer(("", port), h)')
    assert r.passed is False


# --- path traversal guard ---

def test_traversal_guard_passes():
    code = 'if not RUN_ID_RE.fullmatch(run): return\nledger = (runs/run).resolve()\nif not ledger.is_relative_to(runs_dir): return'
    assert check_path_traversal_guard(code).passed is True

def test_traversal_no_guard_fails():
    code = 'ledger = runs_dir / run / "ledger.jsonl"\nrows = read(ledger)'
    r = check_path_traversal_guard(code)
    assert r.passed is False


# --- JSON strictness (DSH-1 round 4: non-finite) ---

def test_json_strict_hooks_pass():
    code = 'json.loads(line, parse_constant=_reject, parse_float=_no_overflow)'
    assert check_json_strictness(code).passed is True

def test_json_naive_loads_fails():
    code = 'rows.append(json.loads(line))'
    r = check_json_strictness(code)
    assert r.passed is False


# --- error path leak (DSH-1 rounds 1-2) ---

def test_error_redaction_passes():
    code = 'def _rel_error(self, e):\n    return e.replace(str(self.factory_root), "")\nexcept OSError as exc:\n    self._send_json(200, {"error": self._rel_error(f"{path}: {exc}")})'
    assert check_error_path_leak(code).passed is True

def test_error_raw_path_fails():
    code = 'except OSError as exc:\n    self._send_json(200, {"error": f"{path}: {exc}"})'
    r = check_error_path_leak(code)
    assert r.passed is False


# --- HEAD no body (DSH-1 round 6) ---

def test_head_no_body_pass():
    code = 'if self.command != "HEAD":\n    self.wfile.write(body)'
    assert check_head_no_body(code).passed is True

def test_head_writes_body_fails():
    code = 'self.end_headers()\nself.wfile.write(body)'
    r = check_head_no_body(code)
    assert r.passed is False


# --- integration: real DSH-1 heads ---

def test_real_defective_head_fails():
    # df6ffaf = original coder output (pre round-1 fixes): no Host check,
    # naive json.loads, raw path errors.
    code = _server_at("df6ffaf")
    if code is None:
        return
    r = security_gate(code)
    assert r.passed is False
    assert len(r.failures) >= 3

def test_real_fixed_head_passes():
    code = _server_at("ebc6323")
    if code is None:
        return
    r = security_gate(code)
    assert r.passed is True, r.failures

def test_non_network_code_skips_network_checks():
    r = security_gate("export function Card(){return <div/>}")
    assert r.passed is True
    assert r.network_surface is False
