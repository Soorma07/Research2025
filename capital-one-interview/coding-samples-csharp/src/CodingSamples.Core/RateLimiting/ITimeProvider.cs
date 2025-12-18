namespace CodingSamples.Core.RateLimiting;

public interface ITimeProvider
{
    double GetCurrentTime();
}

public class SystemTimeProvider : ITimeProvider
{
    public double GetCurrentTime()
    {
        return DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
    }
}
