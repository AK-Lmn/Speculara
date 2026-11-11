import { test, expect } from "@playwright/test";
test("dataset notes are readable and full methods stay in report", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Try synthetic demo data" }).click();
  const summary = page.getByRole("region", { name: "Dataset summary" });
  await expect(summary).toContainText("42 rows", { timeout: 30000 });
  await summary.getByText("About this data", { exact: true }).click();
  await expect(summary.getByText("This demo uses made-up records.")).toBeVisible();
  await expect(
    summary.getByText("Patterns are clues, not proof of what caused a change."),
  ).toBeVisible();
  await expect(summary).not.toContainText("Pearson");
  await expect(summary).not.toContainText("Schema version");
  const notes = summary.locator("details");
  await expect(notes).toHaveCSS("font-size", "16px");
  expect((await notes.innerText()).length).toBeLessThan(700);
  await summary.screenshot({path:"docs/screenshots/data-notes.png"});
});

test('file-specific issues remain visible in simple language',async({page})=>{
  await page.goto('/');
  await page.locator('#upload').setInputFiles({name:'checks.csv',mimeType:'text/csv',buffer:Buffer.from('date,views,sales\nbad,100,2\n2026-01-01,,3\n2026-01-02,200,4\n2026-01-02,200,4\n')});
  const summary=page.getByRole('region',{name:'Dataset summary'});await expect(summary).toContainText('4 rows',{timeout:30000});
  await summary.getByText('About this data',{exact:true}).click();
  await expect(summary.getByText('Some counts are missing. They are left out, not counted as zero.')).toBeVisible();
  await expect(summary.getByText('Some dates are missing or unreadable. Time comparisons may be unavailable.')).toBeVisible();
  await expect(summary.getByText('Some entries repeat. Check they were not counted twice.')).toBeVisible();
});
