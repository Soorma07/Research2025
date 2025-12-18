"""
Unit tests for credit card validation module.
Run with: pytest tests/test_credit_card_validation.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from importlib.machinery import SourceFileLoader

# Load the module with numeric prefix
credit_card = SourceFileLoader(
    "credit_card_validation",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "05_credit_card_validation.py")
).load_module()

CardType = credit_card.CardType
CreditCard = credit_card.CreditCard
luhn_checksum = credit_card.luhn_checksum
identify_card_type = credit_card.identify_card_type
mask_card_number = credit_card.mask_card_number
validate_expiry = credit_card.validate_expiry
validate_cvv = credit_card.validate_cvv
CreditCardValidator = credit_card.CreditCardValidator
generate_test_card = credit_card.generate_test_card


class TestLuhnChecksum:
    """Test cases for Luhn algorithm validation."""
    
    def test_valid_visa(self):
        """Test valid Visa test card number."""
        assert luhn_checksum("4111111111111111"), "Visa test card should be valid"
    
    def test_valid_mastercard(self):
        """Test valid Mastercard test card number."""
        assert luhn_checksum("5500000000000004"), "Mastercard test card should be valid"
    
    def test_valid_amex(self):
        """Test valid Amex test card number."""
        assert luhn_checksum("340000000000009"), "Amex test card should be valid"
    
    def test_valid_discover(self):
        """Test valid Discover test card number."""
        assert luhn_checksum("6011000000000004"), "Discover test card should be valid"
    
    def test_invalid_checksum(self):
        """Test card number with invalid checksum."""
        assert not luhn_checksum("4111111111111112"), "Should fail checksum"
    
    def test_random_number_invalid(self):
        """Test random number fails checksum."""
        assert not luhn_checksum("1234567890123456"), "Random number should fail"
    
    def test_with_spaces(self):
        """Test card number with spaces."""
        assert luhn_checksum("4111 1111 1111 1111"), "Should handle spaces"
    
    def test_with_dashes(self):
        """Test card number with dashes."""
        assert luhn_checksum("4111-1111-1111-1111"), "Should handle dashes"
    
    def test_non_numeric_invalid(self):
        """Test non-numeric input is invalid."""
        assert not luhn_checksum("4111-1111-1111-111a"), "Non-numeric should be invalid"


class TestIdentifyCardType:
    """Test cases for card type identification."""
    
    def test_visa(self):
        """Test Visa card identification."""
        assert identify_card_type("4111111111111111") == CardType.VISA
    
    def test_mastercard_51_prefix(self):
        """Test Mastercard with 51 prefix."""
        assert identify_card_type("5100000000000000") == CardType.MASTERCARD
    
    def test_mastercard_55_prefix(self):
        """Test Mastercard with 55 prefix."""
        assert identify_card_type("5500000000000004") == CardType.MASTERCARD
    
    def test_amex_34_prefix(self):
        """Test Amex with 34 prefix."""
        assert identify_card_type("340000000000009") == CardType.AMEX
    
    def test_amex_37_prefix(self):
        """Test Amex with 37 prefix."""
        assert identify_card_type("370000000000002") == CardType.AMEX
    
    def test_discover_6011_prefix(self):
        """Test Discover with 6011 prefix."""
        assert identify_card_type("6011000000000004") == CardType.DISCOVER
    
    def test_discover_65_prefix(self):
        """Test Discover with 65 prefix."""
        assert identify_card_type("6500000000000000") == CardType.DISCOVER
    
    def test_unknown_card(self):
        """Test unknown card type."""
        assert identify_card_type("1234567890123456") == CardType.UNKNOWN
    
    def test_invalid_length(self):
        """Test card with invalid length."""
        assert identify_card_type("411111111111") == CardType.UNKNOWN  # Too short


class TestMaskCardNumber:
    """Test cases for card number masking."""
    
    def test_mask_16_digit(self):
        """Test masking 16-digit card number."""
        result = mask_card_number("4111111111111111")
        assert result == "**** **** **** 1111"
    
    def test_mask_15_digit(self):
        """Test masking 15-digit card number (Amex)."""
        result = mask_card_number("340000000000009")
        assert "009" in result, "Last 4 digits should be visible"
        assert "*" in result, "Should contain masked characters"
    
    def test_mask_with_spaces(self):
        """Test masking card number with spaces."""
        result = mask_card_number("4111 1111 1111 1111")
        assert "1111" in result, "Last 4 digits should be visible"
    
    def test_custom_visible_digits(self):
        """Test custom number of visible digits."""
        result = mask_card_number("4111111111111111", visible_digits=6)
        assert "11 1111" in result, "Last 6 digits should be visible (formatted with spaces)"


class TestValidateExpiry:
    """Test cases for expiry date validation."""
    
    def test_valid_future_date(self):
        """Test valid future expiry date."""
        is_valid, error = validate_expiry(12, 2027)
        assert is_valid, f"Future date should be valid: {error}"
    
    def test_expired_year(self):
        """Test expired year."""
        is_valid, error = validate_expiry(12, 2020)
        assert not is_valid, "Past year should be invalid"
        assert "expired" in error.lower()
    
    def test_invalid_month(self):
        """Test invalid month."""
        is_valid, error = validate_expiry(13, 2027)
        assert not is_valid, "Month 13 should be invalid"
        assert "month" in error.lower()
    
    def test_two_digit_year(self):
        """Test two-digit year format."""
        is_valid, error = validate_expiry(12, 27)
        assert is_valid, f"Two-digit year should work: {error}"
    
    def test_far_future_invalid(self):
        """Test too far in future is invalid."""
        is_valid, error = validate_expiry(12, 2050)
        assert not is_valid, "Too far in future should be invalid"


class TestValidateCVV:
    """Test cases for CVV validation."""
    
    def test_valid_3_digit_cvv(self):
        """Test valid 3-digit CVV for non-Amex."""
        is_valid, error = validate_cvv("123", CardType.VISA)
        assert is_valid, f"3-digit CVV should be valid for Visa: {error}"
    
    def test_valid_4_digit_cvv_amex(self):
        """Test valid 4-digit CVV for Amex."""
        is_valid, error = validate_cvv("1234", CardType.AMEX)
        assert is_valid, f"4-digit CVV should be valid for Amex: {error}"
    
    def test_invalid_3_digit_for_amex(self):
        """Test 3-digit CVV is invalid for Amex."""
        is_valid, error = validate_cvv("123", CardType.AMEX)
        assert not is_valid, "3-digit CVV should be invalid for Amex"
    
    def test_invalid_4_digit_for_visa(self):
        """Test 4-digit CVV is invalid for Visa."""
        is_valid, error = validate_cvv("1234", CardType.VISA)
        assert not is_valid, "4-digit CVV should be invalid for Visa"
    
    def test_non_numeric_cvv(self):
        """Test non-numeric CVV is invalid."""
        is_valid, error = validate_cvv("12a", CardType.VISA)
        assert not is_valid, "Non-numeric CVV should be invalid"


class TestCreditCardValidator:
    """Test cases for full credit card validation."""
    
    def test_valid_card(self):
        """Test validation of a valid card."""
        card = CreditCard(
            number="4111111111111111",
            expiry_month=12,
            expiry_year=2027,
            cvv="123",
            cardholder_name="John Doe"
        )
        is_valid, errors = CreditCardValidator.validate(card)
        assert is_valid, f"Valid card should pass: {errors}"
    
    def test_invalid_card_number(self):
        """Test validation with invalid card number."""
        card = CreditCard(
            number="4111111111111112",  # Invalid checksum
            expiry_month=12,
            expiry_year=2027,
            cvv="123",
            cardholder_name="John Doe"
        )
        is_valid, errors = CreditCardValidator.validate(card)
        assert not is_valid, "Invalid card number should fail"
        assert any("checksum" in e.lower() for e in errors)
    
    def test_expired_card(self):
        """Test validation with expired card."""
        card = CreditCard(
            number="4111111111111111",
            expiry_month=1,
            expiry_year=2020,
            cvv="123",
            cardholder_name="John Doe"
        )
        is_valid, errors = CreditCardValidator.validate(card)
        assert not is_valid, "Expired card should fail"
        assert any("expired" in e.lower() for e in errors)
    
    def test_empty_cardholder_name(self):
        """Test validation with empty cardholder name."""
        card = CreditCard(
            number="4111111111111111",
            expiry_month=12,
            expiry_year=2027,
            cvv="123",
            cardholder_name=""
        )
        is_valid, errors = CreditCardValidator.validate(card)
        assert not is_valid, "Empty cardholder name should fail"


class TestGenerateTestCard:
    """Test cases for test card generation."""
    
    def test_generate_visa(self):
        """Test generating Visa test card."""
        card = generate_test_card(CardType.VISA)
        assert luhn_checksum(card), "Generated card should pass Luhn check"
        assert identify_card_type(card) == CardType.VISA
    
    def test_generate_mastercard(self):
        """Test generating Mastercard test card."""
        card = generate_test_card(CardType.MASTERCARD)
        assert luhn_checksum(card), "Generated card should pass Luhn check"
        assert identify_card_type(card) == CardType.MASTERCARD
    
    def test_generate_amex(self):
        """Test generating Amex test card."""
        card = generate_test_card(CardType.AMEX)
        assert luhn_checksum(card), "Generated card should pass Luhn check"
        assert identify_card_type(card) == CardType.AMEX


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
