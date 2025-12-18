namespace CodingSamples.Core.RateLimiting;

public interface IRateLimiter
{
    bool IsAllowed(string userId);
}
