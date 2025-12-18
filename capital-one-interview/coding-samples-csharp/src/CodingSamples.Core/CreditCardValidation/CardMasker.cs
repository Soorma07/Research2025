using System.Text;

namespace CodingSamples.Core.CreditCardValidation;

public static class CardMasker
{
    public static string Mask(string cardNumber, int visibleDigits = 4)
    {
        string digits = cardNumber.Replace(" ", "").Replace("-", "");

        if (digits.Length < visibleDigits)
        {
            return new string('*', digits.Length);
        }

        string masked = new string('*', digits.Length - visibleDigits) + digits[^visibleDigits..];

        var result = new StringBuilder();
        for (int i = 0; i < masked.Length; i++)
        {
            if (i > 0 && i % 4 == 0)
            {
                result.Append(' ');
            }
            result.Append(masked[i]);
        }

        return result.ToString();
    }
}

public static class TestCardGenerator
{
    private static readonly Dictionary<CardType, string> TestCards = new()
    {
        { CardType.Visa, "4111111111111111" },
        { CardType.Mastercard, "5500000000000004" },
        { CardType.Amex, "340000000000009" },
        { CardType.Discover, "6011000000000004" }
    };

    public static string Generate(CardType cardType)
    {
        return TestCards.GetValueOrDefault(cardType, string.Empty);
    }
}
