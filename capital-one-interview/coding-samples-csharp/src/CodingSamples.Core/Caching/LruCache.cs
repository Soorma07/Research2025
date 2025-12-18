namespace CodingSamples.Core.Caching;

public class LruCache<TKey, TValue> : ICache<TKey, TValue> where TKey : notnull
{
    private readonly int _capacity;
    private readonly Dictionary<TKey, ListNode<TKey, TValue>> _cache = new();
    private readonly ListNode<TKey, TValue> _head;
    private readonly ListNode<TKey, TValue> _tail;

    public LruCache(int capacity)
    {
        _capacity = capacity;
        _head = new ListNode<TKey, TValue>(default!, default!);
        _tail = new ListNode<TKey, TValue>(default!, default!);
        _head.Next = _tail;
        _tail.Prev = _head;
    }

    private void AddToHead(ListNode<TKey, TValue> node)
    {
        node.Prev = _head;
        node.Next = _head.Next;
        _head.Next!.Prev = node;
        _head.Next = node;
    }

    private void RemoveNode(ListNode<TKey, TValue> node)
    {
        node.Prev!.Next = node.Next;
        node.Next!.Prev = node.Prev;
    }

    private void MoveToHead(ListNode<TKey, TValue> node)
    {
        RemoveNode(node);
        AddToHead(node);
    }

    private ListNode<TKey, TValue> PopTail()
    {
        var lru = _tail.Prev!;
        RemoveNode(lru);
        return lru;
    }

    public TValue? Get(TKey key)
    {
        if (!_cache.TryGetValue(key, out var node))
        {
            return default;
        }

        MoveToHead(node);
        return node.Value;
    }

    public void Put(TKey key, TValue value)
    {
        if (_cache.TryGetValue(key, out var node))
        {
            node.Value = value;
            MoveToHead(node);
        }
        else
        {
            if (_cache.Count >= _capacity)
            {
                var lru = PopTail();
                _cache.Remove(lru.Key);
            }

            var newNode = new ListNode<TKey, TValue>(key, value);
            _cache[key] = newNode;
            AddToHead(newNode);
        }
    }
}
