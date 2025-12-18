namespace CodingSamples.Core.Caching;

public class ListNode<TKey, TValue>
{
    public TKey Key { get; set; }
    public TValue Value { get; set; }
    public ListNode<TKey, TValue>? Prev { get; set; }
    public ListNode<TKey, TValue>? Next { get; set; }

    public ListNode(TKey key, TValue value)
    {
        Key = key;
        Value = value;
    }
}
