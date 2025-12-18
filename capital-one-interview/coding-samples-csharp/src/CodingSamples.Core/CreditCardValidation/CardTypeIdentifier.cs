namespace CodingSamples.Core.CreditCardValidation;

public class CardTypeIdentifier : ICardTypeIdentifier
{
    public CardType Identify(string cardNumber)
    {
        string digits = cardNumber.Replace(" ", "").Replace("-", "");

        if (!digits.All(char.IsDigit))
        {
            return CardType.Unknown;
        }

        int length = digits.Length;

        if (digits[0] == '4' && (length == 13 || length == 16 || length == 19))
        {
            return CardType.Visa;
        }

        if (length == 16)
        {
            int prefix2 = int.Parse(digits[..2]);
            int prefix4 = int.Parse(digits[..4]);

            if (prefix2 >= 51 && prefix2 <= 55)
            {
                return CardType.Mastercard;
            }
            if (prefix4 >= 2221 && prefix4 <= 2720)
            {
                return CardType.Mastercard;
            }
        }

        if (length == 15 && (digits[..2] == "34" || digits[..2] == "37"))
        {
            return CardType.Amex;
        }

        if (length >= 16 && length <= 19)
        {
            if (digits[..4] == "6011")
            {
                return CardType.Discover;
            }
            if (digits[..2] == "65")
            {
                return CardType.Discover;
            }
            int prefix3 = int.Parse(digits[..3]);
            if (prefix3 >= 644 && prefix3 <= 649)
            {
                return CardType.Discover;
            }
        }

        return CardType.Unknown;
    }
}
