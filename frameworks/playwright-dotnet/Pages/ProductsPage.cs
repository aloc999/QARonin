using Microsoft.Playwright;

namespace QARonin.PlaywrightDotnet.Pages;

public class ProductsPage
{
    private readonly IPage _page;
    public ProductsPage(IPage page) => _page = page;

    public ILocator ProductCards => _page.Locator(".card.product");
    public ILocator CartCount => _page.Locator("#cart-count");
    public ILocator UserBadge => _page.Locator("#user-badge");

    public async Task OpenAsync(string baseUrl) => await _page.GotoAsync($"{baseUrl}/products");
}
