namespace CodingSamples.Core.TransactionAnalysis.Rules;

public class HighVelocityRule : ISuspiciousActivityRule
{
    private readonly int _maxTransactions;
    private readonly int _windowSeconds;

    public HighVelocityRule(int maxTransactions = 3, int windowSeconds = 60)
    {
        _maxTransactions = maxTransactions;
        _windowSeconds = windowSeconds;
    }

    public bool IsSuspicious(IReadOnlyList<Transaction> sortedTransactions)
    {
        int n = sortedTransactions.Count;
        
        for (int i = 0; i < n; i++)
        {
            int windowCount = 0;
            
            for (int j = i; j < n; j++)
            {
                if (sortedTransactions[j].Timestamp - sortedTransactions[i].Timestamp <= _windowSeconds)
                {
                    windowCount++;
                }
                else
                {
                    break;
                }
            }
            
            if (windowCount > _maxTransactions)
            {
                return true;
            }
        }
        
        return false;
    }
}
