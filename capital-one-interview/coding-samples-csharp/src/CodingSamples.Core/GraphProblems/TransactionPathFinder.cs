namespace CodingSamples.Core.GraphProblems;

public interface ITransactionPathFinder
{
    (int Hops, List<string> Path) FindShortestPath(
        List<(string Sender, string Receiver, decimal Amount)> transactions,
        string source,
        string target);
}

public class TransactionPathFinder : ITransactionPathFinder
{
    public (int Hops, List<string> Path) FindShortestPath(
        List<(string Sender, string Receiver, decimal Amount)> transactions,
        string source,
        string target)
    {
        var graph = new Dictionary<string, List<string>>();

        foreach (var (sender, receiver, _) in transactions)
        {
            if (!graph.ContainsKey(sender))
            {
                graph[sender] = new List<string>();
            }
            graph[sender].Add(receiver);
        }

        var queue = new Queue<(string Node, List<string> Path)>();
        queue.Enqueue((source, new List<string> { source }));
        var visited = new HashSet<string> { source };

        while (queue.Count > 0)
        {
            var (node, path) = queue.Dequeue();

            if (node == target)
            {
                return (path.Count - 1, path);
            }

            if (graph.TryGetValue(node, out var neighbors))
            {
                foreach (var neighbor in neighbors)
                {
                    if (!visited.Contains(neighbor))
                    {
                        visited.Add(neighbor);
                        var newPath = new List<string>(path) { neighbor };
                        queue.Enqueue((neighbor, newPath));
                    }
                }
            }
        }

        return (-1, new List<string>());
    }
}
