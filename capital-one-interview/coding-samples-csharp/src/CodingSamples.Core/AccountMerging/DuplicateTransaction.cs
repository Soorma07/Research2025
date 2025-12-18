namespace CodingSamples.Core.AccountMerging;

public record DuplicateTransaction(
    int Id,
    string Source,
    string Target,
    decimal Amount,
    string Category,
    long Time
);

public interface IDuplicateTransactionDetector
{
    List<List<DuplicateTransaction>> FindDuplicateTransactions(List<DuplicateTransaction> transactions);
}

public class DuplicateTransactionDetector : IDuplicateTransactionDetector
{
    private readonly int _timeWindowSeconds;

    public DuplicateTransactionDetector(int timeWindowSeconds = 60)
    {
        _timeWindowSeconds = timeWindowSeconds;
    }

    public List<List<DuplicateTransaction>> FindDuplicateTransactions(List<DuplicateTransaction> transactions)
    {
        var sortedTxns = transactions
            .OrderBy(t => (t.Source, t.Target, t.Amount, t.Category))
            .ThenBy(t => t.Time)
            .ToList();

        var duplicates = new List<List<DuplicateTransaction>>();

        var groups = sortedTxns.GroupBy(t => (t.Source, t.Target, t.Amount, t.Category));

        foreach (var group in groups)
        {
            var groupList = group.ToList();

            if (groupList.Count < 2)
            {
                continue;
            }

            int i = 0;
            while (i < groupList.Count)
            {
                var cluster = new List<DuplicateTransaction> { groupList[i] };
                int j = i + 1;

                while (j < groupList.Count)
                {
                    bool withinWindow = cluster.Any(t => Math.Abs(groupList[j].Time - t.Time) <= _timeWindowSeconds);
                    if (withinWindow)
                    {
                        cluster.Add(groupList[j]);
                        j++;
                    }
                    else
                    {
                        break;
                    }
                }

                if (cluster.Count > 1)
                {
                    duplicates.Add(cluster);
                }

                i = j;
            }
        }

        return duplicates;
    }
}
