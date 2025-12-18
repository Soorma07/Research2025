namespace CodingSamples.Core.TransactionAnalysis;

public interface ISuspiciousAccountDetector
{
    HashSet<string> FindSuspiciousAccounts(IEnumerable<Transaction> transactions);
}
