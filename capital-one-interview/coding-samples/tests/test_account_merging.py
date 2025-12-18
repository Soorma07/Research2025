"""
Unit tests for account merging module.
Run with: pytest tests/test_account_merging.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from importlib.machinery import SourceFileLoader

# Load the module with numeric prefix
account_merging = SourceFileLoader(
    "account_merging",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "03_account_merging.py")
).load_module()

UnionFind = account_merging.UnionFind
merge_accounts = account_merging.merge_accounts
merge_accounts_dfs = account_merging.merge_accounts_dfs
find_duplicate_transactions = account_merging.find_duplicate_transactions


class TestUnionFind:
    """Test cases for Union-Find data structure."""
    
    def test_find_creates_new_set(self):
        """Test that find creates a new set for unknown elements."""
        uf = UnionFind()
        root = uf.find("a")
        assert root == "a", "New element should be its own root"
    
    def test_union_connects_elements(self):
        """Test that union connects two elements."""
        uf = UnionFind()
        uf.union("a", "b")
        assert uf.find("a") == uf.find("b"), "United elements should have same root"
    
    def test_transitive_union(self):
        """Test that union is transitive."""
        uf = UnionFind()
        uf.union("a", "b")
        uf.union("b", "c")
        assert uf.find("a") == uf.find("c"), "Transitively united elements should have same root"
    
    def test_separate_sets(self):
        """Test that separate sets remain separate."""
        uf = UnionFind()
        uf.union("a", "b")
        uf.union("c", "d")
        assert uf.find("a") != uf.find("c"), "Separate sets should have different roots"


class TestMergeAccounts:
    """Test cases for account merging functions."""
    
    @pytest.fixture
    def sample_accounts(self):
        """Sample accounts for testing."""
        return [
            ["John", "john@mail.com", "john_work@mail.com"],
            ["John", "john@mail.com", "john_home@mail.com"],
            ["Mary", "mary@mail.com"],
            ["John", "johnny@mail.com"]
        ]
    
    def test_merge_accounts_basic(self, sample_accounts):
        """Test basic account merging."""
        result = merge_accounts(sample_accounts)
        
        # Find John's merged account
        john_accounts = [a for a in result if a[0] == "John"]
        assert len(john_accounts) == 2, "Should have 2 John accounts (one merged, one separate)"
        
        # Find the merged account (has more emails)
        merged = max(john_accounts, key=len)
        assert "john@mail.com" in merged
        assert "john_work@mail.com" in merged
        assert "john_home@mail.com" in merged
    
    def test_merge_accounts_dfs_basic(self, sample_accounts):
        """Test DFS-based account merging."""
        result = merge_accounts_dfs(sample_accounts)
        
        john_accounts = [a for a in result if a[0] == "John"]
        assert len(john_accounts) == 2
        
        merged = max(john_accounts, key=len)
        assert "john@mail.com" in merged
        assert "john_work@mail.com" in merged
        assert "john_home@mail.com" in merged
    
    def test_both_implementations_match(self, sample_accounts):
        """Test that both implementations produce equivalent results."""
        result1 = merge_accounts(sample_accounts)
        result2 = merge_accounts_dfs(sample_accounts)
        
        # Sort for comparison
        sorted1 = sorted([tuple(sorted(a[1:])) for a in result1])
        sorted2 = sorted([tuple(sorted(a[1:])) for a in result2])
        
        assert sorted1 == sorted2, "Both implementations should produce same email groups"
    
    def test_no_merge_needed(self):
        """Test when no accounts need merging."""
        accounts = [
            ["Alice", "alice@mail.com"],
            ["Bob", "bob@mail.com"],
        ]
        result = merge_accounts(accounts)
        assert len(result) == 2, "Should have 2 separate accounts"
    
    def test_all_merge_into_one(self):
        """Test when all accounts merge into one."""
        accounts = [
            ["User", "a@mail.com", "b@mail.com"],
            ["User", "b@mail.com", "c@mail.com"],
            ["User", "c@mail.com", "d@mail.com"],
        ]
        result = merge_accounts(accounts)
        assert len(result) == 1, "All accounts should merge into one"
        assert len(result[0]) == 5, "Should have name + 4 emails"
    
    def test_emails_sorted(self):
        """Test that emails in result are sorted."""
        accounts = [
            ["User", "z@mail.com", "a@mail.com"],
        ]
        result = merge_accounts(accounts)
        emails = result[0][1:]  # Skip name
        assert emails == sorted(emails), "Emails should be sorted"
    
    def test_empty_accounts(self):
        """Test with empty account list."""
        result = merge_accounts([])
        assert result == [], "Empty input should return empty result"


class TestFindDuplicateTransactions:
    """Test cases for duplicate transaction detection."""
    
    def test_finds_duplicates_within_window(self):
        """Test that duplicates within 60 seconds are found."""
        transactions = [
            {'id': 1, 'source': 'A', 'target': 'B', 'amount': 100, 
             'category': 'food', 'time': 1000},
            {'id': 2, 'source': 'A', 'target': 'B', 'amount': 100, 
             'category': 'food', 'time': 1030},
        ]
        duplicates = find_duplicate_transactions(transactions)
        assert len(duplicates) == 1, "Should find 1 duplicate group"
        assert len(duplicates[0]) == 2, "Group should have 2 transactions"
    
    def test_no_duplicates_outside_window(self):
        """Test that transactions outside 60 seconds are not duplicates."""
        transactions = [
            {'id': 1, 'source': 'A', 'target': 'B', 'amount': 100, 
             'category': 'food', 'time': 1000},
            {'id': 2, 'source': 'A', 'target': 'B', 'amount': 100, 
             'category': 'food', 'time': 2000},  # 1000 seconds later
        ]
        duplicates = find_duplicate_transactions(transactions)
        assert len(duplicates) == 0, "Should find no duplicates"
    
    def test_different_attributes_not_duplicates(self):
        """Test that transactions with different attributes are not duplicates."""
        transactions = [
            {'id': 1, 'source': 'A', 'target': 'B', 'amount': 100, 
             'category': 'food', 'time': 1000},
            {'id': 2, 'source': 'A', 'target': 'B', 'amount': 200,  # Different amount
             'category': 'food', 'time': 1030},
        ]
        duplicates = find_duplicate_transactions(transactions)
        assert len(duplicates) == 0, "Different amounts should not be duplicates"
    
    def test_multiple_duplicate_groups(self):
        """Test finding multiple duplicate groups."""
        transactions = [
            {'id': 1, 'source': 'A', 'target': 'B', 'amount': 100, 
             'category': 'food', 'time': 1000},
            {'id': 2, 'source': 'A', 'target': 'B', 'amount': 100, 
             'category': 'food', 'time': 1030},
            {'id': 3, 'source': 'C', 'target': 'D', 'amount': 200, 
             'category': 'gas', 'time': 2000},
            {'id': 4, 'source': 'C', 'target': 'D', 'amount': 200, 
             'category': 'gas', 'time': 2030},
        ]
        duplicates = find_duplicate_transactions(transactions)
        assert len(duplicates) == 2, "Should find 2 duplicate groups"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
