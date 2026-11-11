import test from "node:test";
import assert from "node:assert/strict";
import { answer, analysisReport, type Analysis } from "../src/analysis.ts";
const a = {
  schema_version: 2,
  source_kind: "uploaded",
  columns: ["views", "sales"],
  metrics: ["views", "sales"],
  missing: {},
  charts: {},
  ratios: {},
  periods: {},
  rankings: { categories: {}, posts: {} },
  rows: 2,
  totals: { views: 300, sales: 6 },
  warnings: ["Missing values excluded."],
  correlation: [],
  predict: { available: false, reason: "Need 14 dates." },
  sentiment: { available: false, reason: "Need text." },
  demand: { available: false, reason: "Need signals." },
  recommend: [
    { title: "Test checkout", evidence: "6 sales / 300 views", action: "Change one variable." },
  ],
} satisfies Analysis;

test("chat reports measured totals and handles unsupported questions", () => {
  assert.match(answer("Total views?", a), /300 views/);
  assert.match(answer("Who won the election?", a), /cannot fetch accounts/);
  assert.match(answer("Forecast accuracy?", a), /14 days/);
  assert.match(answer("Sentiment?", a), /comments or reviews/);
  assert.match(answer("What should I do next?", a), /6 sales \/ 300 views/);
});
test("report preserves source, decisions, limits and full results", () => {
  const report = analysisReport(a, "SYNTHETIC DEMO");
  for (const text of [
    "SYNTHETIC DEMO",
    "300",
    "6 sales / 300 views",
    "Missing values excluded.",
    "Need 14 dates.",
    "Full computed results",
    "zero-view",
    "1,000",
    "14 UTC",
    "n<10",
    "last_value",
    "holdout",
    "lexicon",
    "uplift",
  ])
    assert.ok(report.includes(text));
});

// Schema-v2 intent contract: these assertions precede implementation.
test("v2 specific calculation intents precede generic sales/trend matches", () => {
  const v = {
    ...a,
    ratios: {
      sales_per_view: {
        available: true,
        reason: null,
        numerator_metric: "sales",
        denominator_metric: "views",
        numerator: 6,
        denominator: 300,
        percent: 2,
        n: 2,
        excluded_rows: 1,
        zero_view_rows: 0,
        notes: [],
      },
    },
    periods: {
      sales: {
        available: true,
        reason: null,
        current_start: "2026-01-08",
        current_end: "2026-01-14",
        previous_start: "2026-01-01",
        previous_end: "2026-01-07",
        current_total: 6,
        previous_total: 0,
        absolute_change: 6,
        percent_change: null,
        percent_change_reason: "Previous total is zero; percentage change is undefined.",
      },
    },
    rankings: {
      posts: {
        sales_per_view: {
          available: false,
          reason: "Repeated post IDs make snapshots versus increments ambiguous.",
          rows: [],
          excluded_groups: 0,
        },
      },
      categories: {},
    },
    predict: {
      available: true,
      reason: null,
      method: "Daily linear trend. No seasonality or causal model.",
      mae: 0,
      training_days: 14,
      metric: "sales",
      points: [{ label: "2026-01-15", value: 7 }],
      selected_model: "linear",
      evaluation: {
        train_days: 11,
        scores: { linear: 0, last_value: 2 },
        holdout_dates: ["2026-01-12", "2026-01-13", "2026-01-14"],
      },
      notes: [],
    },
    correlation: [
      {
        a: "sales",
        b: "views",
        r: 1,
        spearman_r: 1,
        n: 14,
        p: 0,
        spearman_p: 0,
        small_sample: false,
      },
    ],
  } satisfies Analysis;
  assert.match(answer("technical sales rate", v), /6 sales \/ 300 views/);
  assert.match(answer("technical sales rate", v), /1 excluded/);
  assert.match(
    answer("technical sales growth trend", v),
    /2026-01-01.*2026-01-07.*2026-01-08.*2026-01-14.*zero/s,
  );
  assert.match(answer("technical best post sales", v), /Repeated post IDs/);
  for (const question of ["best post sales", "best category sales", "rank"]) {
    for (const limit of [
      "3 complete positive-view rows",
      "1,000 views",
      "unique nonblank IDs",
      "100 views",
      "Top 10",
      "heuristics",
      "not causal",
    ]) {
      assert.ok(
        answer("technical " + question, v).includes(limit),
        `${question}: missing ${limit}`,
      );
    }
  }
  assert.match(answer("technical forecast", v), /linear.*0.*last_value.*2/s);
  assert.match(answer("technical correlation", v), /Pearson.*Spearman/s);
  for (const heading of ["Ratios", "Period comparisons", "Rankings"])
    assert.ok(analysisReport(v, "fixture").includes(heading));
});

// Available forecasts must carry the complete server payload.
// @ts-expect-error An availability flag alone cannot supply a forecast.
const incompleteForecast: Analysis["predict"] = { available: true, reason: null };
void incompleteForecast;
type AvailableForecast = Extract<Analysis["predict"], { available: true }>;
// @ts-expect-error Evaluation must include the pre-holdout training day count.
const incompleteEvaluation: AvailableForecast["evaluation"] = {
  holdout_dates: [],
  scores: { linear: 0, last_value: 0 },
};
void incompleteEvaluation;
