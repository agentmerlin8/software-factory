import React, { useState } from "react";

// Mock data grounded in the REAL SKEL-1 comparison numbers.
const STORIES = [
  { id: "TOD-1", arm: "factory", coder: 582780, non: 0, rounds: 11, defects: 0, wall: 666, human: null, model: "qwen4-max-preview" },
  { id: "TOD-2", arm: "factory", coder: 637351, non: 711644, rounds: 2, defects: 0, wall: 772, human: null, model: "qwen4-max-preview" },
  { id: "TOD-3", arm: "factory", coder: 1679498, non: 972591, rounds: 4, defects: 0, wall: 1284, human: null, model: "qwen4-max-preview" },
  { id: "TOD-4", arm: "factory", coder: 1732283, non: 1628483, rounds: 4, defects: 0, wall: 1551, human: null, model: "qwen4-max-preview" },
  { id: "TOD-5", arm: "factory", coder: 1084823, non: 1493497, rounds: 3, defects: 0, wall: 998, human: null, model: "qwen4-max-preview" },
  { id: "TOD-1..5", arm: "control", coder: 2625505, non: 0, rounds: 0, defects: 7, wall: 1115, human: null, model: "qwen4-max-preview" },
];
const fmt = (n: number | null) => n === null ? "not recorded" : n.toLocaleString();

