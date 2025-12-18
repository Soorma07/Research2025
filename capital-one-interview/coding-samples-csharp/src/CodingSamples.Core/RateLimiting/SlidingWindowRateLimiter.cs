using System.Collections.Concurrent;

namespace CodingSamples.Core.RateLimiting;

public class SlidingWindowRateLimiter : IRateLimiter
{
    private readonly int _maxRequests;
    private readonly int _windowSeconds;
    private readonly ITimeProvider _timeProvider;
    private readonly ConcurrentDictionary<string, Queue<double>> _userRequests = new();
    private readonly ConcurrentDictionary<string, object> _locks = new();

    public SlidingWindowRateLimiter(int maxRequests, int windowSeconds, ITimeProvider? timeProvider = null)
    {
        _maxRequests = maxRequests;
        _windowSeconds = windowSeconds;
        _timeProvider = timeProvider ?? new SystemTimeProvider();
    }

    public bool IsAllowed(string userId)
    {
        double currentTime = _timeProvider.GetCurrentTime();
        double windowStart = currentTime - _windowSeconds;

        var lockObj = _locks.GetOrAdd(userId, _ => new object());
        
        lock (lockObj)
        {
            var requests = _userRequests.GetOrAdd(userId, _ => new Queue<double>());

            while (requests.Count > 0 && requests.Peek() < windowStart)
            {
                requests.Dequeue();
            }

            if (requests.Count < _maxRequests)
            {
                requests.Enqueue(currentTime);
                return true;
            }

            return false;
        }
    }

    public int GetRemaining(string userId)
    {
        double currentTime = _timeProvider.GetCurrentTime();
        double windowStart = currentTime - _windowSeconds;

        var lockObj = _locks.GetOrAdd(userId, _ => new object());
        
        lock (lockObj)
        {
            if (!_userRequests.TryGetValue(userId, out var requests))
            {
                return _maxRequests;
            }

            int validCount = requests.Count(t => t >= windowStart);
            return Math.Max(0, _maxRequests - validCount);
        }
    }
}
