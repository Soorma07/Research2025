namespace CodingSamples.Core.TransactionAnalysis.Rules;

public class MultipleCitiesRule : ISuspiciousActivityRule
{
    private readonly int _maxCities;
    private readonly int _windowSeconds;

    public MultipleCitiesRule(int maxCities = 2, int windowSeconds = 600)
    {
        _maxCities = maxCities;
        _windowSeconds = windowSeconds;
    }

    public bool IsSuspicious(IReadOnlyList<Transaction> sortedTransactions)
    {
        int n = sortedTransactions.Count;
        
        for (int i = 0; i < n; i++)
        {
            var citiesInWindow = new HashSet<string>();
            
            for (int j = i; j < n; j++)
            {
                if (sortedTransactions[j].Timestamp - sortedTransactions[i].Timestamp <= _windowSeconds)
                {
                    citiesInWindow.Add(sortedTransactions[j].City);
                }
                else
                {
                    break;
                }
            }
            
            if (citiesInWindow.Count > _maxCities)
            {
                return true;
            }
        }
        
        return false;
    }
}
