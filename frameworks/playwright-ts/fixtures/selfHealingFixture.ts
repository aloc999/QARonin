import { test as base, expect, Locator, Page } from "@playwright/test";
import { execFileSync } from "child_process";
import * as fs from "fs";
import * as path from "path";

/**
 * Self-healing Playwright fixture for QARonin.
 *
 * On locator failure it:
 *   1. captures a minimal DOM snapshot (tag/id/classes/attrs/text),
 *   2. writes a `FailureContext` JSON compatible with `python -m selfheal heal`,
 *   3. calls `python -m selfheal heal --failure <f> --dom <d> --report`
 *      with `SELFHEAL_REPORT_PATH=reports/healing/<stamp>.jsonl`,
 *   4. retries the action once with the healed selector.
 *
 * JSONL audit trail lands in `reports/healing/` (one file per failure,
 * never overwritten). The healer itself lives in `ai-selfhealing/selfheal/`
 * and runs offline-heuristic when no OPENAI_API_KEY is set.
 *
 * Usage:
 * ```ts
 * import { test, expect } from "../fixtures/selfHealingFixture";
 *
 * test("@smoke checkout still works after id rename", async ({ page, healOnFailure }) => {
 *   await page.goto("/cart");
 *   await healOnFailure("#submit-order-btn", "click checkout button", async (locator) => {
 *     await locator.click();
 *   });
 * });
 * ```
 */

export type HealFn = (
  originalSelector: string,
  action: string,
  actionFn: (locator: Locator) => Promise<void>
) => Promise<{ healed: boolean; selector: string }>;

type SelfHealingFixtures = {
  healOnFailure: HealFn;
};

const HEALING_DIR = path.resolve(__dirname, "../../reports/healing");
const SELFHEAL_CWD = path.resolve(__dirname, "../../../ai-selfhealing");

function ensureHealingDir(): string {
  fs.mkdirSync(HEALING_DIR, { recursive: true });
  return HEALING_DIR;
}

function stamp(): string {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

/** Minimal DOM snapshot: enough signal for the offline heuristic scorer. */
async function captureDomSnapshot(page: Page): Promise<{ elements: unknown[] }> {
  const elements = await page.evaluate(() => {
    const nodes = Array.from(document.querySelectorAll("button, a, input, div, span, h1, h2, td, [data-testid], [id]"));
    return nodes.slice(0, 120).map((el) => {
      const e = el as HTMLElement;
      const rect = e.getBoundingClientRect();
      return {
        tag: e.tagName.toLowerCase(),
        id: (e as HTMLElement).id || "",
        classes: Array.from(e.classList || []),
        attributes: Object.fromEntries(
          Array.from(e.attributes || [])
            .filter((a) => ["type", "href", "value", "role", "data-testid", "name", "placeholder"].includes(a.name))
            .map((a) => [a.name, a.value])
        ),
        text: (e.innerText || e.textContent || "").slice(0, 80),
        position: [Math.round(rect.x), Math.round(rect.y)],
        parent_tag: e.parentElement ? e.parentElement.tagName.toLowerCase() : "",
        parent_classes: e.parentElement ? Array.from(e.parentElement.classList || []) : [],
        unique: true,
      };
    });
  });
  return { elements };
}

function runHealer(failurePath: string, domPath: string, reportPath: string): string | null {
  try {
    execFileSync(
      "python3",
      ["-m", "selfheal", "heal", "--failure", failurePath, "--dom", domPath, "--report"],
      {
        cwd: SELFHEAL_CWD,
        timeout: 60_000,
        stdio: "pipe",
        env: { ...process.env, SELFHEAL_REPORT_PATH: reportPath, PYTHONPATH: "." },
      }
    );
  } catch {
    // Non-zero exit just means "no healed selector"; the JSONL (if any) is still written.
  }
  try {
    const lines = fs.readFileSync(reportPath, "utf-8").trim().split("\n").filter(Boolean);
    if (lines.length === 0) return null;
    const last = JSON.parse(lines[lines.length - 1]) as { healed_selector?: string };
    return last.healed_selector || null;
  } catch {
    return null;
  }
}

export const test = base.extend<SelfHealingFixtures>({
  healOnFailure: async ({ page }, use) => {
    const heal: HealFn = async (originalSelector, action, actionFn) => {
      try {
        await actionFn(page.locator(originalSelector));
        return { healed: false, selector: originalSelector };
      } catch (firstError) {
        const dir = ensureHealingDir();
        const runStamp = stamp();
        const failurePath = path.join(dir, `failure-${runStamp}.json`);
        const domPath = path.join(dir, `dom-${runStamp}.json`);
        const reportPath = path.join(dir, `healing-${runStamp}.jsonl`);
        const failure = {
          selector: originalSelector,
          selector_type: "css",
          page_url: page.url(),
          action,
          error: String((firstError as Error)?.message || firstError).slice(0, 500),
        };
        fs.writeFileSync(failurePath, JSON.stringify(failure, null, 2));
        try {
          fs.writeFileSync(domPath, JSON.stringify(await captureDomSnapshot(page), null, 2));
        } catch {
          fs.writeFileSync(domPath, JSON.stringify({ elements: [] }));
        }
        // eslint-disable-next-line no-console
        console.log(`[self-heal] ${originalSelector} failed (${action}); calling selfheal -> ${reportPath}`);
        const healedSelector = runHealer(failurePath, domPath, reportPath);
        if (!healedSelector) throw firstError;
        // eslint-disable-next-line no-console
        console.log(`[self-heal] retrying with healed selector: ${healedSelector}`);
        await actionFn(page.locator(healedSelector));
        return { healed: true, selector: healedSelector };
      }
    };
    await use(heal);
  },
});

export { expect };
