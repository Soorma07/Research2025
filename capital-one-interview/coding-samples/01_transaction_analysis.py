"""
Capital One Coding Sample: Transaction Analysis

This is a common type of problem at Capital One - analyzing financial transactions.
The problem tests your ability to work with data structures, handle edge cases,
and write clean, efficient code.

Problem: Given a list of transactions, find all accounts that have suspicious activity.
An account is suspicious if:
1. It has more than 3 transactions within any 60-second window
2. The total amount in any 60-second window exceeds $10,000
3. There are transactions from more than 2 different cities within 10 minutes

Time Complexity Target: O(n log n) where n is number of transactions
Space Complexity Target: O(n)
"""

from collections import defaultdict
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    transaction_id: str
    account_id: str
    amount: float
    timestamp: int  # Unix timestamp in seconds
    city: str


def find_suspicious_accounts(transactions: List[Transaction]) -> Set[str]:
    """
    Find all accounts with suspicious activity.
    
    Args:
        transactions: List of Transaction objects
        
    Returns:
        Set of account IDs that have suspicious activity
    """
    suspicious = set()
    
    # Group transactions by account
    account_transactions: Dict[str, List[Transaction]] = defaultdict(list)
    for txn in transactions:
        account_transactions[txn.account_id].append(txn)
    
    for account_id, txns in account_transactions.items():
        # Sort by timestamp
        txns.sort(key=lambda x: x.timestamp)
        
        if is_suspicious(txns):
            suspicious.add(account_id)
    
    return suspicious


def is_suspicious(txns: List[Transaction]) -> bool:
    """Check if a list of transactions (for one account) is suspicious."""
    n = len(txns)
    
    # Sliding window approach for 60-second checks
    for i in range(n):
        window_count = 0
        window_amount = 0.0
        
        for j in range(i, n):
            if txns[j].timestamp - txns[i].timestamp <= 60:
                window_count += 1
                window_amount += txns[j].amount
            else:
                break
        
        # Check condition 1: More than 3 transactions in 60 seconds
        if window_count > 3:
            return True
        
        # Check condition 2: Total amount exceeds $10,000 in 60 seconds
        if window_amount > 10000:
            return True
    
    # Check condition 3: More than 2 cities within 10 minutes (600 seconds)
    for i in range(n):
        cities_in_window = set()
        
        for j in range(i, n):
            if txns[j].timestamp - txns[i].timestamp <= 600:
                cities_in_window.add(txns[j].city)
            else:
                break
        
        if len(cities_in_window) > 2:
            return True
    
    return False


# Optimized version using two-pointer technique
def find_suspicious_accounts_optimized(transactions: List[Transaction]) -> Set[str]:
    """
    Optimized version using sliding window with two pointers.
    This reduces the time complexity for the window checks.
    """
    suspicious = set()
    account_transactions: Dict[str, List[Transaction]] = defaultdict(list)
    
    for txn in transactions:
        account_transactions[txn.account_id].append(txn)
    
    for account_id, txns in account_transactions.items():
        txns.sort(key=lambda x: x.timestamp)
        
        # Two-pointer for 60-second window
        left = 0
        window_amount = 0.0
        
        for right in range(len(txns)):
            window_amount += txns[right].amount
            
            # Shrink window if outside 60 seconds
            while txns[right].timestamp - txns[left].timestamp > 60:
                window_amount -= txns[left].amount
                left += 1
            
            window_size = right - left + 1
            
            if window_size > 3 or window_amount > 10000:
                suspicious.add(account_id)
                break
        
        if account_id in suspicious:
            continue
        
        # Two-pointer for 10-minute city check
        left = 0
        cities: Dict[str, int] = defaultdict(int)
        
        for right in range(len(txns)):
            cities[txns[right].city] += 1
            
            while txns[right].timestamp - txns[left].timestamp > 600:
                cities[txns[left].city] -= 1
                if cities[txns[left].city] == 0:
                    del cities[txns[left].city]
                left += 1
            
            if len(cities) > 2:
                suspicious.add(account_id)
                break
    
    return suspicious


# Test cases
def test_suspicious_accounts():
    transactions = [
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
    
    result = find_suspicious_accounts(transactions)
    print(f"Suspicious accounts: {result}")
    assert "acc1" in result, "acc1 should be suspicious (amount > 10000)"
    assert "acc2" in result, "acc2 should be suspicious (4 cities)"
    assert "acc3" in result, "acc3 should be suspicious (5 transactions)"
    assert "acc4" not in result, "acc4 should not be suspicious"
    
    # Test optimized version
    result_opt = find_suspicious_accounts_optimized(transactions)
    assert result == result_opt, "Both implementations should return same result"
    
    print("All tests passed!")


if __name__ == "__main__":
    test_suspicious_accounts()
