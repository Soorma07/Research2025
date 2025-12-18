namespace CodingSamples.Core.GraphProblems;

public interface IPageRankCalculator
{
    Dictionary<string, double> Calculate(
        List<(string Sender, string Receiver, decimal Amount)> transactions,
        double damping = 0.85,
        int iterations = 100);
}

public class PageRankCalculator : IPageRankCalculator
{
    public Dictionary<string, double> Calculate(
        List<(string Sender, string Receiver, decimal Amount)> transactions,
        double damping = 0.85,
        int iterations = 100)
    {
        var graph = new Dictionary<string, List<string>>();
        var allAccounts = new HashSet<string>();

        foreach (var (sender, receiver, _) in transactions)
        {
            if (!graph.ContainsKey(sender))
            {
                graph[sender] = new List<string>();
            }
            graph[sender].Add(receiver);
            allAccounts.Add(sender);
            allAccounts.Add(receiver);
        }

        int n = allAccounts.Count;
        var accounts = allAccounts.ToList();

        var pr = new Dictionary<string, double>();
        foreach (var acc in accounts)
        {
            pr[acc] = 1.0 / n;
        }

        for (int i = 0; i < iterations; i++)
        {
            var newPr = new Dictionary<string, double>();

            foreach (var acc in accounts)
            {
                double incomingPr = 0.0;
                foreach (var sender in accounts)
                {
                    if (graph.TryGetValue(sender, out var receivers) && receivers.Contains(acc))
                    {
                        int outDegree = receivers.Count;
                        if (outDegree > 0)
                        {
                            incomingPr += pr[sender] / outDegree;
                        }
                    }
                }

                newPr[acc] = (1 - damping) / n + damping * incomingPr;
            }

            pr = newPr;
        }

        return pr;
    }
}
