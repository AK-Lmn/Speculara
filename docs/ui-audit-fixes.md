# UI audit fixes

Implemented in the existing project on November 12, 2026. Speculara branding, neumorphic surfaces, six modules, synthetic-data labels and analysis calculations are preserved.

## Changes

- Chat reserves readable message space on short screens, keeps its composer visible, and wraps short suggested-question labels. Opening focuses the input; Escape closes from anywhere while open and restores launcher focus. The panel remains nonmodal, so Tab can reach the page.
- Keyboard focus stays visible on chat and the module list. Main module buttons expose their selected state. Unavailable modules remain disabled.
- Primary buttons keep white text on a dark navy gradient through hover and active states. Secondary text is slightly darker. Shared colors, shadows and motion values now come from 45 project design tokens with deterministic CSS generation.
- Charts use at least 12px labels and sparse month/day ticks. Every bar, value and exact date remains available in titles, accessible chart descriptions and tables. Date formatting uses UTC and preserves invalid labels literally.
- Filter choices wrap visibly. Demo downloads, filter buttons and disclosures have larger touch targets. Phone layouts also work at 125% root text size.

## Verification

Frozen-source checks passed: 13 frontend tests, 22 Chromium browser tests, TypeScript and the production build. Generated tokens are current; token JSON and required contrast pairs pass validation. The measured secondary text contrast is at least 7:1 on normal surfaces; primary hover gradient endpoints measure 9.16:1 and 10.59:1.

Browser coverage includes 320, 375, 768 and 1280px widths, 125% root text at phone widths, exact chart/table agreement, seven forecast bars, loaded short-screen chat, keyboard focus, Escape, existing uploads, reports and plain-language answers. Settled-screen axe checks found no violations in five tested states: empty, recommendations, charts, unavailable sentiment and open chat. A snapshot during arrival animation briefly reported enhanced contrast below 7:1; settled text passes. This is measured evidence, not WCAG certification.

All three tasks received independent reviews. Independent full-change review approved the work with no material findings; its report is in `.superpowers/ui-fixes/final-review.md`. Screenshots and machine evidence remain in `.superpowers/ui-fixes/` because this folder has no Git history.

## Decisions and limits

1. Used the existing folder and snapshots instead of initializing Git or creating a worktree, honoring the user's instruction. Cost: no commit-based rollback.
2. Fixed chat, keyboard access, contrast and readability with scoped shared tokens. Cost: extra audit time; this is not a full redesign.
3. Used natural Tab exit for nonmodal chat instead of an extra F6 command or Leave button. Cost: no dedicated page-jump shortcut.
4. Removed opacity from the focusable module-list container while retaining disabled-button dimming. Cost: one component line was included in the theme task; independent review approved it.

No backend calculations or dependencies changed. Backend tests were not rerun for these presentation-only changes. Real-device software keyboards, screen readers and browsers beyond Chromium were not tested. No GitHub upload or deployment was performed as part of these fixes.
