namespace CodingSamples.Core.GraphProblems;

public class Graph<TNode> : IGraph<TNode> where TNode : notnull
{
    private readonly bool _directed;
    private readonly Dictionary<TNode, List<(TNode Neighbor, int Weight)>> _adj = new();
    private readonly HashSet<TNode> _nodes = new();

    public Graph(bool directed = true)
    {
        _directed = directed;
    }

    public void AddEdge(TNode u, TNode v, int weight = 1)
    {
        if (!_adj.ContainsKey(u))
        {
            _adj[u] = new List<(TNode, int)>();
        }
        _adj[u].Add((v, weight));
        _nodes.Add(u);
        _nodes.Add(v);

        if (!_directed)
        {
            if (!_adj.ContainsKey(v))
            {
                _adj[v] = new List<(TNode, int)>();
            }
            _adj[v].Add((u, weight));
        }
    }

    public List<TNode> Bfs(TNode start)
    {
        var visited = new HashSet<TNode>();
        var result = new List<TNode>();
        var queue = new Queue<TNode>();
        queue.Enqueue(start);

        while (queue.Count > 0)
        {
            var node = queue.Dequeue();
            if (visited.Contains(node))
            {
                continue;
            }

            visited.Add(node);
            result.Add(node);

            if (_adj.TryGetValue(node, out var neighbors))
            {
                foreach (var (neighbor, _) in neighbors)
                {
                    if (!visited.Contains(neighbor))
                    {
                        queue.Enqueue(neighbor);
                    }
                }
            }
        }

        return result;
    }

    public List<TNode> Dfs(TNode start)
    {
        var visited = new HashSet<TNode>();
        var result = new List<TNode>();

        void DfsHelper(TNode node)
        {
            if (visited.Contains(node))
            {
                return;
            }

            visited.Add(node);
            result.Add(node);

            if (_adj.TryGetValue(node, out var neighbors))
            {
                foreach (var (neighbor, _) in neighbors)
                {
                    DfsHelper(neighbor);
                }
            }
        }

        DfsHelper(start);
        return result;
    }

    public (int Distance, List<TNode> Path) ShortestPathDijkstra(TNode start, TNode end)
    {
        var distances = new Dictionary<TNode, int>();
        var previous = new Dictionary<TNode, TNode?>();

        foreach (var node in _nodes)
        {
            distances[node] = int.MaxValue;
            previous[node] = default;
        }
        distances[start] = 0;

        var pq = new PriorityQueue<TNode, int>();
        pq.Enqueue(start, 0);
        var visited = new HashSet<TNode>();

        while (pq.Count > 0)
        {
            var node = pq.Dequeue();

            if (visited.Contains(node))
            {
                continue;
            }
            visited.Add(node);

            if (EqualityComparer<TNode>.Default.Equals(node, end))
            {
                break;
            }

            if (_adj.TryGetValue(node, out var neighbors))
            {
                foreach (var (neighbor, weight) in neighbors)
                {
                    if (visited.Contains(neighbor))
                    {
                        continue;
                    }

                    int newDist = distances[node] + weight;
                    if (newDist < distances[neighbor])
                    {
                        distances[neighbor] = newDist;
                        previous[neighbor] = node;
                        pq.Enqueue(neighbor, newDist);
                    }
                }
            }
        }

        var path = new List<TNode>();
        TNode? current = end;
        while (current != null)
        {
            path.Add(current);
            current = previous.GetValueOrDefault(current);
        }
        path.Reverse();

        return (distances[end], path);
    }

    public bool HasCycle()
    {
        const int WHITE = 0, GRAY = 1, BLACK = 2;
        var color = new Dictionary<TNode, int>();

        foreach (var node in _nodes)
        {
            color[node] = WHITE;
        }

        bool DfsCycle(TNode node)
        {
            color[node] = GRAY;

            if (_adj.TryGetValue(node, out var neighbors))
            {
                foreach (var (neighbor, _) in neighbors)
                {
                    if (color[neighbor] == GRAY)
                    {
                        return true;
                    }
                    if (color[neighbor] == WHITE && DfsCycle(neighbor))
                    {
                        return true;
                    }
                }
            }

            color[node] = BLACK;
            return false;
        }

        foreach (var node in _nodes)
        {
            if (color[node] == WHITE)
            {
                if (DfsCycle(node))
                {
                    return true;
                }
            }
        }

        return false;
    }

    public List<TNode> TopologicalSort()
    {
        var inDegree = new Dictionary<TNode, int>();
        foreach (var node in _nodes)
        {
            inDegree[node] = 0;
        }

        foreach (var node in _nodes)
        {
            if (_adj.TryGetValue(node, out var neighbors))
            {
                foreach (var (neighbor, _) in neighbors)
                {
                    inDegree[neighbor]++;
                }
            }
        }

        var queue = new Queue<TNode>();
        foreach (var node in _nodes)
        {
            if (inDegree[node] == 0)
            {
                queue.Enqueue(node);
            }
        }

        var result = new List<TNode>();
        while (queue.Count > 0)
        {
            var node = queue.Dequeue();
            result.Add(node);

            if (_adj.TryGetValue(node, out var neighbors))
            {
                foreach (var (neighbor, _) in neighbors)
                {
                    inDegree[neighbor]--;
                    if (inDegree[neighbor] == 0)
                    {
                        queue.Enqueue(neighbor);
                    }
                }
            }
        }

        if (result.Count != _nodes.Count)
        {
            return new List<TNode>();
        }

        return result;
    }
}
