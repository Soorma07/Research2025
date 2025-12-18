"""
Capital One Coding Sample: Credit Card Validation & Processing

This problem is directly relevant to Capital One's business domain.
Tests understanding of:
- String manipulation and validation
- Luhn algorithm (checksum validation)
- Object-oriented design
- Error handling

Common interview topics around credit cards:
1. Validate card number (Luhn algorithm)
2. Identify card type from number
3. Mask card number for display
4. Parse and validate expiration dates
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
import re


class CardType(Enum):
    VISA = "Visa"
    MASTERCARD = "Mastercard"
    AMEX = "American Express"
    DISCOVER = "Discover"
    UNKNOWN = "Unknown"


@dataclass
class CreditCard:
    number: str
    expiry_month: int
    expiry_year: int
    cvv: str
    cardholder_name: str


def luhn_checksum(card_number: str) -> bool:
    """
    Validate card number using Luhn algorithm (mod 10).
    
    Algorithm:
    1. From right to left, double every second digit
    2. If doubling results in > 9, subtract 9
    3. Sum all digits
    4. Valid if sum % 10 == 0
    
    Time Complexity: O(n) where n is length of card number
    Space Complexity: O(1)
    """
    # Remove spaces and dashes
    digits = card_number.replace(" ", "").replace("-", "")
    
    if not digits.isdigit():
        return False
    
    total = 0
    is_second = False
    
    # Process from right to left
    for char in reversed(digits):
        digit = int(char)
        
        if is_second:
            digit *= 2
            if digit > 9:
                digit -= 9
        
        total += digit
        is_second = not is_second
    
    return total % 10 == 0


def identify_card_type(card_number: str) -> CardType:
    """
    Identify card type based on IIN (Issuer Identification Number).
    
    Card Type    | IIN Ranges           | Length
    -------------|---------------------|--------
    Visa         | 4                   | 13, 16, 19
    Mastercard   | 51-55, 2221-2720    | 16
    Amex         | 34, 37              | 15
    Discover     | 6011, 644-649, 65   | 16-19
    """
    digits = card_number.replace(" ", "").replace("-", "")
    
    if not digits.isdigit():
        return CardType.UNKNOWN
    
    length = len(digits)
    
    # Visa: starts with 4
    if digits[0] == '4' and length in (13, 16, 19):
        return CardType.VISA
    
    # Mastercard: 51-55 or 2221-2720
    if length == 16:
        prefix2 = int(digits[:2])
        prefix4 = int(digits[:4])
        
        if 51 <= prefix2 <= 55:
            return CardType.MASTERCARD
        if 2221 <= prefix4 <= 2720:
            return CardType.MASTERCARD
    
    # Amex: 34 or 37
    if length == 15 and digits[:2] in ('34', '37'):
        return CardType.AMEX
    
    # Discover: 6011, 644-649, 65
    if 16 <= length <= 19:
        if digits[:4] == '6011':
            return CardType.DISCOVER
        if digits[:2] == '65':
            return CardType.DISCOVER
        prefix3 = int(digits[:3])
        if 644 <= prefix3 <= 649:
            return CardType.DISCOVER
    
    return CardType.UNKNOWN


def mask_card_number(card_number: str, visible_digits: int = 4) -> str:
    """
    Mask card number for display, showing only last N digits.
    
    Example: "4111111111111111" -> "**** **** **** 1111"
    """
    digits = card_number.replace(" ", "").replace("-", "")
    
    if len(digits) < visible_digits:
        return "*" * len(digits)
    
    masked = "*" * (len(digits) - visible_digits) + digits[-visible_digits:]
    
    # Format with spaces every 4 digits
    return " ".join(masked[i:i+4] for i in range(0, len(masked), 4))


def validate_expiry(month: int, year: int) -> Tuple[bool, str]:
    """
    Validate card expiration date.
    
    Returns (is_valid, error_message)
    """
    if not (1 <= month <= 12):
        return False, "Invalid month"
    
    current = datetime.now()
    current_year = current.year
    current_month = current.month
    
    # Handle 2-digit year
    if year < 100:
        year += 2000
    
    if year < current_year:
        return False, "Card has expired"
    
    if year == current_year and month < current_month:
        return False, "Card has expired"
    
    # Check if too far in future (typically max 20 years)
    if year > current_year + 20:
        return False, "Invalid expiration year"
    
    return True, ""


def validate_cvv(cvv: str, card_type: CardType) -> Tuple[bool, str]:
    """
    Validate CVV based on card type.
    
    Amex: 4 digits (front of card)
    Others: 3 digits (back of card)
    """
    if not cvv.isdigit():
        return False, "CVV must contain only digits"
    
    expected_length = 4 if card_type == CardType.AMEX else 3
    
    if len(cvv) != expected_length:
        return False, f"CVV must be {expected_length} digits for {card_type.value}"
    
    return True, ""


class CreditCardValidator:
    """
    Complete credit card validation service.
    """
    
    @staticmethod
    def validate(card: CreditCard) -> Tuple[bool, list]:
        """
        Validate all aspects of a credit card.
        
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate card number format
        digits = card.number.replace(" ", "").replace("-", "")
        if not digits.isdigit():
            errors.append("Card number must contain only digits")
        elif len(digits) < 13 or len(digits) > 19:
            errors.append("Card number must be 13-19 digits")
        elif not luhn_checksum(card.number):
            errors.append("Invalid card number (checksum failed)")
        
        # Identify card type
        card_type = identify_card_type(card.number)
        if card_type == CardType.UNKNOWN:
            errors.append("Unrecognized card type")
        
        # Validate expiry
        expiry_valid, expiry_error = validate_expiry(
            card.expiry_month, card.expiry_year
        )
        if not expiry_valid:
            errors.append(expiry_error)
        
        # Validate CVV
        cvv_valid, cvv_error = validate_cvv(card.cvv, card_type)
        if not cvv_valid:
            errors.append(cvv_error)
        
        # Validate cardholder name
        if not card.cardholder_name or len(card.cardholder_name.strip()) < 2:
            errors.append("Invalid cardholder name")
        
        return len(errors) == 0, errors


