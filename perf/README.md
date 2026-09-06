# Performance (k6 + Locust + JMeter + Gatling)

| Tool | File | Gate |
|------|------|------|
| k6 | `perf/k6/*.js` | SLO-as-code thresholds (p95 reads <800ms, orders <1200ms, <1% errors) |
| Locust | `perf/locust/locustfile.py` | weighted browse/cart/login/order profile |
| JMeter | `perf/jmeter/smoke.jmx` | 10 threads, 2 min, 800ms duration assertion |
| Gatling | `perf/gatling/RoninShopSimulation.scala` | 20-user ramp, p95<800ms, >99% success |

```bash
make perf-smoke   # k6 + locust vs live target
make perf-jmeter  # needs jmeter: jmeter -n -t perf/jmeter/smoke.jmx
# Gatling runs in CI (maven/gatling plugin) or: mvn gatling:test with the sim on the classpath
```

Soak profiles (k6/Locust extended, JMeter 30-min, Gatling ramp) stay nightly;
the merge gate keeps only `perf-smoke`.
