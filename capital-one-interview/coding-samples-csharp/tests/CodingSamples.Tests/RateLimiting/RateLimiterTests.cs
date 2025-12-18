using CodingSamples.Core.RateLimiting;

namespace CodingSamples.Tests.RateLimiting;

public class MockTimeProvider : ITimeProvider
{
    private double _currentTime;

    public MockTimeProvider(double initialTime = 0)
    {
        _currentTime = initialTime;
    }

    public double GetCurrentTime() => _currentTime;

    public void AdvanceTime(double seconds)
    {
        _currentTime += seconds;
    }

    public void SetTime(double time)
    {
        _currentTime = time;
    }
}

public class SlidingWindowRateLimiterTests
{
    [Fact]
    public void IsAllowed_RequestsUnderLimit_ReturnsTrue()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new SlidingWindowRateLimiter(maxRequests: 5, windowSeconds: 10, timeProvider);
        
        for (int i = 0; i < 5; i++)
        {
            Assert.True(limiter.IsAllowed("user1"), $"Request {i + 1} should be allowed");
        }
    }

    [Fact]
    public void IsAllowed_RequestsOverLimit_ReturnsFalse()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new SlidingWindowRateLimiter(maxRequests: 5, windowSeconds: 10, timeProvider);
        
        for (int i = 0; i < 5; i++)
        {
            limiter.IsAllowed("user1");
        }
        
        Assert.False(limiter.IsAllowed("user1"), "6th request should be denied");
    }

    [Fact]
    public void IsAllowed_DifferentUsers_Independent()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new SlidingWindowRateLimiter(maxRequests: 2, windowSeconds: 10, timeProvider);
        
        Assert.True(limiter.IsAllowed("user1"));
        Assert.True(limiter.IsAllowed("user1"));
        Assert.False(limiter.IsAllowed("user1"), "user1 should be rate limited");
        Assert.True(limiter.IsAllowed("user2"), "user2 should be allowed");
    }

    [Fact]
    public void GetRemaining_ReturnsCorrectCount()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new SlidingWindowRateLimiter(maxRequests: 5, windowSeconds: 10, timeProvider);
        
        Assert.Equal(5, limiter.GetRemaining("user1"));
        limiter.IsAllowed("user1");
        Assert.Equal(4, limiter.GetRemaining("user1"));
    }

    [Fact]
    public void IsAllowed_WindowExpiry_AllowsNewRequests()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new SlidingWindowRateLimiter(maxRequests: 2, windowSeconds: 1, timeProvider);
        
        Assert.True(limiter.IsAllowed("user1"));
        Assert.True(limiter.IsAllowed("user1"));
        Assert.False(limiter.IsAllowed("user1"));
        
        timeProvider.AdvanceTime(1.1);
        Assert.True(limiter.IsAllowed("user1"), "Should be allowed after window expires");
    }
}

public class TokenBucketRateLimiterTests
{
    [Fact]
    public void IsAllowed_BurstUpToCapacity_ReturnsTrue()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new TokenBucketRateLimiter(bucketCapacity: 10, refillRate: 1.0, timeProvider);
        
        for (int i = 0; i < 10; i++)
        {
            Assert.True(limiter.IsAllowed("user1"), $"Burst request {i + 1} should be allowed");
        }
    }

    [Fact]
    public void IsAllowed_AfterBurst_ReturnsFalse()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new TokenBucketRateLimiter(bucketCapacity: 10, refillRate: 1.0, timeProvider);
        
        for (int i = 0; i < 10; i++)
        {
            limiter.IsAllowed("user1");
        }
        
        Assert.False(limiter.IsAllowed("user1"), "11th request should be denied");
    }

    [Fact]
    public void IsAllowed_Refill_AllowsNewRequests()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new TokenBucketRateLimiter(bucketCapacity: 2, refillRate: 2.0, timeProvider);
        
        Assert.True(limiter.IsAllowed("user1"));
        Assert.True(limiter.IsAllowed("user1"));
        Assert.False(limiter.IsAllowed("user1"));
        
        timeProvider.AdvanceTime(0.6);
        Assert.True(limiter.IsAllowed("user1"), "Should be allowed after refill");
    }

    [Fact]
    public void IsAllowed_DifferentUsers_IndependentBuckets()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new TokenBucketRateLimiter(bucketCapacity: 1, refillRate: 0.1, timeProvider);
        
        Assert.True(limiter.IsAllowed("user1"));
        Assert.False(limiter.IsAllowed("user1"));
        Assert.True(limiter.IsAllowed("user2"), "user2 should have full bucket");
    }
}

public class LeakyBucketRateLimiterTests
{
    [Fact]
    public void IsAllowed_UnderCapacity_ReturnsTrue()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new LeakyBucketRateLimiter(bucketCapacity: 5, leakRate: 0.0, timeProvider);
        
        for (int i = 0; i < 5; i++)
        {
            Assert.True(limiter.IsAllowed("user1"), $"Request {i + 1} should be allowed");
        }
    }

    [Fact]
    public void IsAllowed_OverCapacity_ReturnsFalse()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new LeakyBucketRateLimiter(bucketCapacity: 3, leakRate: 0.0, timeProvider);
        
        for (int i = 0; i < 3; i++)
        {
            limiter.IsAllowed("user1");
        }
        
        Assert.False(limiter.IsAllowed("user1"), "Request over capacity should be denied");
    }

    [Fact]
    public void IsAllowed_Leak_AllowsNewRequests()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new LeakyBucketRateLimiter(bucketCapacity: 2, leakRate: 10.0, timeProvider);
        
        Assert.True(limiter.IsAllowed("user1"));
        Assert.True(limiter.IsAllowed("user1"));
        
        timeProvider.AdvanceTime(0.3);
        Assert.True(limiter.IsAllowed("user1"), "Should be allowed after leak");
        Assert.True(limiter.IsAllowed("user1"), "Should be allowed after leak");
    }
}

public class FixedWindowRateLimiterTests
{
    [Fact]
    public void IsAllowed_UnderLimit_ReturnsTrue()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new FixedWindowRateLimiter(maxRequests: 5, windowSeconds: 10, timeProvider);
        
        for (int i = 0; i < 5; i++)
        {
            Assert.True(limiter.IsAllowed("user1"), $"Request {i + 1} should be allowed");
        }
    }

    [Fact]
    public void IsAllowed_OverLimit_ReturnsFalse()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new FixedWindowRateLimiter(maxRequests: 3, windowSeconds: 10, timeProvider);
        
        for (int i = 0; i < 3; i++)
        {
            limiter.IsAllowed("user1");
        }
        
        Assert.False(limiter.IsAllowed("user1"), "4th request should be denied");
    }

    [Fact]
    public void IsAllowed_NewWindow_ResetsCount()
    {
        var timeProvider = new MockTimeProvider();
        var limiter = new FixedWindowRateLimiter(maxRequests: 2, windowSeconds: 1, timeProvider);
        
        Assert.True(limiter.IsAllowed("user1"));
        Assert.True(limiter.IsAllowed("user1"));
        Assert.False(limiter.IsAllowed("user1"));
        
        timeProvider.AdvanceTime(1.1);
        Assert.True(limiter.IsAllowed("user1"), "Should be allowed in new window");
    }
}
