/**
 * EXAMPLE ONLY - not compiled or executed by any build in this repo.
 *
 * TypeScript port of the resilient-locator pattern from
 * selfheal/integration/resilient.py, for teams whose suites are on
 * Playwright for Node. It shells out to the selfheal engine (installed via
 * `pip install ./ai-selfhealing` or run as `python -m selfheal heal ...`)
 * so the scoring/agent logic stays in one place.
 */

import { Page, Locator } from "@playwright/test";
import { spawnSync } from "child_process";
import { writeFileSync, mkdtempSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

interface DomElementJson {
  tag: string;
  id: string;
  classes: string[];
  attributes: Record<string, string>;
  text: string;
  position?: [number, number];
  parent_tag?: string;
  parent_classes?: string[];
  unique?: boolean;
}

interface HealingVerdict {
  healed_selector: string | null;
  confidence: number;
  mode: string;
}

function collectDom(page: Page): DomElementJson[] {
  return page.evaluate(() =>
    Array.from(document.querySelectorAll("*"))
      .slice(0, 400)
      .map((el) => {
        const rect = el.getBoundingClientRect();
        const attrs: Record<string, string> = {};
        for (const attr of Array.from(el.attributes)) attrs[attr.name] = attr.value;
        return {
          tag: el.tagName.toLowerCase(),
          id: el.id || "",
          classes: Array.from(el.classList),
          attributes: attrs,
          text: (el.textContent || "").trim().slice(0, 120),
          position: [Math.round(rect.x), Math.round(rect.y)] as [number, number],
          parent_tag: el.parentElement ? el.parentElement.tagName.toLowerCase() : "",
          parent_classes: el.parentElement ? Array.from(el.parentElement.classList) : [],
          unique: el.id ? document.querySelectorAll(`#${CSS.escape(el.id)}`).length === 1 : true,
        };
      })
  ) as unknown as DomElementJson[];
}

/**
 * Ask the Python selfheal engine to rank candidates for a failed selector.
 * Runs fully offline unless OPENAI_API_KEY is exported (agentic mode).
 */
export function healSelector(
  failure: { selector: string; page_url: string; action: string; error: string },
  dom: DomElementJson[]
): HealingVerdict {
  const dir = mkdtempSync(join(tmpdir(), "selfheal-"));
  const failurePath = join(dir, "failure.json");
  const domPath = join(dir, "dom.json");
  writeFileSync(failurePath, JSON.stringify(failure));
  writeFileSync(domPath, JSON.stringify({ elements: dom }));

  const proc = spawnSync(
    "python3",
    ["-m", "selfheal", "heal", "--failure", failurePath, "--dom", domPath],
    {
      encoding: "utf-8",
      env: { ...process.env },
      cwd: join(__dirname, "..", "..", "ai-selfhealing"),
    }
  );
  if (proc.status !== 0) return { healed_selector: null, confidence: 0, mode: "unavailable" };

  // The CLI prints a table; the first candidate line is `1<spaces><selector><spaces>score`.
  const match = proc.stdout.match(/^1\s{2,}(\S.*)\s{2,}\d\.\d+$/m);
  if (!match) return { healed_selector: null, confidence: 0, mode: "heuristic" };
  return { healed_selector: match[1].trim(), confidence: 0.5, mode: "cli" };
}

/**
 * resilient.locator(page, "#submit-order-btn") -> Locator that retries with
 * the healed selector if the original fails, logging to selfheal-report.jsonl.
 */
export async function resilientLocator(
  page: Page,
  originalSelector: string,
  action: (locator: Locator) => Promise<void>
): Promise<void> {
  try {
    await action(page.locator(originalSelector));
    return;
  } catch (error) {
    const verdict = healSelector({
      selector: originalSelector,
      page_url: page.url(),
      action: "resilient",
      error: String(error).slice(0, 500),
    }, collectDom(page));
    console.log("[selfheal]", originalSelector, "->", JSON.stringify(verdict));
    if (!verdict.healed_selector || verdict.confidence < 0.5) throw error;
    await action(page.locator(verdict.healed_selector));
  }
}
