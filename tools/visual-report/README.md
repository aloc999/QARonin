# Visual Report

One HTML dashboard for the whole regression: JUnit suites + coverage +
LLM-eval, stdlib only.

```bash
python tools/visual-report/generate.py \
  --junit "frameworks/playwright-ts/junit.xml" \
  --junit "frameworks/api-python/junit.xml" \
  --junit "api/postman-newman/newman-report.xml" \
  --coverage coverage.xml \
  --llm-eval evals/llm/eval-report.json \
  -o reports/visual-report.html
# or: make visual-report
python -m pytest tools/visual-report/tests -q
```

CI uploads `reports/visual-report.html` as the release quality record (QMS).
