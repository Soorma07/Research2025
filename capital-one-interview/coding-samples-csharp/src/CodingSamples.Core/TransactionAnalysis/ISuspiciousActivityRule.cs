namespace CodingSamples.Core.TransactionAnalysis;

public interface ISuspiciousActivityRule
{
    bool IsSuspicious(IReadOnlyList<Transaction> sortedTransactions);
}
