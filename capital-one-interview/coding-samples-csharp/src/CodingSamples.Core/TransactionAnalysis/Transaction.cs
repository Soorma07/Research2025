namespace CodingSamples.Core.TransactionAnalysis;

public record Transaction(
    string TransactionId,
    string AccountId,
    decimal Amount,
    long Timestamp,
    string City
);
