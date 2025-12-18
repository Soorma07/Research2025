using System.Collections.Concurrent;

namespace CodingSamples.Core.RateLimiting;

public class FixedWindowRateLimiter : IRateLimiter
{
    private readonly int _maxRequests;
    private readonly int _windowSeconds;
    private readonly ITimeProvider _timeProvider;
    private readonly ConcurrentDictionary<string, Dictionary<long, int>> _windows = new();
    private readonly ConcurrentDictionary<string, object> _locks = new();

    public FixedWindowRateLimiter(int maxRequests, int windowSeconds, ITimeProvider? timeProvider = null)
    {
        _maxRequests = maxRequests;
        _windowSeconds = windowSeconds;
        _timeProvider = timeProvider ?? new SystemTimeProvider();
    }

    private long GetWindowKey(double timestamp)
    {
        return (long)(timestamp / _windowSeconds);
    }

    public bool IsAllowed(string userId)
    {
        double currentTime = _timeProvider.GetCurrentTime();
        long windowKey = GetWindowKey(currentTime);

        var lockObj = _locks.GetOrAdd(userId, _ => new object());
        
        lock (lockObj)
        {
            var userWindows = _windows.GetOrAdd(userId, _ => new Dictionary<long, int>());

            var oldKeys = userWindows.Keys.Where(k => k < windowKey - 1).ToList();
            foreach (var k in oldKeys)
            {
                userWindows.Remove(k);
            }

            int currentCount = userWindows.GetValueOrDefault(windowKey, 0);

            if (currentCount < _maxRequests)
            {
                userWindows[windowKey] = currentCount + 1;
                return true;
            }

            return false;
        }
    }
}
