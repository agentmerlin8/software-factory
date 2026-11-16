// FIXTURE: planted defects SD-02 (self-certifying test) and SD-09 (test-gap).
import { describe, it, expect, beforeEach } from "vitest";
import { loadTasks, addTask, filterTasks } from "./store";

beforeEach(() => localStorage.clear());

// SD-02 (self-certifying-test): payload led by null throws into loadTasks'
// outer catch, masking a missing per-entry guard — passes even on defect.
describe("corrupt storage", () => {
  it("renders empty on malformed entries", () => {
    localStorage.setItem("tasks", "[null, {}, 42]");
    expect(loadTasks()).toEqual([]);
  });
});

// SD-09 (test-gap): asserts COUNT but not the newest-first ORDERING AC.
describe("list tasks", () => {
  it("shows the right number of tasks", () => {
    addTask("a"); addTask("b"); addTask("c");
    expect(loadTasks().length).toBe(3);  // never checks order
  });
});

describe("filter", () => {
  it("completed filter returns completed tasks", () => {
    const tasks = [
      { id: "1", title: "a", completed: true, createdAt: 1 },
      { id: "2", title: "b", completed: false, createdAt: 2 },
    ];
    // asserts non-empty, not that ONLY completed tasks are returned (SD-10 hides here)
    expect(filterTasks(tasks, "completed").length).toBeGreaterThan(0);
  });
});
