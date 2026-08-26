"""Generate the synthetic fixture JUnit XMLs in fixtures/ (deterministic).

Run history across run-1..run-5:

  test_login_flow        P P P P P   -> stable
  test_search_products   P F P F P   -> flaky (flips every transition, rate 1.00)
  test_add_to_cart       P P P P F   -> flaky (one flip, rate 0.25)
  test_checkout_order    P P P P P   -> stable
  test_admin_report      F F F F F   -> broken
  test_new_feature       P P         -> only 2 runs (present from run-4? no: added run-4)
"""

from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def testcase(classname: str, name: str, outcome: str) -> str:
    if outcome == "P":
        return f'    <testcase classname="{classname}" name="{name}" time="0.012"/>'
    return (
        f'    <testcase classname="{classname}" name="{name}" time="0.012">\n'
        f"      <failure message=\"assert 'expected' == 'actual'\">{name} failed</failure>\n"
        f"    </testcase>"
    )


def write_run(run_no: int, cases: list[str]) -> None:
    body = "\n".join(cases)
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<testsuite name="qaronin.synthetic" tests="{len(cases)}" '
        f'failures="{sum(1 for c in cases if "failure" in c)}" time="0.06">\n'
        f"{body}\n"
        "</testsuite>\n"
    )
    (FIXTURES / f"run-{run_no}.xml").write_text(xml, encoding="utf-8")


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)

    # per-run outcomes for tests that appear in all 5 runs
    history = {
        ("tests.api", "test_login_flow"): ["P"] * 5,
        ("tests.ui", "test_search_products"): ["P", "F", "P", "F", "P"],
        ("tests.ui", "test_add_to_cart"): ["P", "P", "P", "P", "F"],
        ("tests.api", "test_checkout_order"): ["P"] * 5,
        ("tests.reports", "test_admin_report"): ["F"] * 5,
    }
    # test added in run 4 (exercises partial-history handling)
    late = {("tests.api", "test_new_feature"): {4: "P", 5: "P"}}

    for run in range(1, 6):
        cases = []
        for (classname, name), outcomes in sorted(history.items()):
            cases.append(testcase(classname, name, outcomes[run - 1]))
        for (classname, name), outcomes in sorted(late.items()):
            if run in outcomes:
                cases.append(testcase(classname, name, outcomes[run]))
        write_run(run, cases)

    print(f"wrote 5 fixture runs to {FIXTURES}")


if __name__ == "__main__":
    main()
