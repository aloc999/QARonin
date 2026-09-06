# Playwright .NET — Lintas Bahasa (Cross-Language Parity)

C# port of `frameworks/playwright-ts` smoke + regression suites.
"Lintas bahasa" = cross-language: every `@smoke`/`@regression` case exists in
both TypeScript and C# with identical selectors and assertions, proving the
Page Object contract is language-agnostic.

| TS (playwright-ts) | C# (this dir) |
|--------------------|---------------|
| smoke: product grid (8 cards) | SmokeTests.ProductGridLoadsWithSeededItems |
| smoke: add-to-cart badge | SmokeTests.AddToCartIncrementsBadge |
| smoke: invalid login error | SmokeTests.LoginWithInvalidCredentialsShowsError |
| regression: admin RBAC 403 | RegressionTests.AdminRbacNegativeForUserSession |
| regression: logout clears session | RegressionTests.LogoutClearsSessionAndRedirectsToLogin |

```bash
# needs .NET 6 SDK + browsers
dotnet restore frameworks/playwright-dotnet
dotnet build frameworks/playwright-dotnet --no-restore
BASE_URL=http://127.0.0.1:8199 dotnet test frameworks/playwright-dotnet --no-build --filter "Category=smoke"
# or: make csharp-install csharp-test
pwsh frameworks/playwright-dotnet/bin/Debug/net6.0/playwright.ps1 install chromium
```

Auth mirrors `playwright-ts/tests/global-setup.ts`: `Tests/AuthSetup.cs` logs
in via `POST /api/auth/login` once per fixture and writes a storage-state
file (localStorage `token`/`username`/`role`) consumed through
`ContextOptions().StorageStatePath`, so UI tests start authenticated.

Note: UI suites (TS and C#) require the demo-target's pinned dependencies
(`apps/demo-target/requirements.txt`, Starlette 0.x template API). Running the
target under a newer Starlette breaks `/products` rendering for every
framework, not just this one.

Tier: L2 UI E2E (C# shard, ~8 min budget). CI job: `csharp-tests`.
