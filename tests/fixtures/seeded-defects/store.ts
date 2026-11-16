// FIXTURE with 10 PLANTED defects for reviewer calibration (SKEL-5 MEA-3).
// Ground truth: factory/calibration.py SEEDED_DEFECTS. Do not "fix" these —
// they are the calibration targets. Reviewers must FIND them.

export interface Task { id: string; title: string; completed: boolean; createdAt: number; }
const KEY = "tasks";

// SD-03 (untrusted-boundary): isTask accepts empty-string title.
function isTask(v: unknown): v is Task {
  if (typeof v !== "object" || v === null) return false;
  const t = v as Record<string, unknown>;
  return typeof t.id === "string" && typeof t.title === "string"
    && typeof t.completed === "boolean" && typeof t.createdAt === "number";
}

export function loadTasks(): Task[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isTask);
  } catch { return []; }
}

// SD-01 (concurrency-lost-update): reads ONCE, writes from stale snapshot.
// No write-boundary re-read; a concurrent tab's commit is clobbered.
export function addTask(title: string): Task[] {
  const current = loadTasks();           // single read
  const task: Task = { id: String(Date.now()), title, completed: false, createdAt: Date.now() };
  const next = [...current, task];       // merges against stale current
  localStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

export function toggleTask(id: string): Task[] {
  const current = loadTasks();           // SD-01 again: stale snapshot
  const next = current.map(t => t.id === id ? { ...t, completed: !t.completed } : t);
  localStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

// SD-10 (state-integrity): completed filter uses wrong predicate (>= instead of ===),
// off-by-one lets an active task slip into the completed view.
export function filterTasks(tasks: Task[], filter: "all" | "active" | "completed"): Task[] {
  if (filter === "active") return tasks.filter(t => !t.completed);
  if (filter === "completed") return tasks.filter(t => t.completed || t.createdAt >= 0);
  return tasks;
}
