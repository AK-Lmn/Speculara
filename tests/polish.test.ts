import test from "node:test";
import assert from "node:assert/strict";
import { moduleInfo, updatedLabel, priorityLabel } from "../src/polish.ts";
import type { Analysis } from "../src/analysis.ts";
const a = {
  schema_version: 2,
  source_kind: "synthetic",
  rows: 3,
  columns: ["views"],
  metrics: ["views"],
  totals: { views: 100 },
  missing: {},
  warnings: [],
  charts: {},
  ratios: {},
  periods: {},
  rankings: { categories: {}, posts: {} },
  correlation: [],
  predict: { available: false, reason: "Need daily dates" },
  sentiment: { available: false, reason: "Need text" },
  demand: { available: false, reason: "Need signals" },
  recommend: [
    { title: "Add more useful data", evidence: "3 entries", action: "Add dated counts." },
  ],
} satisfies Analysis;
test("module states and takeaways reflect available evidence", () => {
  assert.equal(moduleInfo("charts", null).status, "Waiting for data");
  assert.equal(moduleInfo("charts", a).status, "Ready");
  assert.match(moduleInfo("charts", a).finding, /100 views/);
  assert.equal(moduleInfo("sentiment", a).status, "Needs data");
  assert.match(moduleInfo("sentiment", a).needed!, /comments or reviews/);
  assert.equal(moduleInfo("predict", a).status, "Needs data");
  assert.match(moduleInfo("predict", a).needed!, /14.*365/);
  const p = {
    a: "views",
    b: "sales",
    r: -0.8,
    n: 4,
    p: 0.1,
    spearman_r: -0.8,
    spearman_p: 0.1,
    small_sample: true,
  };
  assert.equal(moduleInfo("correlation", { ...a, correlation: [p] }).status, "Early finding");
  assert.match(moduleInfo("correlation", { ...a, correlation: [p] }).finding, /lower/);
});
test("freshness and priorities describe analysis time and suggested order only", () => {
  assert.equal(updatedLabel(1000, 1001), "Updated just now");
  assert.equal(updatedLabel(1000, 61000), "Updated 1 minute ago");
  assert.equal(priorityLabel(0), "Start here");
  assert.equal(priorityLabel(1), "Try next");
  assert.equal(priorityLabel(3), "Also consider");
});
