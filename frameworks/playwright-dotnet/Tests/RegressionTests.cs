using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using NUnit.Framework;
using QARonin.PlaywrightDotnet.Pages;

namespace QARonin.PlaywrightDotnet.Tests;

/// <summary>
/// Mirrors playwright-ts regression.spec.ts (@regression): RBAC negative,
/// cart persistence, logout.
/// </summary>
[TestFixture]
public class RegressionTests : PageTest
{
    private static string BaseUrl =>
        Environment.GetEnvironmentVariable("BASE_URL") ?? "http://127.0.0.1:8199";

    [OneTimeSetUp]
    public async Task AuthenticateOnce() => await AuthSetup.EnsureAsync(BaseUrl);

    public override BrowserNewContextOptions ContextOptions() =>
        new() { StorageStatePath = AuthSetup.StatePath };

    [Test]
    [Category("regression")]
    public async Task AdminRbacNegativeForUserSession()
    {
        var products = new ProductsPage(Page);
        await products.OpenAsync(BaseUrl);
        var token = await Page.EvaluateAsync<string?>("() => localStorage.getItem('token')");
        await using var api = await Playwright.APIRequest.NewContextAsync(new() { BaseURL = BaseUrl });
        var res = await api.GetAsync("/api/admin/orders",
            new() { Headers = new Dictionary<string, string> { ["Authorization"] = $"Bearer {token}" } });
        Assert.That(res.Status, Is.EqualTo(403));
    }

    [Test]
    [Category("regression")]
    public async Task LogoutClearsSessionAndRedirectsToLogin()
    {
        var products = new ProductsPage(Page);
        await products.OpenAsync(BaseUrl);
        await Expect(products.UserBadge).ToHaveTextAsync("demo");
        await Page.Locator("#logout-btn").ClickAsync();
        await Expect(Page).ToHaveURLAsync(new System.Text.RegularExpressions.Regex("/login$"));
        var token = await Page.EvaluateAsync<string?>("() => localStorage.getItem('token')");
        Assert.That(token, Is.Null);
    }
}
