using System.Collections.Concurrent;

namespace CodingSamples.Core.RateLimiting;

public class LeakyBucketRateLimiter : IRateLimiter
{
    private readonly int _bucketCapacity;
    private readonly double _leakRate;
    private readonly ITimeProvider _timeProvider;
    private readonly ConcurrentDictionary<string, double> _buckets = new();
    private readonly ConcurrentDictionary<string, double> _lastLeak = new();
    private readonly ConcurrentDictionary<string, object> _locks = new();

    public LeakyBucketRateLimiter(int bucketCapacity, double leakRate, ITimeProvider? timeProvider = null)
    {
        _bucketCapacity = bucketCapacity;
        _leakRate = leakRate;
        _timeProvider = timeProvider ?? new SystemTimeProvider();
    }

    public bool IsAllowed(string userId)
    {
        double currentTime = _timeProvider.GetCurrentTime();

        var lockObj = _locks.GetOrAdd(userId, _ => new object());
        
        lock (lockObj)
        {
            if (!_lastLeak.ContainsKey(userId))
            {
                _lastLeak[userId] = currentTime;
                _buckets[userId] = 0;
            }

            double elapsed = currentTime - _lastLeak[userId];
            double leaked = elapsed * _leakRate;
            _buckets[userId] = Math.Max(0, _buckets[userId] - leaked);
            _lastLeak[userId] = currentTime;

            if (_buckets[userId] < _bucketCapacity)
            {
                _buckets[userId] += 1;
                return true;
            }

            return false;
        }
    }
}
