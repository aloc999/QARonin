# Selenium-Python Framework

Selenium 4 + pytest UI suite against RoninShop (`apps/demo-target`), mirroring
the Page Object Model contract of `frameworks/playwright-ts`.

## Layout

```
selenium-py/
├── config.py          BASE_URL / BROWSER / HEADLESS / SELENIUM_REMOTE_URL env handling
├── conftest.py        driver fixture (local chrome/firefox or Grid) + page-object fixtures
├── pages/             LoginPage, ProductsPage, CartPage (same selectors as playwright-ts)
├── utils/waits.py     Wait wrapper: visibility/clickability/text/count conditions only,
│                      zero blind sleeps anywhere in the suite
└── tests/             @smoke tier + @regression tier via pytest markers
```

## Running

```bash
pip install -r requirements.txt
make target-up                      # demo target on 127.0.0.1:8199

pytest -m smoke                     # L0 gate
pytest                              # full suite (smoke + regression)

BROWSER=firefox pytest -m smoke     # firefox headless (Selenium Manager fetches geckodriver)
HEADLESS=0 BROWSER=chrome pytest    # headed run for debugging
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BASE_URL` | `http://127.0.0.1:8199` | Demo target base URL |
| `BROWSER` | `chrome` | `chrome` or `firefox`; Selenium Manager resolves the driver automatically |
| `HEADLESS` | `1` | Set `0` for a headed browser |
| `SELENIUM_REMOTE_URL` | unset | When set, sessions go to a remote Grid instead of a local driver (e.g. `http://localhost:4444/wd/hub`). Add the optional `selenium-grid` service in `docker/docker-compose.yml` to use this in containers |

## Test matrix

| Marker | Tests |
|--------|-------|
| `@smoke` | login success redirect, invalid-credentials error, logout clears session, products grid loads 8 seeded cards, add-to-cart badge increment |
| `@regression` | cart badge persists across refresh + line total correctness, checkout order confirmation, RBAC admin denial surfaces error for regular user session, admin role allowed via API |
