namespace CodingSamples.Core.GraphProblems;

public interface IFraudRingDetector
{
    List<HashSet<string>> FindFraudRings(List<(string Sender, string Receiver, decimal Amount)> transactions);
}

public class FraudRingDetector : IFraudRingDetector
{
    public List<HashSet<string>> FindFraudRings(List<(string Sender, string Receiver, decimal Amount)> transactions)
    {
        var graph = new Dictionary<string, HashSet<string>>();
        var allAccounts = new HashSet<string>();

        foreach (var (sender, receiver, _) in transactions)
        {
            if (!graph.ContainsKey(sender))
            {
                graph[sender] = new HashSet<string>();
            }
            graph[sender].Add(receiver);
            allAccounts.Add(sender);
            allAccounts.Add(receiver);
        }

        var indexCounter = 0;
        var stack = new Stack<string>();
        var lowlinks = new Dictionary<string, int>();
        var index = new Dictionary<string, int>();
        var onStack = new Dictionary<string, bool>();
        var sccs = new List<HashSet<string>>();

        void StrongConnect(string node)
        {
            index[node] = indexCounter;
            lowlinks[node] = indexCounter;
            indexCounter++;
            stack.Push(node);
            onStack[node] = true;

            if (graph.TryGetValue(node, out var neighbors))
            {
                foreach (var neighbor in neighbors)
                {
                    if (!index.ContainsKey(neighbor))
                    {
                        StrongConnect(neighbor);
                        lowlinks[node] = Math.Min(lowlinks[node], lowlinks[neighbor]);
                    }
                    else if (onStack.GetValueOrDefault(neighbor, false))
                    {
                        lowlinks[node] = Math.Min(lowlinks[node], index[neighbor]);
                    }
                }
            }

            if (lowlinks[node] == index[node])
            {
                var scc = new HashSet<string>();
                while (true)
                {
                    var w = stack.Pop();
                    onStack[w] = false;
                    scc.Add(w);
                    if (w == node)
                    {
                        break;
                    }
                }

                if (scc.Count > 1)
                {
                    sccs.Add(scc);
                }
            }
        }

        foreach (var account in allAccounts)
        {
            if (!index.ContainsKey(account))
            {
                StrongConnect(account);
            }
        }

        return sccs;
    }
}
