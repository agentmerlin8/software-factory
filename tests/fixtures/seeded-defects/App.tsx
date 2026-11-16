// FIXTURE: planted defects SD-04 (silent mutation), SD-05 (stale live-region),
// SD-08 (unhandled IO failure). React component for the to-do fixture.
import React, { useState } from "react";
import { addTask, toggleTask, loadTasks, filterTasks, Task } from "./store";

export default function App() {
  const [tasks, setTasks] = useState<Task[]>(loadTasks());
  const [title, setTitle] = useState("");
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [announcement, setAnnouncement] = useState("");

  function handleAdd() {
    const next = addTask(title);
    setTasks(next);
    setTitle("");
    // SD-05 (stale-live-region): same-title adds produce IDENTICAL text —
    // no count/sequence, so the second add never re-announces.
    setAnnouncement(`Added ${title}.`);
  }

  function handleToggle(id: string) {
    try {
      const next = toggleTask(id);
      setTasks(next);
    } catch {
      // SD-08 (unhandled-io-failure): storage write failure swallowed —
      // no alert, no revert, user sees nothing wrong.
    }
  }

  function handleDelete(id: string) {
    const next = tasks.filter(t => t.id !== id);
    localStorage.setItem("tasks", JSON.stringify(next));
    setTasks(next);
    // SD-04 (silent-mutation): successful delete updates the list but
    // announces NOTHING to screen readers (no setAnnouncement here).
  }

  const visible = filterTasks(tasks, filter);
  return (
    <main>
      <input value={title} onChange={e => setTitle(e.target.value)} aria-label="New task" />
      <button onClick={handleAdd}>Add</button>
      <p role="status" aria-live="polite">{announcement}</p>
      <ul>
        {visible.map(t => (
          <li key={t.id}>
            <input type="checkbox" checked={t.completed} onChange={() => handleToggle(t.id)} aria-label={t.title} />
            <span>{t.title}</span>
            <button onClick={() => handleDelete(t.id)} aria-label={`Delete ${t.title}`}>x</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
