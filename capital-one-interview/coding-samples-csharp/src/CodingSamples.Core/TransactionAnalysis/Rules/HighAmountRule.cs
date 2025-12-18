namespace CodingSamples.Core.TransactionAnalysis.Rules;

public class HighAmountRule : ISuspiciousActivityRule
{
    private readonly decimal _maxAmount;
    private readonly int _windowSeconds;

    public HighAmountRule(decimal maxAmount = 10000m, int windowSeconds = 60)
    {
        _maxAmount = maxAmount;
        _windowSeconds = windowSeconds;
    }

    public bool IsSuspicious(IReadOnlyList<Transaction> sortedTransactions)
    {
        int n = sortedTransactions.Count;
        
        for (int i = 0; i < n; i++)
        {
            decimal windowAmount = 0m;
            
            for (int j = i; j < n; j++)
            {
                if (sortedTransactions[j].Timestamp - sortedTransactions[i].Timestamp <= _windowSeconds)
                {
                    windowAmount += sortedTransactions[j].Amount;
                }
                else
                {
                    break;
                }
            }
            
            if (windowAmount > _maxAmount)
            {
                return true;
            }
        }
        
        return false;
    }
}
