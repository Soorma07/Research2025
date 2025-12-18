namespace CodingSamples.Core.CreditCardValidation;

public interface IDateTimeProvider
{
    DateTime Now { get; }
}

public class SystemDateTimeProvider : IDateTimeProvider
{
    public DateTime Now => DateTime.Now;
}

public class ExpiryValidator : IExpiryValidator
{
    private readonly IDateTimeProvider _dateTimeProvider;

    public ExpiryValidator(IDateTimeProvider? dateTimeProvider = null)
    {
        _dateTimeProvider = dateTimeProvider ?? new SystemDateTimeProvider();
    }

    public (bool IsValid, string Error) Validate(int month, int year)
    {
        if (month < 1 || month > 12)
        {
            return (false, "Invalid month");
        }

        var current = _dateTimeProvider.Now;
        int currentYear = current.Year;
        int currentMonth = current.Month;

        if (year < 100)
        {
            year += 2000;
        }

        if (year < currentYear)
        {
            return (false, "Card has expired");
        }

        if (year == currentYear && month < currentMonth)
        {
            return (false, "Card has expired");
        }

        if (year > currentYear + 20)
        {
            return (false, "Invalid expiration year");
        }

        return (true, string.Empty);
    }
}
