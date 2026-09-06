# BDD with Behave (Python)

Gherkin feature suites against the demo-target API (in-process TestClient,
no browser): `auth` (AE-2/3/4), `catalog` (AE-8), `orders` (AE-12/13/16/17 +
RBAC). Steps are shared globally across features, mirroring the api-python
contract assertions in business-readable language.

```bash
pip install -r frameworks/bdd-python/requirements.txt
cd frameworks/bdd-python && behave            # or: make bdd-test
behave --tags=@smoke                          # if tags are added later
```

Tier: L1 API Regression, budget 60s. CI job: `bdd` in regression-30min.yml
and `.gitlab-ci.yml`.
