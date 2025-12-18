using CodingSamples.Core.CreditCardValidation;

namespace CodingSamples.Tests.CreditCardValidation;

public class LuhnValidatorTests
{
    private readonly ILuhnValidator _validator = new LuhnValidator();

    [Theory]
    [InlineData("4111111111111111")]
    [InlineData("5500000000000004")]
    [InlineData("340000000000009")]
    [InlineData("6011000000000004")]
    public void IsValid_ValidTestCards_ReturnsTrue(string cardNumber)
    {
        Assert.True(_validator.IsValid(cardNumber));
    }

    [Theory]
    [InlineData("4111111111111112")]
    [InlineData("1234567890123456")]
    public void IsValid_InvalidChecksum_ReturnsFalse(string cardNumber)
    {
        Assert.False(_validator.IsValid(cardNumber));
    }

    [Fact]
    public void IsValid_NonDigitCharacters_ReturnsFalse()
    {
        Assert.False(_validator.IsValid("4111-1111-1111-111a"));
    }

    [Fact]
    public void IsValid_WithSpaces_ReturnsTrue()
    {
        Assert.True(_validator.IsValid("4111 1111 1111 1111"));
    }

    [Fact]
    public void IsValid_WithDashes_ReturnsTrue()
    {
        Assert.True(_validator.IsValid("4111-1111-1111-1111"));
    }
}

public class CardTypeIdentifierTests
{
    private readonly ICardTypeIdentifier _identifier = new CardTypeIdentifier();

    [Fact]
    public void Identify_VisaCard_ReturnsVisa()
    {
        Assert.Equal(CardType.Visa, _identifier.Identify("4111111111111111"));
    }

    [Fact]
    public void Identify_MastercardCard_ReturnsMastercard()
    {
        Assert.Equal(CardType.Mastercard, _identifier.Identify("5500000000000004"));
    }

    [Fact]
    public void Identify_AmexCard_ReturnsAmex()
    {
        Assert.Equal(CardType.Amex, _identifier.Identify("340000000000009"));
    }

    [Fact]
    public void Identify_DiscoverCard_ReturnsDiscover()
    {
        Assert.Equal(CardType.Discover, _identifier.Identify("6011000000000004"));
    }

    [Fact]
    public void Identify_UnknownCard_ReturnsUnknown()
    {
        Assert.Equal(CardType.Unknown, _identifier.Identify("1234567890123456"));
    }
}

public class MockDateTimeProvider : IDateTimeProvider
{
    public DateTime Now { get; set; } = new DateTime(2025, 6, 15);
}

public class ExpiryValidatorTests
{
    private readonly MockDateTimeProvider _dateTimeProvider = new() { Now = new DateTime(2025, 6, 15) };
    private readonly IExpiryValidator _validator;

    public ExpiryValidatorTests()
    {
        _validator = new ExpiryValidator(_dateTimeProvider);
    }

    [Fact]
    public void Validate_ValidFutureDate_ReturnsTrue()
    {
        var (isValid, _) = _validator.Validate(12, 2027);
        Assert.True(isValid);
    }

    [Fact]
    public void Validate_ExpiredYear_ReturnsFalse()
    {
        var (isValid, error) = _validator.Validate(1, 2020);
        Assert.False(isValid);
        Assert.Contains("expired", error.ToLower());
    }

    [Fact]
    public void Validate_ExpiredMonth_ReturnsFalse()
    {
        var (isValid, error) = _validator.Validate(1, 2025);
        Assert.False(isValid);
        Assert.Contains("expired", error.ToLower());
    }

    [Fact]
    public void Validate_InvalidMonth_ReturnsFalse()
    {
        var (isValid, error) = _validator.Validate(13, 2027);
        Assert.False(isValid);
        Assert.Contains("month", error.ToLower());
    }

    [Fact]
    public void Validate_TwoDigitYear_ConvertsCorrectly()
    {
        var (isValid, _) = _validator.Validate(12, 27);
        Assert.True(isValid);
    }

    [Fact]
    public void Validate_TooFarInFuture_ReturnsFalse()
    {
        var (isValid, error) = _validator.Validate(12, 2050);
        Assert.False(isValid);
        Assert.Contains("year", error.ToLower());
    }
}

public class CvvValidatorTests
{
    private readonly ICvvValidator _validator = new CvvValidator();

    [Fact]
    public void Validate_ThreeDigitCvv_ForVisa_ReturnsTrue()
    {
        var (isValid, _) = _validator.Validate("123", CardType.Visa);
        Assert.True(isValid);
    }

