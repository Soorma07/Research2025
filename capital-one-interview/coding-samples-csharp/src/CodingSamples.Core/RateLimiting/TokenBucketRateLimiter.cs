using System.Collections.Concurrent;

namespace CodingSamples.Core.RateLimiting;

public class TokenBucketRateLimiter : IRateLimiter
{
    private readonly int _bucketCapacity;
    private readonly double _refillRate;
    private readonly ITimeProvider _timeProvider;
    private readonly ConcurrentDictionary<string, double> _buckets = new();
    private readonly ConcurrentDictionary<string, double> _lastRefill = new();
    private readonly ConcurrentDictionary<string, object> _locks = new();

    public TokenBucketRateLimiter(int bucketCapacity, double refillRate, ITimeProvider? timeProvider = null)
    {
        _bucketCapacity = bucketCapacity;
        _refillRate = refillRate;
        _timeProvider = timeProvider ?? new SystemTimeProvider();
    }

    public bool IsAllowed(string userId)
    {
        double currentTime = _timeProvider.GetCurrentTime();

        var lockObj = _locks.GetOrAdd(userId, _ => new object());
        
        lock (lockObj)
        {
            if (!_buckets.ContainsKey(userId))
            {
                _buckets[userId] = _bucketCapacity;
                _lastRefill[userId] = currentTime;
            }

            double elapsed = currentTime - _lastRefill[userId];
            _buckets[userId] = Math.Min(
                _bucketCapacity,
                _buckets[userId] + elapsed * _refillRate
            );
            _lastRefill[userId] = currentTime;

            if (_buckets[userId] >= 1)
            {
                _buckets[userId] -= 1;
                return true;
            }

            return false;
        }
    }
}