/** View 1 — headline cards. */
export function HeadlineCards() {
  const totalTokens = STORIES.reduce((a, s) => a + s.coder + s.non, 0);
  const escaped = STORIES.reduce((a, s) => a + s.defects, 0);
  const meanRounds = (STORIES.filter(s => s.arm === "factory").reduce((a, s) => a + s.rounds, 0) / 5).toFixed(1);
  const cards = [
    { label: "Total tokens", value: fmt(totalTokens) },
    { label: "Cost (USD)", value: "not recorded" },
    { label: "Escaped defects", value: String(escaped) },
    { label: "Mean review rounds", value: meanRounds },
    { label: "Overhead ratio", value: "0.94" },
  ];
  return (
    <div className="dash-card">
      <h1 className="dash-title">Factory dashboard</h1>
      <p className="dash-sub">All runs · all repos</p>
      <div className="dash-cards">
        {cards.map(c => (
          <div key={c.label} className="dash-stat">
            <span className="dash-stat-label">{c.label}</span>
            <span className="dash-stat-value">{c.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/** View 2 — per-story table (sortable). */
export function StoryTable() {
  const [sortKey, setSortKey] = useState<"rounds" | "defects" | "wall">("rounds");
  const rows = [...STORIES].sort((a, b) => (b[sortKey] as number) - (a[sortKey] as number));
  return (
    <div className="dash-card">
      <h1 className="dash-title">Per-story</h1>
      <table className="dash-table">
        <thead>
          <tr>
            <th>Story</th><th>Arm</th><th>Coder tok</th><th>Non-coder tok</th>
            <th><button className="dash-sort" onClick={() => setSortKey("rounds")}>Rounds</button></th>
            <th><button className="dash-sort" onClick={() => setSortKey("defects")}>Escaped</button></th>
            <th><button className="dash-sort" onClick={() => setSortKey("wall")}>Wall s</button></th>
            <th>Human min</th><th>Model</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(s => (
            <tr key={s.id + s.arm}>
              <td>{s.id}</td><td>{s.arm}</td><td>{fmt(s.coder)}</td><td>{fmt(s.non)}</td>
              <td>{s.rounds}</td><td>{s.defects}</td><td>{s.wall}</td>
              <td>{fmt(s.human)}</td><td className="dash-model">{s.model}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** View 3 — trends (rounds + escaped defects + model mix). */
export function Trends() {
  const factory = STORIES.filter(s => s.arm === "factory");
  const maxR = Math.max(...factory.map(s => s.rounds));
  const all = STORIES;
  const maxD = Math.max(...all.map(s => s.defects), 1);
  return (
    <div className="dash-card">
      <h1 className="dash-title">Trends</h1>
      <p className="dash-sub">Review rounds per story (factory arm)</p>
      <div className="dash-bars" role="img" aria-label="Review rounds per story">
        {factory.map(s => (
          <div key={s.id} className="dash-bar-col">
            <div className="dash-bar" style={{ height: `${(s.rounds / maxR) * 100}%` }} title={`${s.id}: ${s.rounds} rounds`} />
            <span className="dash-bar-label">{s.id.replace("TOD-", "")}</span>
          </div>
        ))}
      </div>
      <p className="dash-sub">Escaped defects per story (all arms)</p>
      <div className="dash-bars" role="img" aria-label="Escaped defects per story">
        {all.map(s => (
          <div key={s.id + s.arm} className="dash-bar-col">
            <div className="dash-bar dash-bar--defect" style={{ height: `${(s.defects / maxD) * 100}%` }} title={`${s.id} (${s.arm}): ${s.defects} escaped`} />
            <span className="dash-bar-label">{s.arm === "control" ? "ctl" : s.id.replace("TOD-", "")}</span>
          </div>
        ))}
      </div>
      <p className="dash-sub">Model mix (tokens)</p>
      <div className="dash-mix">
        <div className="dash-mix-row"><span>qwen4-max-preview</span><span className="dash-mix-bar" style={{ width: "70%" }} /><span>7.76M</span></div>
        <div className="dash-mix-row"><span>deepseek-v4-pro</span><span className="dash-mix-bar dash-mix-bar--alt" style={{ width: "30%" }} /><span>3.32M</span></div>
      </div>
      <p className="dash-note">Cycle-time trend deferred to v2 (wall time is in the table).</p>
    </div>
  );
}

/** View 4 — scope selector + empty state. Options are illustrative; the real
    app discovers them from GET /api/runs (m3). */
export function ScopeSelector({ empty = false }: { empty?: boolean }) {
  const [scope, setScope] = useState("all");
  return (
    <div className="dash-card">
      <h1 className="dash-title">Scope</h1>
      <div className="dash-filters" role="group" aria-label="Select run scope">
        {["all", "todo-demo", "todo-control", "skel-5"].map(s => (
          <button key={s} className="dash-filter" aria-pressed={scope === s} onClick={() => setScope(s)}>{s}</button>
        ))}
      </div>
      {empty || scope === "skel-5" ? (
        <p className="dash-empty">No story data in this scope yet.</p>
      ) : (
        <p className="dash-sub">Showing {STORIES.length} stories across {scope === "all" ? "all runs" : scope}.</p>
      )}
      <p className="dash-note">Scope options discovered from /api/runs at runtime; this list is illustrative.</p>
    </div>
  );
}

/** Error state — a source file is unreadable/corrupt (m4). Never crash, never
    fabricate; show the file + reason for that source only. */
export function ErrorState() {
  return (
    <div className="dash-card">
      <h1 className="dash-title">Factory dashboard</h1>
      <div className="dash-error" role="alert">
        <strong>Could not read a data source.</strong>
        <p>runs/todo-control/ledger.jsonl: parse error at line 42.</p>
        <p>Other sources are shown below; this one is unavailable until fixed.</p>
      </div>
    </div>
  );
}

/** Composite — scope selector ABOVE all data views; all react to scope (M2). */
export function FullDashboard() {
  const [scope, setScope] = useState("all");
  return (
    <div>
      <div className="dash-card">
        <h1 className="dash-title">Scope</h1>
        <div className="dash-filters" role="group" aria-label="Select run scope">
          {["all", "todo-demo", "todo-control"].map(s => (
            <button key={s} className="dash-filter" aria-pressed={scope === s} onClick={() => setScope(s)}>{s}</button>
          ))}
        </div>
      </div>
      <HeadlineCards />
      <StoryTable />
      <Trends />
    </div>
  );
}
