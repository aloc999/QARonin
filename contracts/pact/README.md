# Pact Contract Testing

Consumer-driven contracts between `roninshop-consumer` (any API client:
api-python, Karate, Newman) and `roninshop-provider` (apps/demo-target).

No broker required: the contract is the checked-in file
`pacts/roninshop-consumer-roninshop-provider.json` (Pact v2 shape).
Provider verification replays each interaction against the real FastAPI app
via `TestClient`, so contract drift fails the build before UI tests see it.

```bash
pip install -r contracts/pact/requirements.txt
python -m pytest contracts/pact/tests -q   # or: make pact-test
```

Tier: L1 API Regression, budget 60s (see strategy/TEST-STRATEGY.md).
CI job: `pact` in ci.yml / regression-30min.yml.
