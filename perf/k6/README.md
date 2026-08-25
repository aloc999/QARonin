# perf/k6 - k6 load scripts with SLO-as-code

All scripts encode service-level objectives as k6 `thresholds`. When any
threshold fails, `k6 run` exits non-zero, which makes the threshold set a
drop-in automated SLO gate for CI (a failing SLO breaks the pipeline, not
just a dashboard).

## Scripts

| Script | Flow | Thresholds |
|--------|------|------------|
| `checkout.js` | browse products + login | p95 login < 800ms, p95 products < 800ms, error rate < 1%, checks > 99% |
| `api.js` | products read + order create (tagged requests) | p95 products < 800ms, p95 order create < 1200ms, error rate < 1%, checks > 99% |
| `smoke.js` | single-VU sanity probe of `/api/products` | error rate < 1%, checks > 99% |

Load profile (`stages`): 5s ramp to 10 VUs -> 30s sustain -> 5s ramp down.
`smoke.js` is fixed at 1 VU / 5s.

## Metrics and threshold design

- **p95 latency budgets** come from the tier strategy: interactive reads must
  stay under 800ms at 10 VUs; order creation involves multiple writes and gets
  a 1200ms budget. p95 rather than mean because tail latency is what users feel.
- **`http_req_failed < 1%`** allows for the demo target's deliberately flaky
  endpoint while still catching systemic failures.
- **`checks > 99%`** separates protocol success from functional correctness:
  a 201 with a malformed body still fails the check rate.
- Tagged requests (`tags: { name: "order_create" }`) scope thresholds to
  specific endpoints via `"http_req_duration{name:order_create}"`.

## Usage

```bash
k6 run perf/k6/smoke.js                       # pipeline sanity gate
BASE_URL=http://127.0.0.1:8199 k6 run perf/k6/checkout.js
k6 inspect perf/k6/api.js                     # validate script + list thresholds without load
```

## CI integration

Thresholds are evaluated by k6 itself; `k6 run` returns exit code 99 when a
threshold is breached. A CI job only needs: start target -> `k6 run` ->
non-zero exit fails the build. See `.github/workflows/ci.yml` nightly job.

`example-run.txt` holds a captured real run output for reference.
