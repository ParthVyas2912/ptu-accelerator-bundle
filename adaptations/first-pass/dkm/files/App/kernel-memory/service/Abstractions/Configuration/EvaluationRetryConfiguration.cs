using System;
using System.Globalization;

namespace Microsoft.KernelMemory.Configuration;

/// <summary>Explicit evaluation opt-in; absent configuration leaves the original factory untouched.</summary>
public static class EvaluationRetryConfiguration
{
    public const string EnvironmentVariableName = "DKM_EVAL_MAX_MODEL_RETRIES";

    public static T Create<T>(Func<T> defaultFactory, Func<int, T> evaluationFactory)
    {
        var value = Environment.GetEnvironmentVariable(EnvironmentVariableName);
        if (string.IsNullOrWhiteSpace(value))
        {
            return defaultFactory();
        }

        if (!int.TryParse(value.Trim(), NumberStyles.None, CultureInfo.InvariantCulture, out var retries)
            || retries < 0 || retries > 3)
        {
            throw new ArgumentException(EnvironmentVariableName + " must be an integer from 0 to 3.");
        }

        return evaluationFactory(retries);
    }
}
