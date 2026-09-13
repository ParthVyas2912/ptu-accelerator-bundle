using System.Net;
using Azure.Core;
using Azure.AI.OpenAI;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
#if LEGACY
using Azure.Core.Pipeline;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Eval = Microsoft.KernelMemory.Configuration.EvaluationRetryConfiguration;
#else
using System.ClientModel.Primitives;
using Eval = Microsoft.GS.DPSHost.Helpers.EvaluationRetryConfiguration;
#endif

// No network is used: every SDK request terminates in this in-memory transport.
// These synthetic transport attempts are NOT live model calls.
sealed class Offline503 : HttpMessageHandler
{
    public int Count;
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        if (request.RequestUri?.Host != "unit.invalid")
            throw new Exception("Unexpected destination in offline regression");
        Count++;
        var response = new HttpResponseMessage(HttpStatusCode.ServiceUnavailable)
        {
            Content = new StringContent("{\"error\":{\"code\":\"ServiceUnavailable\",\"message\":\"offline fixture\"}}")
        };
        response.Headers.TryAddWithoutValidation("Retry-After", "0");
        response.Headers.TryAddWithoutValidation("retry-after-ms", "0");
        return Task.FromResult(response);
    }
}

sealed class OfflineCredential : TokenCredential
{
    public override AccessToken GetToken(TokenRequestContext context, CancellationToken cancellationToken) =>
        new("offline-fixture-not-a-credential", DateTimeOffset.UtcNow.AddHours(1));
    public override ValueTask<AccessToken> GetTokenAsync(TokenRequestContext context, CancellationToken cancellationToken) =>
        ValueTask.FromResult(GetToken(context, cancellationToken));
}

static class Program
{
    static int passed;
    static void Check(bool condition, string name)
    {
        if (!condition) throw new Exception("FAILED: " + name);
        passed++;
        Console.WriteLine("PASS " + name);
    }

    static void ContractTests()
    {
        foreach (string? value in new string?[] { null, "", "   " })
        {
            Environment.SetEnvironmentVariable(Eval.EnvironmentVariableName, value);
            var original = new object();
            int normalCalls = 0, evaluationCalls = 0;
            var actual = Eval.Create(() => { normalCalls++; return original; },
                _ => { evaluationCalls++; return new object(); });
            Check(ReferenceEquals(original, actual) && normalCalls == 1 && evaluationCalls == 0,
                "unset/empty preserves original factory and object");
        }
        foreach (var value in new[] { 0, 1, 2, 3 })
        {
            Environment.SetEnvironmentVariable(Eval.EnvironmentVariableName, value.ToString());
            int normalCalls = 0;
            var actual = Eval.Create(() => { normalCalls++; return -1; }, retries => retries);
            Check(actual == value && normalCalls == 0, "explicit opt-in " + value);
        }
        foreach (var value in new[] { "-1", "4", "invalid" })
        {
            Environment.SetEnvironmentVariable(Eval.EnvironmentVariableName, value);
            int factoryCalls = 0;
            bool rejected = false;
            try { Eval.Create(() => { factoryCalls++; return 0; }, _ => { factoryCalls++; return 0; }); }
            catch (ArgumentException) { rejected = true; }
            Check(rejected && factoryCalls == 0, "invalid opt-in fails before client creation");
        }
    }

    static Kernel ControlledKernel(int retries, HttpClient http)
    {
#if LEGACY
        var options = new OpenAIClientOptions { Transport = new HttpClientTransport(http) };
        options.Retry.MaxRetries = retries;
        options.Retry.Delay = TimeSpan.Zero;
        options.Retry.MaxDelay = TimeSpan.Zero;
        var client = new OpenAIClient(new Uri("https://unit.invalid"), new OfflineCredential(), options);
#else
        var options = new AzureOpenAIClientOptions
        {
            Transport = new HttpClientPipelineTransport(http),
            RetryPolicy = new ClientRetryPolicy(retries)
        };
        var client = new AzureOpenAIClient(new Uri("https://unit.invalid"), new OfflineCredential(), options);
#endif
        return Kernel.CreateBuilder().AddAzureOpenAIChatCompletion("offline", client).Build();
    }

    static async Task<int> ChatAttempts(bool wrapped, string? optIn)
    {
        Environment.SetEnvironmentVariable(Eval.EnvironmentVariableName, optIn);
        using var handler = new Offline503();
        using var http = new HttpClient(handler);
        Kernel DefaultFactory() => Kernel.CreateBuilder().AddAzureOpenAIChatCompletion(
            deploymentName: "offline", endpoint: "https://unit.invalid",
            credentials: new OfflineCredential(), httpClient: http).Build();
        var kernel = wrapped ? Eval.Create(DefaultFactory, retries => ControlledKernel(retries, http)) : DefaultFactory();
        try { await kernel.GetRequiredService<IChatCompletionService>().GetChatMessageContentAsync("offline test"); }
        catch (Exception) when (handler.Count > 0) { }
        return handler.Count;
    }

#if LEGACY
    static async Task<int> EmbeddingAttempts(bool wrapped, string? optIn)
    {
        Environment.SetEnvironmentVariable(Eval.EnvironmentVariableName, optIn);
        using var handler = new Offline503();
        using var http = new HttpClient(handler);
        AzureOpenAITextEmbeddingGenerationService DefaultFactory() => new(
            deploymentName: "offline", endpoint: "https://unit.invalid",
            credential: new OfflineCredential(), httpClient: http);
        AzureOpenAITextEmbeddingGenerationService Controlled(int retries)
        {
            var options = new OpenAIClientOptions { Transport = new HttpClientTransport(http) };
            options.Retry.MaxRetries = retries;
            options.Retry.Delay = TimeSpan.Zero;
            options.Retry.MaxDelay = TimeSpan.Zero;
            var client = new OpenAIClient(new Uri("https://unit.invalid"), new OfflineCredential(), options);
            return new AzureOpenAITextEmbeddingGenerationService("offline", client);
        }
        var service = wrapped ? Eval.Create(DefaultFactory, Controlled) : DefaultFactory();
        try { await service.GenerateEmbeddingsAsync(new[] { "offline test" }); }
        catch (Exception) when (handler.Count > 0) { }
        return handler.Count;
    }
#endif

    static async Task Main()
    {
        var previous = Environment.GetEnvironmentVariable(Eval.EnvironmentVariableName);
        try
        {
            ContractTests();
            var baseline = await ChatAttempts(false, null);
            Console.WriteLine($"Observed stock chat fake-transport attempts={baseline}");
            Check(baseline > 0 && await ChatAttempts(true, null) == baseline,
                "chat unset preserves stock SDK transport attempts");
            Check(await ChatAttempts(true, "0") == 1, "chat eval0 gives one transport attempt");
            Check(await ChatAttempts(true, "2") == 3, "chat eval2 gives three transport attempts");
#if LEGACY
            var embeddingBaseline = await EmbeddingAttempts(false, null);
            Console.WriteLine($"Observed stock embedding fake-transport attempts={embeddingBaseline}");
            Check(embeddingBaseline > 0 && await EmbeddingAttempts(true, null) == embeddingBaseline,
                "embedding unset preserves stock SDK transport attempts");
            Check(await EmbeddingAttempts(true, "0") == 1, "embedding eval0 gives one transport attempt");
            Check(await EmbeddingAttempts(true, "2") == 3, "embedding eval2 gives three transport attempts");
#endif
            Console.WriteLine($"ALL_PASS assertions={passed}; live_network_requests=0");
        }
        finally { Environment.SetEnvironmentVariable(Eval.EnvironmentVariableName, previous); }
    }
}
