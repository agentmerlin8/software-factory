"""Announcement-coverage tests — the REAL round-5 regression."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.announcements import check_file, check_tree

REPO = Path.home() / ".hermes/cache/scratch/factory-exp/todo-demo"

ERROR_ONLY = '''
export default function App() {
  const [tasks, setTasks] = useState([]);
  function submit() { const t = addTask(title); setTasks([...tasks, t]); }
  return <p role={failed ? "alert" : undefined}>{hint}</p>;
}
'''

NO_REGION = '''
export default function App() {
  const [tasks, setTasks] = useState([]);
  function submit() { const t = addTask(title); setTasks([...tasks, t]); }
  return <ul>{tasks.map(t => <li key={t.id}>{t.title}</li>)}</ul>;
}
'''

EMPTY_REGION = '''
export default function App() {
  const [tasks, setTasks] = useState([]);
  function submit() { const t = addTask(title); setTasks([...tasks, t]); }
  return <p role="status" aria-live="polite"></p>;
}
'''

FIXED = '''
export default function App() {
  const [tasks, setTasks] = useState([]);
  const [announcement, setAnnouncement] = useState("");
  function submit() {
    const t = addTask(title);
    setTasks([...tasks, t]);
    setAnnouncement(`Added ${t.title}.`);
  }
  return <p role="status" aria-live="polite" aria-atomic="true">{announcement}</p>;
}
'''

PURE = '''
export default function Static() { return <h1>Hello</h1>; }
'''


def test_error_only_announcement_is_flagged(tmp_path):
    p = tmp_path / "App.tsx"; p.write_text(ERROR_ONLY)
    r = check_file(p)
    assert not r.passed
    assert "ASSERTIVE" in r.named_failures()


def test_no_live_region_is_flagged(tmp_path):
    p = tmp_path / "App.tsx"; p.write_text(NO_REGION)
    r = check_file(p)
    assert not r.passed
    assert "NO live region" in r.named_failures()


def test_empty_live_region_is_flagged(tmp_path):
    p = tmp_path / "App.tsx"; p.write_text(EMPTY_REGION)
    r = check_file(p)
    assert not r.passed
    assert "nothing feeds it" in r.named_failures()


def test_fixed_version_passes(tmp_path):
    p = tmp_path / "App.tsx"; p.write_text(FIXED)
    assert check_file(p).passed


def test_non_mutating_component_is_clean(tmp_path):
    p = tmp_path / "Static.tsx"; p.write_text(PURE)
    assert check_file(p).passed


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_round5_prefix_is_flagged(tmp_path):
    old = subprocess.run(["git", "show", "259eceb:src/App.tsx"], cwd=REPO,
                         capture_output=True, text=True)
    if old.returncode != 0:
        pytest.skip("commit unavailable")
    p = tmp_path / "App.tsx"; p.write_text(old.stdout)
    r = check_file(p)
    assert not r.passed, "the pre-fix App must be flagged"


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_fixed_app_passes():
    r = check_file(REPO / "src" / "App.tsx")
    assert r.passed, r.named_failures()


STALE_ALERT = '''
export default function App() {
  const [rejected, setRejected] = useState(false);
  const [storageFailed, setStorageFailed] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  function handleDelete(id: string) {
    try {
      const result = deleteTask(id);
      setTasks(result.tasks);
      setStorageFailed(false);
      setAnnouncement(`Deleted.`);
    } catch {
      setRejected(false);
      setStorageFailed(true);
    }
  }
  return (
    <div>
      <p role="status" aria-live="polite">{announcement}</p>
      <p role={rejected || storageFailed ? "alert" : undefined}>{hint}</p>
    </div>
  );
}
'''


def test_stale_alert_flag_on_success_is_flagged(tmp_path):
    # TOD-4 round-1 class: the failure path clears `rejected` but the
    # SUCCESS path does not — a stale assertive alert survives a delete.
    p = tmp_path / "App.tsx"; p.write_text(STALE_ALERT)
    r = check_file(p)
    assert not r.passed
    assert any("handleDelete" in f and "rejected" in f for f in r.failures)


def test_stale_alert_flag_cleared_on_success_passes(tmp_path):
    p = tmp_path / "App.tsx"
    p.write_text(STALE_ALERT.replace(
        "setStorageFailed(false);\n      setAnnouncement",
        "setStorageFailed(false);\n      setRejected(false);\n      setAnnouncement"))
    r = check_file(p)
    assert r.passed, r.named_failures()


def test_no_conditional_alert_no_flag_requirement(tmp_path):
    # A component with only a polite region imposes no alert-flag duty.
    p = tmp_path / "App.tsx"; p.write_text(FIXED)
    assert check_file(p).passed


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_tod4_prefix_stale_alert_is_flagged(tmp_path):
    old = subprocess.run(["git", "show", "3d558e8:src/App.tsx"], cwd=REPO,
                         capture_output=True, text=True)
    if old.returncode != 0:
        pytest.skip("commit unavailable")
    p = tmp_path / "App.tsx"; p.write_text(old.stdout)
    r = check_file(p)
    assert not r.passed, "the pre-fix TOD-4 App must be flagged"
    assert any("handleDelete" in f for f in r.failures)
    assert any("handleToggle" in f for f in r.failures)