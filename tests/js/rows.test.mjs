import { test } from "node:test";
import assert from "node:assert/strict";
import { allLine, idRows } from "../../herdr-app/ids/rows.js";

const SPACES = [{ id: "sp1", name: "work", tabs: [{ id: "tb1", name: "api" }] }];
const CLAUDE = {
  pane: "pn1",
  app: "claude-code",
  status: "working",
  cwd: "/repo/pane",
  program: { agent: true, name: "Claude Code" },
};

test("no focus lists nothing", () => {
  assert.deepEqual(idRows(null, SPACES, [CLAUDE]), []);
});

test("agent pane lists every id with space and tab names as notes", () => {
  const focus = { space: "sp1", tab: "tb1", pane: "pn1", terminal: "t7", cwd: "/repo" };
  assert.deepEqual(idRows(focus, SPACES, [CLAUDE]), [
    ["space", "sp1", "work"],
    ["tab", "tb1", "api"],
    ["pane", "pn1"],
    ["terminal", "t7"],
    ["agent", "claude-code"],
    ["status", "working"],
    ["cwd", "/repo"],
  ]);
});

test("agent falls back to the program name when the agent reports no app", () => {
  const focus = { space: "sp1", tab: "tb1", pane: "pn1", terminal: "t7", cwd: null };
  const rows = idRows(focus, SPACES, [{ ...CLAUDE, app: null }]);
  assert.deepEqual(rows.find(([label]) => label === "agent"), ["agent", "Claude Code"]);
  assert.deepEqual(rows.find(([label]) => label === "cwd"), ["cwd", "/repo/pane"]);
});

test("shell pane has no agent or status row", () => {
  const shell = { pane: "pn2", app: null, status: null, cwd: "/home", program: { agent: false, name: "zsh" } };
  const focus = { space: "sp1", tab: "tb1", pane: "pn2", terminal: "mini/t3", cwd: "/home" };
  assert.deepEqual(
    idRows(focus, SPACES, [shell]).map(([label]) => label),
    ["space", "tab", "pane", "terminal", "cwd"],
  );
});

test("terminal block focus has no pane row", () => {
  const focus = { space: "sp1", tab: "tb1", pane: null, terminal: "t9", cwd: "/x" };
  assert.deepEqual(
    idRows(focus, SPACES, [CLAUDE]).map(([label]) => label),
    ["space", "tab", "terminal", "cwd"],
  );
});

test("all line joins label=value pairs", () => {
  assert.equal(allLine([["space", "sp1", "work"], ["terminal", "t7"]]), "space=sp1 terminal=t7");
});
