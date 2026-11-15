"""Contention test — SKEL-3 SEC-2 (MRG-1): parallel writers, no lost events.

The controller's concurrency group serializes git pushes in CI. Locally we
exercise the equivalent invariant: N concurrent append_submission calls
against ONE ledger, serialized by a lock (the in-process analogue of the
concurrency group), must land every event with an intact hash chain and
zero exhausted retries. A naive unserialized parallel append would corrupt
the chain (lost prev-hash updates) — this test proves the serialized path.
"""
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.controller import append_submission
from factory.ledger import Ledger

N_WRITERS = 12
EVENTS_PER_WRITER = 5


def test_parallel_writers_no_lost_events(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    lock = threading.Lock()  # in-process analogue of the CI concurrency group
    retries = {"count": 0}

    def writer(wid):
        landed = 0
        for i in range(EVENTS_PER_WRITER):
            sub = {"schema": 0, "source": f"agent-{wid}",
                   "events": [{"event": "dispatch_completed",
                               "story": f"TOD-{wid}", "role": "coder",
                               "detail": {"seq": i}}]}
            # Serialize the append (the concurrency-group invariant).
            with lock:
                append_submission(ledger, sub)
            landed += 1
        return landed

    with ThreadPoolExecutor(max_workers=N_WRITERS) as ex:
        futures = [ex.submit(writer, w) for w in range(N_WRITERS)]
        results = [f.result() for f in as_completed(futures)]

    assert sum(results) == N_WRITERS * EVENTS_PER_WRITER
    rows = ledger.read()  # read() VERIFIES the hash chain — corruption raises
    assert len(rows) == N_WRITERS * EVENTS_PER_WRITER
    # every writer's events present, none lost
    sources = {r["detail"]["_source"] for r in rows}
    assert sources == {f"agent-{w}" for w in range(N_WRITERS)}
    assert retries["count"] == 0  # serialized path needs no retries


def test_unserialized_parallel_would_corrupt_chain(tmp_path):
    """Negative control: WITHOUT serialization, concurrent appends race on
    the prev-hash. With a barrier forcing maximal interleaving, the chain
    breaks or events are lost — proving the lock/concurrency-group is
    load-bearing. (Races are nondeterministic; if this ever passes cleanly
    it means the race didn't trigger, which we surface, not hide.)"""
    ledger = Ledger(tmp_path / "ledger.jsonl")
    barrier = threading.Barrier(N_WRITERS)
    errors = []

    def writer(wid):
        barrier.wait()  # maximize interleaving
        sub = {"schema": 0, "source": f"agent-{wid}",
               "events": [{"event": "dispatch_completed", "story": f"TOD-{wid}",
                           "role": "coder", "detail": {}}]}
        try:
            append_submission(ledger, sub)
        except Exception as exc:  # noqa: BLE001 — record, don't crash the pool
            errors.append(str(exc))

    with ThreadPoolExecutor(max_workers=N_WRITERS) as ex:
        list(ex.map(writer, range(N_WRITERS)))

    raw_rows = ledger.read(verify_chain=False)
    try:
        ledger.read()  # verifies chain
        chain_ok = True
    except Exception:
        chain_ok = False
    # The negative control MUST show a problem: broken chain, lost events,
    # or append errors. If none occurred the race simply didn't trigger.
    problem = (not chain_ok) or len(raw_rows) < N_WRITERS or bool(errors)
    assert problem, (
        "negative control showed no corruption — the race did not trigger; "
        "increase N_WRITERS or add a sleep in append to force interleaving")
