using CodingSamples.Core.Caching;

namespace CodingSamples.Tests.Caching;

public class LruCacheTests
{
    [Fact]
    public void Get_ExistingKey_ReturnsValue()
    {
        var cache = new LruCache<int, int>(2);
        cache.Put(1, 1);
        
        Assert.Equal(1, cache.Get(1));
    }

    [Fact]
    public void Get_NonExistingKey_ReturnsDefault()
    {
        var cache = new LruCache<int, int>(2);
        
        Assert.Equal(0, cache.Get(1));
    }

    [Fact]
    public void Put_OverCapacity_EvictsLru()
    {
        var cache = new LruCache<int, int>(2);
        
        cache.Put(1, 1);
        cache.Put(2, 2);
        cache.Get(1);
        cache.Put(3, 3);
        
        Assert.Equal(0, cache.Get(2));
        Assert.Equal(1, cache.Get(1));
        Assert.Equal(3, cache.Get(3));
    }

    [Fact]
    public void Put_UpdateExistingKey_UpdatesValue()
    {
        var cache = new LruCache<int, int>(2);
        
        cache.Put(1, 1);
        cache.Put(1, 10);
        
        Assert.Equal(10, cache.Get(1));
    }

    [Fact]
    public void Put_UpdateExistingKey_MovesToHead()
    {
        var cache = new LruCache<int, int>(2);
        
        cache.Put(1, 1);
        cache.Put(2, 2);
        cache.Put(1, 10);
        cache.Put(3, 3);
        
        Assert.Equal(0, cache.Get(2));
        Assert.Equal(10, cache.Get(1));
        Assert.Equal(3, cache.Get(3));
    }

    [Fact]
    public void LruCache_FullScenario()
    {
        var cache = new LruCache<int, int>(2);
        
        cache.Put(1, 1);
        cache.Put(2, 2);
        Assert.Equal(1, cache.Get(1));
        
        cache.Put(3, 3);
        Assert.Equal(0, cache.Get(2));
        
        cache.Put(4, 4);
        Assert.Equal(0, cache.Get(1));
        Assert.Equal(3, cache.Get(3));
        Assert.Equal(4, cache.Get(4));
    }
}

public class LfuCacheTests
{
    [Fact]
    public void Get_ExistingKey_ReturnsValue()
    {
        var cache = new LfuCache<int, int>(2);
        cache.Put(1, 1);
        
        Assert.Equal(1, cache.Get(1));
    }

    [Fact]
    public void Get_NonExistingKey_ReturnsDefault()
    {
        var cache = new LfuCache<int, int>(2);
        
        Assert.Equal(0, cache.Get(1));
    }

    [Fact]
    public void Put_OverCapacity_EvictsLfu()
    {
        var cache = new LfuCache<int, int>(2);
        
        cache.Put(1, 1);
        cache.Put(2, 2);
        cache.Get(1);
        cache.Put(3, 3);
        
        Assert.Equal(0, cache.Get(2));
        Assert.Equal(1, cache.Get(1));
        Assert.Equal(3, cache.Get(3));
    }

    [Fact]
    public void Put_ZeroCapacity_DoesNothing()
    {
        var cache = new LfuCache<int, int>(0);
        
        cache.Put(1, 1);
        
        Assert.Equal(0, cache.Get(1));
    }

    [Fact]
    public void LfuCache_EvictsLruAmongSameFrequency()
    {
        var cache = new LfuCache<int, int>(2);
        
        cache.Put(1, 1);
        cache.Put(2, 2);
        cache.Get(1);
        
        cache.Put(3, 3);
        Assert.Equal(0, cache.Get(2));
        Assert.Equal(3, cache.Get(3));
        
        cache.Put(4, 4);
        Assert.Equal(0, cache.Get(1));
        Assert.Equal(3, cache.Get(3));
        Assert.Equal(4, cache.Get(4));
    }

    [Fact]
    public void LfuCache_FullScenario()
    {
        var cache = new LfuCache<int, int>(2);
        
        cache.Put(1, 1);
        cache.Put(2, 2);
        Assert.Equal(1, cache.Get(1));
        
        cache.Put(3, 3);
        Assert.Equal(0, cache.Get(2));
        Assert.Equal(3, cache.Get(3));
        
        cache.Put(4, 4);
        Assert.Equal(0, cache.Get(1));
        Assert.Equal(3, cache.Get(3));
        Assert.Equal(4, cache.Get(4));
    }
}
