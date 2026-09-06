using System.Net.Http.Json;
using System.Text.Json;

namespace QARonin.PlaywrightDotnet.Tests;

/// <summary>
/// Mirrors frameworks/playwright-ts/tests/global-setup.ts: logs in via the
/// API once per fixture and writes a Playwright storage-state file so every
/// test starts with an authenticated session (localStorage token/username/role).
/// </summary>
public static class AuthSetup
{
    public static readonly string StateDir =
        Path.Combine(AppContext.BaseDirectory, ".auth");

    public static readonly string StatePath =
        Path.Combine(StateDir, "user.json");

    public static async Task EnsureAsync(string baseUrl)
    {
        if (File.Exists(StatePath))
            return;

        using var http = new HttpClient { BaseAddress = new Uri(baseUrl) };
        using var res = await http.PostAsJsonAsync(
            "/api/auth/login", new { username = "demo", password = "demo1234" });
        res.EnsureSuccessStatusCode();
        using var body = await res.Content.ReadFromJsonAsync<JsonDocument>();
        var token = body!.RootElement.GetProperty("access_token").GetString();

        Directory.CreateDirectory(StateDir);
        var state = new
        {
            cookies = Array.Empty<object>(),
            origins = new[]
            {
                new
                {
                    origin = baseUrl,
                    localStorage = new[]
                    {
                        new { name = "token", value = token },
                        new { name = "username", value = "demo" },
                        new { name = "role", value = "user" },
                    },
                },
            },
        };
        await File.WriteAllTextAsync(
            StatePath,
            JsonSerializer.Serialize(state, new JsonSerializerOptions { WriteIndented = true }));
    }
}
