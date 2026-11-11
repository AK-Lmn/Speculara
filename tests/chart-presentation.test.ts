import { test } from 'node:test';
import assert from 'node:assert/strict';
import { chartTicks } from '../src/chart-presentation.ts';
test('date ticks are sparse, evenly spaced, UTC-safe and keep endpoints', () => {
  const labels = Array.from({length: 12}, (_, i) => `2026-09-${String(i + 1).padStart(2, '0')}`);
  assert.deepEqual(chartTicks(labels, true, 192), [
    {index: 0, text: 'Sep 1'}, {index: 6, text: 'Sep 7'}, {index: 11, text: 'Sep 12'}
  ]);
  assert.equal(chartTicks(['2026-02-30'], true, 192)[0].text, '2026-02-30');
  assert.equal(chartTicks(['2026-09-01'], false, 192)[0].text, '2026-09-01');
  assert.deepEqual(chartTicks([], true, 192), []);
});
