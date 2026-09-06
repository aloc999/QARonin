# Cypress (E2E + Component)

Cypress 15 suite: E2E parity with Playwright-TS/C# (`smoke`, `regression`),
network interception (`network.cy.js`: spy, stub-to-UI, failure simulation),
custom commands (`cy.login`, `cy.addToCart`, `cy.clearCart`), JSON fixtures,
and a React `ProductCard` component spec via the Cypress component runner.

```bash
cd frameworks/cypress && npm install
npm run test:e2e        # headless Chrome vs $CYPRESS_BASE_URL (default 127.0.0.1:8199)
npm run test:smoke      # fast subset
npm run test:component  # React component runner (needs vite, no backend)
# or: make cypress-test / make cypress-component
```

Tier: L2 UI E2E (parallel CI job, ~6 min). Videos + screenshots upload on failure.
AI test generator note: new user stories start from `cypress/e2e/*.cy.js`
patterns + `support/commands.js`; see reference flows in `regression.cy.js`.