    [Fact]
    public void Validate_FourDigitCvv_ForAmex_ReturnsTrue()
    {
        var (isValid, _) = _validator.Validate("1234", CardType.Amex);
        Assert.True(isValid);
    }

    [Fact]
    public void Validate_ThreeDigitCvv_ForAmex_ReturnsFalse()
    {
        var (isValid, error) = _validator.Validate("123", CardType.Amex);
        Assert.False(isValid);
        Assert.Contains("4 digits", error);
    }

    [Fact]
    public void Validate_FourDigitCvv_ForVisa_ReturnsFalse()
    {
        var (isValid, error) = _validator.Validate("1234", CardType.Visa);
        Assert.False(isValid);
        Assert.Contains("3 digits", error);
    }

    [Fact]
    public void Validate_NonDigitCvv_ReturnsFalse()
    {
        var (isValid, error) = _validator.Validate("12a", CardType.Visa);
        Assert.False(isValid);
        Assert.Contains("only digits", error);
    }
}

public class CreditCardValidatorTests
{
    private readonly ICardValidator _validator;

    public CreditCardValidatorTests()
    {
        var dateTimeProvider = new MockDateTimeProvider { Now = new DateTime(2025, 6, 15) };
        _validator = new CreditCardValidator(
            expiryValidator: new ExpiryValidator(dateTimeProvider)
        );
    }

    [Fact]
    public void Validate_ValidCard_ReturnsTrue()
    {
        var card = new CreditCard(
            Number: "4111111111111111",
            ExpiryMonth: 12,
            ExpiryYear: 2027,
            Cvv: "123",
            CardholderName: "John Doe"
        );

        var (isValid, errors) = _validator.Validate(card);

        Assert.True(isValid);
        Assert.Empty(errors);
    }

    [Fact]
    public void Validate_ExpiredCard_ReturnsFalse()
    {
        var card = new CreditCard(
            Number: "4111111111111111",
            ExpiryMonth: 1,
            ExpiryYear: 2020,
            Cvv: "123",
            CardholderName: "John Doe"
        );

        var (isValid, errors) = _validator.Validate(card);

        Assert.False(isValid);
        Assert.Contains(errors, e => e.ToLower().Contains("expired"));
    }

    [Fact]
    public void Validate_InvalidChecksum_ReturnsFalse()
    {
        var card = new CreditCard(
            Number: "4111111111111112",
            ExpiryMonth: 12,
            ExpiryYear: 2027,
            Cvv: "123",
            CardholderName: "John Doe"
        );

        var (isValid, errors) = _validator.Validate(card);

        Assert.False(isValid);
        Assert.Contains(errors, e => e.ToLower().Contains("checksum"));
    }

    [Fact]
    public void Validate_InvalidCardholderName_ReturnsFalse()
    {
        var card = new CreditCard(
            Number: "4111111111111111",
            ExpiryMonth: 12,
            ExpiryYear: 2027,
            Cvv: "123",
            CardholderName: ""
        );

        var (isValid, errors) = _validator.Validate(card);

        Assert.False(isValid);
        Assert.Contains(errors, e => e.ToLower().Contains("cardholder"));
    }
}

public class CardMaskerTests
{
    [Fact]
    public void Mask_StandardCard_MasksCorrectly()
    {
        string masked = CardMasker.Mask("4111111111111111");
        Assert.Equal("**** **** **** 1111", masked);
    }

    [Fact]
    public void Mask_AmexCard_MasksCorrectly()
    {
        string masked = CardMasker.Mask("340000000000009");
        Assert.Equal("**** **** ***0 009", masked);
    }

    [Fact]
    public void Mask_ShortNumber_MasksAll()
    {
        string masked = CardMasker.Mask("123");
        Assert.Equal("***", masked);
    }
}

public class TestCardGeneratorTests
{
    [Theory]
    [InlineData(CardType.Visa, "4111111111111111")]
    [InlineData(CardType.Mastercard, "5500000000000004")]
    [InlineData(CardType.Amex, "340000000000009")]
    [InlineData(CardType.Discover, "6011000000000004")]
    public void Generate_KnownCardType_ReturnsTestCard(CardType cardType, string expected)
    {
        Assert.Equal(expected, TestCardGenerator.Generate(cardType));
    }

    [Fact]
    public void Generate_UnknownCardType_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, TestCardGenerator.Generate(CardType.Unknown));
    }
}
