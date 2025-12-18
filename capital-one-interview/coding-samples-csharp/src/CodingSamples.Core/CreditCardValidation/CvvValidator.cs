namespace CodingSamples.Core.CreditCardValidation;

public class CvvValidator : ICvvValidator
{
    public (bool IsValid, string Error) Validate(string cvv, CardType cardType)
    {
        if (!cvv.All(char.IsDigit))
        {
            return (false, "CVV must contain only digits");
        }

        int expectedLength = cardType == CardType.Amex ? 4 : 3;

        if (cvv.Length != expectedLength)
        {
            return (false, $"CVV must be {expectedLength} digits for {cardType}");
        }

        return (true, string.Empty);
    }
}
