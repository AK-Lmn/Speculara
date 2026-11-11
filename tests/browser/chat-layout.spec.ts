import { test, expect } from "@playwright/test";
test("chat suggestions and composer stay inside the panel at narrow and short sizes", async ({
  page,
}) => {
  for (const size of [
    { width: 375, height: 620 },
    { width: 320, height: 420 },
    { width: 1280, height: 720 },
  ]) {
    await page.setViewportSize(size);
    await page.goto("/");
    await page.getByRole("button", { name: "Open chat", exact: true }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    const suggestions = dialog.getByRole("group", { name: "Suggested questions" });
    await expect(suggestions).toBeVisible();
    const box = await dialog.boundingBox();
    expect(box!.y).toBeGreaterThanOrEqual(8);
    expect(box!.y + box!.height).toBeLessThanOrEqual(size.height - 70);
    for (const button of await suggestions.getByRole("button").all()) {
      const chip = await button.boundingBox();
      expect(chip!.x).toBeGreaterThanOrEqual(box!.x + 8);
      expect(chip!.x + chip!.width).toBeLessThanOrEqual(box!.x + box!.width - 8);
      await expect(button).toBeVisible();
    }
    expect(await suggestions.evaluate((el) => el.scrollWidth <= el.clientWidth)).toBe(true);
    await expect(dialog.getByRole("textbox", { name: "Your question" })).toBeVisible();
    await dialog.getByRole("textbox", { name: "Your question" }).fill("hello");
    await dialog.getByRole("button", { name: "Send", exact: true }).click();
    await expect(dialog).toContainText("Upload a dataset");
    await page.keyboard.press("Escape");
    await expect(dialog).toHaveCount(0);
  }
});
