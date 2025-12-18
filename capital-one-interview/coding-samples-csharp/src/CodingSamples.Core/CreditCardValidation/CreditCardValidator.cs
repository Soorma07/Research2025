namespace CodingSamples.Core.CreditCardValidation;

public class CreditCardValidator : ICardValidator
{
    private readonly ILuhnValidator _luhnValidator;
    private readonly ICardTypeIdentifier _cardTypeIdentifier;
    private readonly IExpiryValidator _expiryValidator;
    private readonly ICvvValidator _cvvValidator;

    public CreditCardValidator(
        ILuhnValidator? luhnValidator = null,
        ICardTypeIdentifier? cardTypeIdentifier = null,
        IExpiryValidator? expiryValidator = null,
        ICvvValidator? cvvValidator = null)
    {
        _luhnValidator = luhnValidator ?? new LuhnValidator();
        _cardTypeIdentifier = cardTypeIdentifier ?? new CardTypeIdentifier();
        _expiryValidator = expiryValidator ?? new ExpiryValidator();
        _cvvValidator = cvvValidator ?? new CvvValidator();
    }

    public (bool IsValid, List<string> Errors) Validate(CreditCard card)
    {
        var errors = new List<string>();

        string digits = card.Number.Replace(" ", "").Replace("-", "");
        if (!digits.All(char.IsDigit))
        {
            errors.Add("Card number must contain only digits");
        }
        else if (digits.Length < 13 || digits.Length > 19)
        {
            errors.Add("Card number must be 13-19 digits");
        }
        else if (!_luhnValidator.IsValid(card.Number))
        {
            errors.Add("Invalid card number (checksum failed)");
        }

        var cardType = _cardTypeIdentifier.Identify(card.Number);
        if (cardType == CardType.Unknown)
        {
            errors.Add("Unrecognized card type");
        }

        var (expiryValid, expiryError) = _expiryValidator.Validate(card.ExpiryMonth, card.ExpiryYear);
        if (!expiryValid)
        {
            errors.Add(expiryError);
        }

        var (cvvValid, cvvError) = _cvvValidator.Validate(card.Cvv, cardType);
        if (!cvvValid)
        {
            errors.Add(cvvError);
        }

        if (string.IsNullOrWhiteSpace(card.CardholderName) || card.CardholderName.Trim().Length < 2)
        {
            errors.Add("Invalid cardholder name");
        }

        return (errors.Count == 0, errors);
    }
}
