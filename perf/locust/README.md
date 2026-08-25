# perf/locust - Locust load profile

## Tasks and weighting

| Task | Weight | Endpoint |
|------|--------|----------|
| browse products | 60% | `GET /api/products` |
| add-to-cart (API-equivalent product lookup) | 25% | `GET /api/products/{id}` |
| login | 10% | `POST /api/auth/login` |
| order create | 5% | `POST /api/orders` (auth via token from login task) |

Wait time between tasks: uniform 1-3 seconds (`between(1, 3)`), approximating
think time of a human browsing a small shop.

## Custom stats

A `StatsCsvWriter` listener on the `quitting` event writes
`locust_stats.csv` with per-request name/method/count/failures/median/p95/avg.
Standard Locust CSV/HTML reports remain available via CLI flags.

## Usage

```bash
locust -f perf/locust/locustfile.py --headless -u 5 -r 1 -t 20s \
    --host http://127.0.0.1:8199

LOCUST_CSV_DIR=./out locust -f perf/locust/locustfile.py --headless \
    -u 20 -r 2 -t 2m --host http://127.0.0.1:8199 --csv out/report
```

Exit code is non-zero if the fail ratio exceeds `--stop-on-failure` /
acceptable-loss thresholds you configure, so it can gate CI like k6.

`example-run.txt` holds a captured real headless run for reference.

## Locust vs k6 tradeoffs

| Dimension | k6 | Locust |
|-----------|----|--------|
| Scripting | JavaScript, single-file scenarios | Python; full stdlib/ecosystem in load logic |
| Performance per VU | Go runtime, very low overhead, high VU counts cheap | Gevent greenlets; heavier per user, needs more workers at scale |
| SLO gating | First-class thresholds -> exit codes | Via checks + pass/fail ratios or custom event listeners |
| Distributed load | Native cloud/k6-operator options | Built-in master/worker over zeroMQ |
| Developer fit | Frontend/platform teams comfortable in JS | Python teams reuse fixtures, faker, DB helpers directly |
| Reporting | Rich end-of-test summary + Grafana dashboards | Web UI live control plus CSV; easy custom stats |

QARonin ships both: k6 scripts encode hard SLO gates for CI; the Locust
profile covers realistic weighted behavior mixes and lets Python engineers
extend load logic with existing fixtures.
