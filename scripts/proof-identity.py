#!/usr/bin/env python3
"""Identity proof for a factory App.

Usage: proof-identity.py <app-dir> <expected-repo> <must-fail-repo|-> <push-target|->

  app-dir        e.g. /home/merlin/.factory-controller
  expected-repo  the ONLY repo the installation token may see
  must-fail-repo repo the token must not be able to write (or '-' to skip)
  push-target    repo URL to attempt a git push --dry-run against (or '-')

Pushes are --dry-run: the server authenticates and decides, nothing is written.
Prints no secret values.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

APP_DIR, EXPECTED, FORBIDDEN, PUSH_TARGET = sys.argv[1:5]
CLONE = "/home/merlin/Work/software-factory"


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def api(path, token=None, bearer=None, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "factory-identity-proof"}
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    elif token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(f"https://api.github.com{path}",
                                 data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raw = e.read()[:200]
        try:
            return e.code, {"message": json.loads(raw)["message"]}
        except Exception:
            return e.code, {"message": raw.decode(errors="replace")}


def app_jwt():
    app_id = open(f"{APP_DIR}/app_id.txt").read().strip()
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    now = int(time.time())
    payload = b64url(json.dumps({"iat": now - 60, "exp": now + 540,
                                 "iss": int(app_id)}).encode())
    with tempfile.NamedTemporaryFile() as f:
        f.write(f"{header}.{payload}".encode())
        f.flush()
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign",
                              f"{APP_DIR}/app.pem", f.name],
                             capture_output=True, check=True).stdout
    return f"{header}.{payload}.{b64url(sig)}"


def push(token, repo):
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_CONFIG_COUNT="1",
               GIT_CONFIG_KEY_0="http.extraheader",
               GIT_CONFIG_VALUE_0=f"Authorization: Basic {basic}")
    return subprocess.run(
        ["git", "-C", CLONE, "push", "--dry-run",
         f"https://github.com/{repo}.git", "HEAD:refs/heads/proof-dryrun"],
        capture_output=True, text=True, env=env, timeout=60)


def main() -> int:
    jwt = app_jwt()
    st, insts = api("/app/installations", bearer=jwt)
    if st != 200 or not insts:
        print(f"FAIL: no installation (HTTP {st})")
        return 3
    inst = [i for i in insts if not i.get("suspended_at")][0]
    print(f"installation {inst['id']} on {inst['account']['login']} "
          f"selection={inst['repository_selection']}")
    st, tok = api(f"/app/installations/{inst['id']}/access_tokens",
                  bearer=jwt, method="POST")
    if st != 201:
        print(f"FAIL: token mint HTTP {st} {tok}")
        return 1
    token = tok["token"]
    print(f"token perms {dict(sorted(tok['permissions'].items()))} "
          f"expires {tok['expires_at']}")

    st, repos = api("/installation/repositories", token=token)
    names = [r["full_name"] for r in repos.get("repositories", [])]
    print(f"repo scope ({repos.get('total_count')}): {names}")
    ok = names == [EXPECTED]
    print(f"{'PASS' if ok else 'FAIL'} scope == [{EXPECTED}]")

    if PUSH_TARGET != "-":
        p = push(token, PUSH_TARGET)
        good = p.returncode == 0
        ok &= good
        tail = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "(ok)"
        print(f"{'PASS' if good else 'FAIL'} push --dry-run {PUSH_TARGET} "
              f"-> rc={p.returncode} {tail[:120]}")

    if FORBIDDEN != "-":
        p = push(token, FORBIDDEN)
        refused = p.returncode != 0 and any(
            s in p.stderr for s in ("403", "404", "denied", "not found"))
        ok &= refused
        print(f"{'PASS' if refused else 'FAIL'} push --dry-run {FORBIDDEN} "
              f"-> rc={p.returncode} (must be refused)")

    print("\nRESULT:", "PASS" if ok else "FAIL — see lines above")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())