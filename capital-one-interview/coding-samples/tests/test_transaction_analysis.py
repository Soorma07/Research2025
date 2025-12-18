"""
Unit tests for transaction analysis module.
Run with: pytest tests/test_transaction_analysis.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from importlib.machinery import SourceFileLoader

# Load the module with numeric prefix
transaction_analysis = SourceFileLoader(
    "transaction_analysis",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01_transaction_analysis.py")
).load_module()

Transaction = transaction_analysis.Transaction
find_suspicious_accounts = transaction_analysis.find_suspicious_accounts
find_suspicious_accounts_optimized = transaction_analysis.find_suspicious_accounts_optimized


class TestTransactionAnalysis:
    """Test cases for transaction analysis functions."""
    
    @pytest.fixture
    def sample_transactions(self):
        """Sample transactions for testing."""
        return [
            Transaction("t1", "acc1", 5000, 1000, "NYC"),
            Transaction("t2", "acc1", 3000, 1010, "NYC"),
            Transaction("t3", "acc1", 4000, 1020, "NYC"),  # Total > 10000 in 60s
            
            Transaction("t4", "acc2", 100, 2000, "LA"),
            Transaction("t5", "acc2", 100, 2010, "SF"),
            Transaction("t6", "acc2", 100, 2020, "NYC"),
            Transaction("t7", "acc2", 100, 2030, "Chicago"),  # 4 cities in 10 min
            
            Transaction("t8", "acc3", 100, 3000, "Boston"),
            Transaction("t9", "acc3", 100, 3001, "Boston"),
            Transaction("t10", "acc3", 100, 3002, "Boston"),
            Transaction("t11", "acc3", 100, 3003, "Boston"),
            Transaction("t12", "acc3", 100, 3004, "Boston"),  # 5 txns in 60s
            
            Transaction("t13", "acc4", 500, 4000, "Miami"),
            Transaction("t14", "acc4", 500, 4100, "Miami"),  # Normal account
        ]
    
    def test_high_amount_suspicious(self, sample_transactions):
        """Test that accounts with total > $10,000 in 60s are flagged."""
        result = find_suspicious_accounts(sample_transactions)
        assert "acc1" in result, "acc1 should be suspicious (amount > 10000 in 60s)"
    
    def test_multiple_cities_suspicious(self, sample_transactions):
        """Test that accounts with > 2 cities in 10 min are flagged."""
        result = find_suspicious_accounts(sample_transactions)
        assert "acc2" in result, "acc2 should be suspicious (4 cities in 10 min)"
    
    def test_high_velocity_suspicious(self, sample_transactions):
        """Test that accounts with > 3 transactions in 60s are flagged."""
        result = find_suspicious_accounts(sample_transactions)
        assert "acc3" in result, "acc3 should be suspicious (5 transactions in 60s)"
    
    def test_normal_account_not_flagged(self, sample_transactions):
        """Test that normal accounts are not flagged."""
        result = find_suspicious_accounts(sample_transactions)
        assert "acc4" not in result, "acc4 should not be suspicious"
    
    def test_optimized_matches_basic(self, sample_transactions):
        """Test that optimized version returns same results as basic."""
        basic_result = find_suspicious_accounts(sample_transactions)
        optimized_result = find_suspicious_accounts_optimized(sample_transactions)
        assert basic_result == optimized_result, "Both implementations should return same result"
    
    def test_empty_transactions(self):
        """Test with empty transaction list."""
        result = find_suspicious_accounts([])
        assert result == set(), "Empty transactions should return empty set"
    
    def test_single_transaction(self):
        """Test with single transaction."""
        transactions = [Transaction("t1", "acc1", 100, 1000, "NYC")]
        result = find_suspicious_accounts(transactions)
        assert "acc1" not in result, "Single transaction should not be suspicious"
    
    def test_exactly_three_transactions_not_suspicious(self):
        """Test that exactly 3 transactions in 60s is not suspicious."""
        transactions = [
            Transaction("t1", "acc1", 100, 1000, "NYC"),
            Transaction("t2", "acc1", 100, 1020, "NYC"),
            Transaction("t3", "acc1", 100, 1040, "NYC"),
        ]
        result = find_suspicious_accounts(transactions)
        assert "acc1" not in result, "Exactly 3 transactions should not be suspicious"
    
    def test_exactly_10000_not_suspicious(self):
        """Test that exactly $10,000 in 60s is not suspicious."""
        transactions = [
            Transaction("t1", "acc1", 5000, 1000, "NYC"),
            Transaction("t2", "acc1", 5000, 1020, "NYC"),
        ]
        result = find_suspicious_accounts(transactions)
        assert "acc1" not in result, "Exactly $10,000 should not be suspicious"
    
    def test_exactly_two_cities_not_suspicious(self):
        """Test that exactly 2 cities in 10 min is not suspicious."""
        transactions = [
            Transaction("t1", "acc1", 100, 1000, "NYC"),
            Transaction("t2", "acc1", 100, 1100, "LA"),
        ]
        result = find_suspicious_accounts(transactions)
        assert "acc1" not in result, "Exactly 2 cities should not be suspicious"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