# Bonus: Generate valid test card numbers
def generate_test_card(card_type: CardType) -> str:
    """
    Generate a valid test card number for the given type.
    Uses well-known test card numbers.
    """
    test_cards = {
        CardType.VISA: "4111111111111111",
        CardType.MASTERCARD: "5500000000000004",
        CardType.AMEX: "340000000000009",
        CardType.DISCOVER: "6011000000000004",
    }
    return test_cards.get(card_type, "")


# Test cases
def test_credit_card_validation():
    print("Testing Luhn Algorithm...")
    
    # Valid test card numbers
    assert luhn_checksum("4111111111111111"), "Visa test card should be valid"
    assert luhn_checksum("5500000000000004"), "Mastercard test card should be valid"
    assert luhn_checksum("340000000000009"), "Amex test card should be valid"
    assert luhn_checksum("6011000000000004"), "Discover test card should be valid"
    
    # Invalid numbers
    assert not luhn_checksum("4111111111111112"), "Should fail checksum"
    assert not luhn_checksum("1234567890123456"), "Random number should fail"
    
    print("Luhn Algorithm tests passed!")
    
    print("\nTesting Card Type Identification...")
    
    assert identify_card_type("4111111111111111") == CardType.VISA
    assert identify_card_type("5500000000000004") == CardType.MASTERCARD
    assert identify_card_type("340000000000009") == CardType.AMEX
    assert identify_card_type("6011000000000004") == CardType.DISCOVER
    assert identify_card_type("1234567890123456") == CardType.UNKNOWN
    
    print("Card Type Identification tests passed!")
    
    print("\nTesting Card Masking...")
    
    assert mask_card_number("4111111111111111") == "**** **** **** 1111"
    assert mask_card_number("340000000000009") == "**** **** ***0 009"
    
    print("Card Masking tests passed!")
    
    print("\nTesting Full Validation...")
    
    valid_card = CreditCard(
        number="4111111111111111",
        expiry_month=12,
        expiry_year=2027,
        cvv="123",
        cardholder_name="John Doe"
    )
    
    is_valid, errors = CreditCardValidator.validate(valid_card)
    assert is_valid, f"Valid card should pass: {errors}"
    
    expired_card = CreditCard(
        number="4111111111111111",
        expiry_month=1,
        expiry_year=2020,
        cvv="123",
        cardholder_name="John Doe"
    )
    
    is_valid, errors = CreditCardValidator.validate(expired_card)
    assert not is_valid, "Expired card should fail"
    assert any("expired" in e.lower() for e in errors)
    
    print("Full Validation tests passed!")
    
    print("\nAll credit card validation tests passed!")


if __name__ == "__main__":
    test_credit_card_validation()
