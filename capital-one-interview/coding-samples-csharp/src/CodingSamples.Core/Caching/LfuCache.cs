namespace CodingSamples.Core.Caching;

public class LfuCache<TKey, TValue> : ICache<TKey, TValue> where TKey : notnull
{
    private readonly int _capacity;
    private int _minFreq;
    private readonly Dictionary<TKey, TValue> _keyToVal = new();
    private readonly Dictionary<TKey, int> _keyToFreq = new();
    private readonly Dictionary<int, LinkedList<TKey>> _freqToKeys = new();

    public LfuCache(int capacity)
    {
        _capacity = capacity;
        _minFreq = 0;
    }

    private void UpdateFreq(TKey key)
    {
        int freq = _keyToFreq[key];
        _keyToFreq[key] = freq + 1;

        _freqToKeys[freq].Remove(key);

        if (_freqToKeys[freq].Count == 0 && _minFreq == freq)
        {
            _minFreq = freq + 1;
        }

        if (!_freqToKeys.ContainsKey(freq + 1))
        {
            _freqToKeys[freq + 1] = new LinkedList<TKey>();
        }
        _freqToKeys[freq + 1].AddLast(key);
    }

    public TValue? Get(TKey key)
    {
        if (!_keyToVal.TryGetValue(key, out var value))
        {
            return default;
        }

        UpdateFreq(key);
        return value;
    }

    public void Put(TKey key, TValue value)
    {
        if (_capacity <= 0)
        {
            return;
        }

        if (_keyToVal.ContainsKey(key))
        {
            _keyToVal[key] = value;
            UpdateFreq(key);
            return;
        }

        if (_keyToVal.Count >= _capacity)
        {
            var evictKey = _freqToKeys[_minFreq].First!.Value;
            _freqToKeys[_minFreq].RemoveFirst();
            _keyToVal.Remove(evictKey);
            _keyToFreq.Remove(evictKey);
        }

        _keyToVal[key] = value;
        _keyToFreq[key] = 1;
        _minFreq = 1;

        if (!_freqToKeys.ContainsKey(1))
        {
            _freqToKeys[1] = new LinkedList<TKey>();
        }
        _freqToKeys[1].AddLast(key);
    }
}
