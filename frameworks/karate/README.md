# Karate API Layer

Karate DSL suite against the demo-target API (auth, products, orders+RBAC).
Feeds the same tier budget report as api-python/Newman.

```bash
cd frameworks/karate
mvn test -Dkarate.baseUrl=http://127.0.0.1:8199   # or: make karate-test
```

Requires Java 17+ and Maven. CI installs both (`actions/setup-java` +
`s4u/setup-maven-action`). JUnit XML from surefire feeds `tier_report.py`.

Tier: L1 API Regression, budget 120s.
