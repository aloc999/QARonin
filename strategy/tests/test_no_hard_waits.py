import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from no_hard_waits import BANNED, load_allowlist, scan


def _match_any(line):
    return [msg for rx, msg in BANNED if rx.search(line)]


def test_banned_patterns_match():
    assert _match_any("await page.waitForTimeout(300)")
    assert _match_any("time.sleep(1)")
    assert _match_any("Thread.sleep(1000)")
    assert _match_any("await Task.Delay(500)")
    assert _match_any("cy.wait(2000)")
    assert _match_any("driver.implicitly_wait(10)")


def test_blessed_alternatives_not_flagged():
    assert not _match_any('cy.wait("@getProducts")')
    assert not _match_any("await expect(page.locator('#x')).toBeVisible()")
    assert not _match_any("WebDriverWait(driver, 10).until(EC.visibility_of_element_located(loc))")
    assert not _match_any("for i in $(seq 1 30); do curl -sf $URL && break || sleep 1; done")


def test_allowlist_documents_reasons():
    allowed = load_allowlist()
    assert allowed, "allowlist must exist with documented exceptions"
    assert all(reason for reason in allowed.values())


def test_repo_is_clean():
    assert scan() == []
