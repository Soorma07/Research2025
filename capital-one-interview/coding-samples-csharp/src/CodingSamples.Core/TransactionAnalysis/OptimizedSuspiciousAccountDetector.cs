namespace CodingSamples.Core.TransactionAnalysis;

public class OptimizedSuspiciousAccountDetector : ISuspiciousAccountDetector
{
    private readonly int _maxTransactionsIn60Seconds;
    private readonly decimal _maxAmountIn60Seconds;
    private readonly int _maxCitiesIn10Minutes;

    public OptimizedSuspiciousAccountDetector(
        int maxTransactionsIn60Seconds = 3,
        decimal maxAmountIn60Seconds = 10000m,
        int maxCitiesIn10Minutes = 2)
    {
        _maxTransactionsIn60Seconds = maxTransactionsIn60Seconds;
        _maxAmountIn60Seconds = maxAmountIn60Seconds;
        _maxCitiesIn10Minutes = maxCitiesIn10Minutes;
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
            if (IsSuspiciousOptimized(txns))
            {
                suspicious.Add(accountId);
            }
        }
        
        return suspicious;
    }

    private bool IsSuspiciousOptimized(List<Transaction> txns)
    {
        int left = 0;
        decimal windowAmount = 0m;
        
        for (int right = 0; right < txns.Count; right++)
        {
            windowAmount += txns[right].Amount;
            
            while (txns[right].Timestamp - txns[left].Timestamp > 60)
            {
                windowAmount -= txns[left].Amount;
                left++;
            }
            
            int windowSize = right - left + 1;
            
            if (windowSize > _maxTransactionsIn60Seconds || windowAmount > _maxAmountIn60Seconds)
            {
                return true;
            }
        }
        
        left = 0;
        var cities = new Dictionary<string, int>();
        
        for (int right = 0; right < txns.Count; right++)
        {
            if (!cities.ContainsKey(txns[right].City))
            {
                cities[txns[right].City] = 0;
            }
            cities[txns[right].City]++;
            
            while (txns[right].Timestamp - txns[left].Timestamp > 600)
            {
                cities[txns[left].City]--;
                if (cities[txns[left].City] == 0)
                {
                    cities.Remove(txns[left].City);
                }
                left++;
            }
            
            if (cities.Count > _maxCitiesIn10Minutes)
            {
                return true;
            }
        }
        
        return false;
    }
}
