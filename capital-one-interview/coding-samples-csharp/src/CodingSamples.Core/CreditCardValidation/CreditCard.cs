namespace CodingSamples.Core.CreditCardValidation;

public record CreditCard(
    string Number,
    int ExpiryMonth,
    int ExpiryYear,
    string Cvv,
    string CardholderName
);
