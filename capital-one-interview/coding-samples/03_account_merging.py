"""
Capital One Coding Sample: Account Merging (Union-Find)

This is a classic problem that appears in financial services interviews.
Given a list of accounts where each account has a name and list of emails,
merge accounts that belong to the same person (share at least one email).

This tests:
- Union-Find (Disjoint Set Union) data structure
- Graph traversal (alternative approach)
- Handling complex data relationships

LeetCode 721: Accounts Merge
"""

from collections import defaultdict
from typing import List, Dict, Set


class UnionFind:
    """
    Union-Find data structure with path compression and union by rank.
    
    Time Complexity:
        - find: O(α(n)) ≈ O(1) amortized (inverse Ackermann)
        - union: O(α(n)) ≈ O(1) amortized
    Space Complexity: O(n)
    """
    
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}
    
    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        
        return self.parent[x]
    
    def union(self, x: str, y: str) -> None:
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1


def merge_accounts(accounts: List[List[str]]) -> List[List[str]]:
    """
    Merge accounts that share at least one email.
    
    Args:
        accounts: List of [name, email1, email2, ...] lists
        
    Returns:
        Merged accounts with sorted emails
        
    Time Complexity: O(n * k * α(n * k)) where n = accounts, k = avg emails
    Space Complexity: O(n * k)
    """
    uf = UnionFind()
    email_to_name: Dict[str, str] = {}
    email_to_id: Dict[str, int] = {}
    
    # Build union-find structure
    for i, account in enumerate(accounts):
        name = account[0]
        emails = account[1:]
        
        for email in emails:
            email_to_name[email] = name
            
            if email not in email_to_id:
                email_to_id[email] = i
            
            # Union all emails in same account
            uf.union(emails[0], email)
    
    # Group emails by their root
    root_to_emails: Dict[str, Set[str]] = defaultdict(set)
    for email in email_to_name:
        root = uf.find(email)
        root_to_emails[root].add(email)
    
    # Build result
    result = []
    for root, emails in root_to_emails.items():
        name = email_to_name[root]
        result.append([name] + sorted(emails))
    
    return result


def merge_accounts_dfs(accounts: List[List[str]]) -> List[List[str]]:
    """
    Alternative approach using DFS on email graph.
    
    Build a graph where emails are nodes and edges connect emails
    in the same account. Then find connected components.
    """
    # Build adjacency list
    graph: Dict[str, Set[str]] = defaultdict(set)
    email_to_name: Dict[str, str] = {}
    
    for account in accounts:
        name = account[0]
        emails = account[1:]
        
        for email in emails:
            email_to_name[email] = name
        
        # Connect all emails in same account
        for i in range(len(emails)):
            for j in range(i + 1, len(emails)):
                graph[emails[i]].add(emails[j])
                graph[emails[j]].add(emails[i])
    
    # DFS to find connected components
    visited: Set[str] = set()
    result = []
    
    def dfs(email: str, component: List[str]) -> None:
        visited.add(email)
        component.append(email)
        
        for neighbor in graph[email]:
            if neighbor not in visited:
                dfs(neighbor, component)
    
    for email in email_to_name:
        if email not in visited:
            component: List[str] = []
            dfs(email, component)
            name = email_to_name[email]
            result.append([name] + sorted(component))
    
    return result


# Related problem: Find duplicate transactions
def find_duplicate_transactions(
    transactions: List[Dict]
) -> List[List[Dict]]:
    """
    Find groups of duplicate transactions.
    
    A transaction is a duplicate if it has the same:
    - source account
    - target account  
    - amount
    - category
    And occurs within 60 seconds of another matching transaction.
    
    This is a common Capital One interview variation.
    """
    from itertools import groupby
    
    # Group by (source, target, amount, category)
    def get_key(txn):
        return (txn['source'], txn['target'], txn['amount'], txn['category'])
    
    # Sort by key then by time
    sorted_txns = sorted(transactions, key=lambda t: (get_key(t), t['time']))
    
    duplicates = []
    
    for key, group in groupby(sorted_txns, key=get_key):
        group_list = list(group)
        
        if len(group_list) < 2:
            continue
        
        # Find clusters within 60 seconds
        i = 0
        while i < len(group_list):
            cluster = [group_list[i]]
            j = i + 1
            
            while j < len(group_list):
                # Check if within 60 seconds of any in cluster
                if any(abs(group_list[j]['time'] - t['time']) <= 60 
                       for t in cluster):
                    cluster.append(group_list[j])
                    j += 1
                else:
                    break
            
            if len(cluster) > 1:
                duplicates.append(cluster)
            
            i = j
    
    return duplicates


# Test cases
def test_account_merging():
    accounts = [
        ["John", "john@mail.com", "john_work@mail.com"],
        ["John", "john@mail.com", "john_home@mail.com"],
        ["Mary", "mary@mail.com"],
        ["John", "johnny@mail.com"]
    ]
    
    result = merge_accounts(accounts)
    print("Union-Find result:")
    for account in result:
        print(f"  {account}")
    
    # Verify John's accounts are merged
    john_accounts = [a for a in result if a[0] == "John"]
    assert len(john_accounts) == 2, "Should have 2 John accounts (one merged, one separate)"
    
    # Find the merged account
    merged = max(john_accounts, key=len)
    assert "john@mail.com" in merged
    assert "john_work@mail.com" in merged
    assert "john_home@mail.com" in merged
    
    # Test DFS approach
    result_dfs = merge_accounts_dfs(accounts)
    print("\nDFS result:")
    for account in result_dfs:
        print(f"  {account}")
    
    print("\nAll account merging tests passed!")


def test_duplicate_transactions():
    transactions = [
        {'id': 1, 'source': 'A', 'target': 'B', 'amount': 100, 
         'category': 'food', 'time': 1000},
        {'id': 2, 'source': 'A', 'target': 'B', 'amount': 100, 
         'category': 'food', 'time': 1030},  # Duplicate of 1
        {'id': 3, 'source': 'A', 'target': 'B', 'amount': 100, 
         'category': 'food', 'time': 1045},  # Duplicate of 1 and 2
        {'id': 4, 'source': 'A', 'target': 'B', 'amount': 100, 
         'category': 'food', 'time': 2000},  # Not duplicate (too far)
        {'id': 5, 'source': 'C', 'target': 'D', 'amount': 200, 
         'category': 'gas', 'time': 3000},   # Different transaction
    ]
    
    duplicates = find_duplicate_transactions(transactions)
    print("\nDuplicate transaction groups:")
    for group in duplicates:
        print(f"  IDs: {[t['id'] for t in group]}")
    
    assert len(duplicates) == 1, "Should find 1 duplicate group"
    assert len(duplicates[0]) == 3, "Group should have 3 transactions"
    
    print("Duplicate transaction tests passed!")


if __name__ == "__main__":
    test_account_merging()
    test_duplicate_transactions()
