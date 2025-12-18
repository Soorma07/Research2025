namespace CodingSamples.Core.TransactionAnalysis;

public class SuspiciousAccountDetector : ISuspiciousAccountDetector
{
    private readonly IEnumerable<ISuspiciousActivityRule> _rules;

    public SuspiciousAccountDetector(IEnumerable<ISuspiciousActivityRule> rules)
    {
        _rules = rules ?? throw new ArgumentNullException(nameof(rules));
    }

    public HashSet<string> FindSuspiciousAccounts(IEnumerable<Transaction> transactions)
    {
        var suspicious = new HashSet<string>();
        
        var accountTransactions = transactions
            .GroupBy(t => t.AccountId)
            .ToDictionary(
                g => g.Key,
                g => g.OrderBy(t => t.Timestamp).ToList()
            );
        
        foreach (var (accountId, txns) in accountTransactions)
        {
            if (IsSuspicious(txns))
            {
                suspicious.Add(accountId);
            }
        }
        
        return suspicious;
    }

    private bool IsSuspicious(IReadOnlyList<Transaction> sortedTransactions)
    {
        return _rules.Any(rule => rule.IsSuspicious(sortedTransactions));
    }
}
