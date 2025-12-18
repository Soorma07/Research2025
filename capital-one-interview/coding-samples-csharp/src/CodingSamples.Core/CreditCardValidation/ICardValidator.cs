namespace CodingSamples.Core.CreditCardValidation;

public interface ICardValidator
{
    (bool IsValid, List<string> Errors) Validate(CreditCard card);
}

public interface ILuhnValidator
{
    bool IsValid(string cardNumber);
}

public interface ICardTypeIdentifier
{
    CardType Identify(string cardNumber);
}

public interface IExpiryValidator
{
    (bool IsValid, string Error) Validate(int month, int year);
}

public interface ICvvValidator
{
    (bool IsValid, string Error) Validate(string cvv, CardType cardType);
}
