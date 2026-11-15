import React, { useState } from 'react';

export interface Task { id: string; title: string; completed: boolean; createdAt: number; }

const MOCK: Task[] = [
  { id: '3', title: 'Call the plumber', completed: false, createdAt: 3 },
  { id: '1', title: 'Buy oat milk', completed: false, createdAt: 1 },
  { id: '2', title: 'Write the intake PRD', completed: true, createdAt: 2 },
];
// Newest-first by createdAt (the PRD ordering requirement).
const newestFirst = (ts: Task[]) => [...ts].sort((a, b) => b.createdAt - a.createdAt);

/** Screen 1 — add a task (input + Add button). */
export function AddTask() {
  const [value, setValue] = useState('');
  return (
    <div className="wf-card">
      <h1 className="wf-title">To-Do</h1>
      <p className="wf-sub">Small steps, written down.</p>
      <div className="wf-row">
        <input className="wf-input" placeholder="What needs doing?"
          value={value} onChange={(e) => setValue(e.target.value)} aria-label="New task" />
        <button className="wf-btn" type="button">Add</button>
      </div>
      <p className="wf-count">Press Enter or hit Add. Everything stays in this browser.</p>
    </div>
  );
}

/** Screen 2 — list tasks (newest-first, count, empty state). */
export function TaskList({ empty = false }: { empty?: boolean }) {
  const tasks = empty ? [] : newestFirst(MOCK);
  return (
    <div className="wf-card">
      <h1 className="wf-title">To-Do</h1>
      <p className="wf-count">{tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}</p>
      {tasks.length === 0 ? (
        <p className="wf-empty">Nothing here yet — add your first task above.</p>
      ) : (
        <ul className="wf-list">
          {tasks.map((t) => (
            <li key={t.id} className={`wf-item${t.completed ? ' done' : ''}`}>
              <input type="checkbox" defaultChecked={t.completed} aria-label={t.title} />
              <span className="wf-label">{t.title}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/** Screen 3 — complete / uncomplete (strikethrough on done). */
export function ToggleTask() {
  const [tasks, setTasks] = useState(MOCK);
  const toggle = (id: string) =>
    setTasks((ts) => ts.map((t) => t.id === id ? { ...t, completed: !t.completed } : t));
  return (
    <div className="wf-card">
      <h1 className="wf-title">To-Do</h1>
      <ul className="wf-list">
        {tasks.map((t) => (
          <li key={t.id} className={`wf-item${t.completed ? ' done' : ''}`}>
            <input type="checkbox" checked={t.completed} onChange={() => toggle(t.id)} aria-label={t.title} />
            <span className="wf-label">{t.title}</span>
          </li>
        ))}
      </ul>
      <p className="wf-count">Tap a checkbox to complete; tap again to undo.</p>
    </div>
  );
}

/** Screen 4 — delete a task. */
export function DeleteTask() {
  const [tasks, setTasks] = useState(MOCK);
  return (
    <div className="wf-card">
      <h1 className="wf-title">To-Do</h1>
      <ul className="wf-list">
        {tasks.map((t) => (
          <li key={t.id} className={`wf-item${t.completed ? ' done' : ''}`}>
            <input type="checkbox" defaultChecked={t.completed} aria-label={t.title} />
            <span className="wf-label">{t.title}</span>
            <button className="wf-del" type="button" aria-label={`Delete ${t.title}`}
              onClick={() => setTasks((ts) => ts.filter((x) => x.id !== t.id))}>✕</button>
          </li>
        ))}
      </ul>
      <p className="wf-count">{tasks.length} {tasks.length === 1 ? 'task' : 'tasks'} left.</p>
    </div>
  );
}

/** Screen 5 — filter view (All / Active / Completed). */
export function FilterView() {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const visible = newestFirst(MOCK).filter((t) =>
    filter === 'all' ? true : filter === 'active' ? !t.completed : t.completed);
  const emptyMsg = filter === 'active' ? 'No active tasks — everything is done.'
    : filter === 'completed' ? 'No completed tasks yet.'
    : 'Nothing here yet — add your first task above.';
  return (
    <div className="wf-card">
      <h1 className="wf-title">To-Do</h1>
      <div className="wf-filters" role="group" aria-label="Filter tasks">
        {(['all', 'active', 'completed'] as const).map((f) => (
          <button key={f} className="wf-filter" type="button" aria-pressed={filter === f}
            onClick={() => setFilter(f)}>{f[0].toUpperCase() + f.slice(1)}</button>
        ))}
      </div>
      {visible.length === 0 ? (
        <p className="wf-empty">{emptyMsg}</p>
      ) : (
        <ul className="wf-list">
          {visible.map((t) => (
            <li key={t.id} className={`wf-item${t.completed ? ' done' : ''}`}>
              <input type="checkbox" defaultChecked={t.completed} aria-label={t.title} />
              <span className="wf-label">{t.title}</span>
            </li>
          ))}
        </ul>
      )}
      <p className="wf-count">{visible.length} shown.</p>
    </div>
  );
}

/** Screen 6 — composite: add + toggle + delete + filter wired together. */
export function FullApp() {
  const [tasks, setTasks] = useState<Task[]>(MOCK);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [value, setValue] = useState('');
  const add = () => {
    const title = value.trim();
    if (!title) return;
    setTasks((ts) => [...ts, { id: String(Date.now()), title, completed: false, createdAt: Date.now() }]);
    setValue('');
  };
  const toggle = (id: string) =>
    setTasks((ts) => ts.map((t) => t.id === id ? { ...t, completed: !t.completed } : t));
  const del = (id: string) => setTasks((ts) => ts.filter((t) => t.id !== id));
  const visible = newestFirst(tasks).filter((t) =>
    filter === 'all' ? true : filter === 'active' ? !t.completed : t.completed);
  return (
    <div className="wf-card">
      <h1 className="wf-title">To-Do</h1>
      <div className="wf-row">
        <input className="wf-input" placeholder="What needs doing?" value={value}
          onChange={(e) => setValue(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && add()}
          aria-label="New task" />
        <button className="wf-btn" type="button" onClick={add}>Add</button>
      </div>
      <div className="wf-filters" role="group" aria-label="Filter tasks">
        {(['all', 'active', 'completed'] as const).map((f) => (
          <button key={f} className="wf-filter" type="button" aria-pressed={filter === f}
            onClick={() => setFilter(f)}>{f[0].toUpperCase() + f.slice(1)}</button>
        ))}
      </div>
      {visible.length === 0 ? (
        <p className="wf-empty">Nothing to show here.</p>
      ) : (
        <ul className="wf-list">
          {visible.map((t) => (
            <li key={t.id} className={`wf-item${t.completed ? ' done' : ''}`}>
              <input type="checkbox" checked={t.completed} onChange={() => toggle(t.id)} aria-label={t.title} />
              <span className="wf-label">{t.title}</span>
              <button className="wf-del" type="button" aria-label={`Delete ${t.title}`} onClick={() => del(t.id)}>✕</button>
            </li>
          ))}
        </ul>
      )}
      <p className="wf-count">{visible.length} shown · {tasks.length} total.</p>
    </div>
  );
}
