namespace CodingSamples.Core.Caching;

public interface ICache<TKey, TValue> where TKey : notnull
{
    TValue? Get(TKey key);
    void Put(TKey key, TValue value);
}
