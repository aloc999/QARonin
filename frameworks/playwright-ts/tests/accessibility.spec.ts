import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "fs";
import path from "path";

test.use({ storageState: "playwright/.auth/user.json" });

const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"];
const A11Y_RESULTS_DIR = "test-results/a11y";

interface Violation {
  id: string;
  impact: string | null;
  description: string;
  nodes: number;
}

async function scan(page: import("@playwright/test").Page, name: string) {
  const results = await new AxeBuilder({ page })
    .withTags(WCAG_TAGS)
    .analyze();
  return results.violations.map((v): Violation => ({
    id: v.id,
    impact: v.impact,
    description: v.description,
    nodes: v.nodes.length,
  }));
}

function writeArtifact(pageName: string, violations: Violation[]) {
  fs.mkdirSync(A11Y_RESULTS_DIR, { recursive: true });
  fs.writeFileSync(
    path.join(A11Y_RESULTS_DIR, `${pageName}-violations.json`),
    JSON.stringify(violations, null, 2)
  );
}

for (const pagePath of ["/login", "/products", "/cart"]) {
  test(`@a11y @regression accessibility: ${pagePath} has no critical or serious violations`, async ({
    page,
  }) => {
    await page.goto(pagePath);
    const violations = await scan(page, pagePath);
    const blocking = violations.filter(
      (v) => v.impact === "critical" || v.impact === "serious"
    );
    if (blocking.length > 0) {
      writeArtifact(pagePath.replace(/\//g, "") || "root", blocking);
    }
    expect
      .soft(
        blocking,
        `${pagePath}: critical/serious axe violations found (artifact written to ${A11Y_RESULTS_DIR})`
      )
      .toEqual([]);
    expect(blocking).toEqual([]);
  });
}
