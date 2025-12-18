namespace CodingSamples.Core.CreditCardValidation;

public class LuhnValidator : ILuhnValidator
{
    public bool IsValid(string cardNumber)
    {
        string digits = cardNumber.Replace(" ", "").Replace("-", "");

        if (!digits.All(char.IsDigit))
        {
            return false;
        }

        int total = 0;
        bool isSecond = false;

        for (int i = digits.Length - 1; i >= 0; i--)
        {
            int digit = digits[i] - '0';

            if (isSecond)
            {
                digit *= 2;
                if (digit > 9)
                {
                    digit -= 9;
                }
            }

            total += digit;
            isSecond = !isSecond;
        }

        return total % 10 == 0;
    }
}
