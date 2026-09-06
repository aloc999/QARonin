using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;
using QARonin.PlaywrightDotnet.Pages;

namespace QARonin.PlaywrightDotnet.Tests;

/// <summary>
/// Lintas bahasa (cross-language) parity: mirrors frameworks/playwright-ts
/// smoke.spec.ts tag-for-tag (@smoke). Same selectors, same assertions.
/// </summary>
[TestFixture]
public class SmokeTests : PageTest
{
    private static string BaseUrl =>
        Environment.GetEnvironmentVariable("BASE_URL") ?? "http://127.0.0.1:8199";

    [OneTimeSetUp]
    public async Task AuthenticateOnce() => await AuthSetup.EnsureAsync(BaseUrl);

    public override BrowserNewContextOptions ContextOptions() =>
        new() { StorageStatePath = AuthSetup.StatePath };

    [Test]
    [Category("smoke")]
    public async Task ProductGridLoadsWithSeededItems()
    {
        var products = new ProductsPage(Page);
        await products.OpenAsync(BaseUrl);
        await Expect(products.ProductCards).ToHaveCountAsync(8);
        await Expect(products.ProductCards.First).ToContainTextAsync("$");
    }

    [Test]
    [Category("smoke")]
    public async Task AddToCartIncrementsBadge()
    {
        var products = new ProductsPage(Page);
        await products.OpenAsync(BaseUrl);
        await products.ProductCards.First.Locator(".add-to-cart").ClickAsync();
        await Expect(products.CartCount).ToHaveTextAsync("1");
    }

    [Test]
    [Category("smoke")]
    public async Task LoginWithInvalidCredentialsShowsError()
    {
        var login = new LoginPage(Page);
        await login.OpenAsync(BaseUrl);
        await login.LoginAsync("demo", "wrong-password");
        await Expect(login.ErrorBox).ToBeVisibleAsync();
        await Expect(login.ErrorBox).ToContainTextAsync("Invalid username or password.");
    }
}
