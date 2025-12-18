namespace CodingSamples.Core.AccountMerging;

public class UnionFind
{
    private readonly Dictionary<string, string> _parent = new();
    private readonly Dictionary<string, int> _rank = new();

    public string Find(string x)
    {
        if (!_parent.ContainsKey(x))
        {
            _parent[x] = x;
            _rank[x] = 0;
        }

        if (_parent[x] != x)
        {
            _parent[x] = Find(_parent[x]);
        }

        return _parent[x];
    }

    public void Union(string x, string y)
    {
        string rootX = Find(x);
        string rootY = Find(y);

        if (rootX == rootY)
        {
            return;
        }

        if (_rank[rootX] < _rank[rootY])
        {
            _parent[rootX] = rootY;
        }
        else if (_rank[rootX] > _rank[rootY])
        {
            _parent[rootY] = rootX;
        }
        else
        {
            _parent[rootY] = rootX;
            _rank[rootX]++;
        }
    }
}
