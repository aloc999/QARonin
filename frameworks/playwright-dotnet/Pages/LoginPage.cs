using Microsoft.Playwright;

namespace QARonin.PlaywrightDotnet.Pages;

public class LoginPage
{
    private readonly IPage _page;
    public LoginPage(IPage page) => _page = page;

    public ILocator UsernameInput => _page.Locator("#username");
    public ILocator PasswordInput => _page.Locator("#password");
    public ILocator SubmitButton => _page.Locator("button[type=submit]");
    public ILocator ErrorBox => _page.Locator(".error, #error");

    public async Task OpenAsync(string baseUrl) => await _page.GotoAsync($"{baseUrl}/login");

    public async Task LoginAsync(string username, string password)
    {
        await UsernameInput.FillAsync(username);
        await PasswordInput.FillAsync(password);
        await SubmitButton.ClickAsync();
    }
}
