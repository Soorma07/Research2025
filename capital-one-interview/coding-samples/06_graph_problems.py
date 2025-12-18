"""
Capital One Coding Sample: Graph Problems

Graph problems are common in backend interviews, especially for:
- Fraud detection networks
- Transaction flow analysis
- Dependency resolution
- Network topology

This file covers common graph patterns you should know.
"""

from collections import defaultdict, deque
from typing import List, Dict, Set, Optional, Tuple
import heapq


class Graph:
    """Basic graph implementation with common algorithms."""
    
    def __init__(self, directed: bool = True):
        self.directed = directed
        self.adj: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.nodes: Set[str] = set()
    
    def add_edge(self, u: str, v: str, weight: int = 1) -> None:
        self.adj[u].append((v, weight))
        self.nodes.add(u)
        self.nodes.add(v)
        
        if not self.directed:
            self.adj[v].append((u, weight))
    
    def bfs(self, start: str) -> List[str]:
        """Breadth-first search traversal."""
        visited = set()
        result = []
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            
            visited.add(node)
            result.append(node)
            
            for neighbor, _ in self.adj[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return result
    
    def dfs(self, start: str) -> List[str]:
        """Depth-first search traversal."""
        visited = set()
        result = []
        
        def dfs_helper(node: str) -> None:
            if node in visited:
                return
            
            visited.add(node)
            result.append(node)
            
            for neighbor, _ in self.adj[node]:
                dfs_helper(neighbor)
        
        dfs_helper(start)
        return result
    
    def shortest_path_dijkstra(
        self, start: str, end: str
    ) -> Tuple[int, List[str]]:
        """
        Find shortest path using Dijkstra's algorithm.
        
        Time Complexity: O((V + E) log V)
        Space Complexity: O(V)
        """
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous: Dict[str, Optional[str]] = {node: None for node in self.nodes}
        
        # Priority queue: (distance, node)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            dist, node = heapq.heappop(pq)
            
            if node in visited:
                continue
            visited.add(node)
            
            if node == end:
                break
            
            for neighbor, weight in self.adj[node]:
                if neighbor in visited:
                    continue
                
                new_dist = dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = node
                    heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return distances[end], path
    
    def has_cycle(self) -> bool:
        """
        Detect cycle in directed graph using DFS.
        
        Uses three states: WHITE (unvisited), GRAY (in progress), BLACK (done)
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in self.nodes}
        
        def dfs(node: str) -> bool:
            color[node] = GRAY
            
            for neighbor, _ in self.adj[node]:
                if color[neighbor] == GRAY:
                    return True  # Back edge found
                if color[neighbor] == WHITE and dfs(neighbor):
                    return True
            
            color[node] = BLACK
            return False
        
        for node in self.nodes:
            if color[node] == WHITE:
                if dfs(node):
                    return True
        
        return False
    
    def topological_sort(self) -> List[str]:
        """
        Topological sort using Kahn's algorithm (BFS).
        
        Returns empty list if cycle exists.
        """
        in_degree = defaultdict(int)
        for node in self.nodes:
            for neighbor, _ in self.adj[node]:
                in_degree[neighbor] += 1
        
        # Start with nodes having no incoming edges
        queue = deque([n for n in self.nodes if in_degree[n] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor, _ in self.adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If not all nodes processed, there's a cycle
        if len(result) != len(self.nodes):
            return []
        
        return result


def find_fraud_ring(
    transactions: List[Tuple[str, str, float]]
) -> List[Set[str]]:
    """
    Find potential fraud rings in transaction data.
    
    A fraud ring is a group of accounts that form a cycle of transactions,
    potentially indicating money laundering.
    
    Args:
        transactions: List of (sender, receiver, amount) tuples
        
    Returns:
        List of sets, each containing accounts in a potential fraud ring
    """
    # Build graph
    graph: Dict[str, Set[str]] = defaultdict(set)
    all_accounts: Set[str] = set()
    
    for sender, receiver, _ in transactions:
        graph[sender].add(receiver)
        all_accounts.add(sender)
        all_accounts.add(receiver)
    
    # Find strongly connected components (Tarjan's algorithm)
    index_counter = [0]
    stack: List[str] = []
    lowlinks: Dict[str, int] = {}
    index: Dict[str, int] = {}
    on_stack: Dict[str, bool] = {}
    sccs: List[Set[str]] = []
    
    def strongconnect(node: str) -> None:
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack[node] = True
        
        for neighbor in graph[node]:
            if neighbor not in index:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif on_stack.get(neighbor, False):
                lowlinks[node] = min(lowlinks[node], index[neighbor])
        
        # If node is root of SCC
        if lowlinks[node] == index[node]:
            scc: Set[str] = set()
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.add(w)
                if w == node:
                    break
            
            # Only include SCCs with more than 1 node (actual cycles)
            if len(scc) > 1:
                sccs.append(scc)
    
    for account in all_accounts:
        if account not in index:
            strongconnect(account)
    
    return sccs


def find_shortest_transaction_path(
    transactions: List[Tuple[str, str, float]],
    source: str,
    target: str
) -> Tuple[int, List[str]]:
    """
    Find the shortest path (by number of hops) between two accounts.
    
    Useful for tracing money flow or finding degrees of separation.
    """
    graph: Dict[str, List[str]] = defaultdict(list)
    
    for sender, receiver, _ in transactions:
        graph[sender].append(receiver)
    
    # BFS for shortest path
    queue = deque([(source, [source])])
    visited = {source}
    
    while queue:
        node, path = queue.popleft()
        
        if node == target:
            return len(path) - 1, path
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return -1, []  # No path found


def calculate_pagerank(
    transactions: List[Tuple[str, str, float]],
    damping: float = 0.85,
    iterations: int = 100
) -> Dict[str, float]:
    """
    Calculate PageRank-like importance score for accounts.
    
    Higher scores indicate accounts that receive transactions from
    many important accounts - could indicate central nodes in a network.
    """
    # Build graph and get all nodes
    graph: Dict[str, List[str]] = defaultdict(list)
    all_accounts: Set[str] = set()
    
    for sender, receiver, _ in transactions:
        graph[sender].append(receiver)
        all_accounts.add(sender)
        all_accounts.add(receiver)
    
    n = len(all_accounts)
    accounts = list(all_accounts)
    
    # Initialize PageRank
    pr = {acc: 1.0 / n for acc in accounts}
    
    # Iterative calculation
    for _ in range(iterations):
        new_pr = {}
        
        for acc in accounts:
            # Find all accounts that link to this one
            incoming_pr = 0.0
            for sender in accounts:
                if acc in graph[sender]:
                    out_degree = len(graph[sender])
                    if out_degree > 0:
                        incoming_pr += pr[sender] / out_degree
            
            new_pr[acc] = (1 - damping) / n + damping * incoming_pr
        
        pr = new_pr
    
    return pr


# Test cases
def test_graph_algorithms():
    print("Testing Graph Algorithms...")
    
    # Test basic graph operations
    g = Graph(directed=True)
    g.add_edge("A", "B", 1)
    g.add_edge("A", "C", 4)
    g.add_edge("B", "C", 2)
    g.add_edge("B", "D", 5)
    g.add_edge("C", "D", 1)
    
    print(f"BFS from A: {g.bfs('A')}")
    print(f"DFS from A: {g.dfs('A')}")
    
    dist, path = g.shortest_path_dijkstra("A", "D")
    print(f"Shortest path A->D: {path} (distance: {dist})")
    assert dist == 4, "Shortest distance should be 4 (A->B->C->D)"
    
    print("\nTesting Cycle Detection...")
    
    cyclic = Graph(directed=True)
    cyclic.add_edge("A", "B")
    cyclic.add_edge("B", "C")
    cyclic.add_edge("C", "A")  # Creates cycle
    
    assert cyclic.has_cycle(), "Should detect cycle"
    
    acyclic = Graph(directed=True)
    acyclic.add_edge("A", "B")
    acyclic.add_edge("B", "C")
    acyclic.add_edge("A", "C")
    
    assert not acyclic.has_cycle(), "Should not detect cycle"
    
    print("Cycle detection tests passed!")
    
    print("\nTesting Topological Sort...")
    
    dag = Graph(directed=True)
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("B", "D")
    dag.add_edge("C", "D")
    
    topo = dag.topological_sort()
    print(f"Topological order: {topo}")
    assert topo.index("A") < topo.index("B")
    assert topo.index("A") < topo.index("C")
    assert topo.index("B") < topo.index("D")
    
    print("Topological sort tests passed!")
    
    print("\nTesting Fraud Ring Detection...")
    
    transactions = [
        ("Alice", "Bob", 100),
        ("Bob", "Charlie", 95),
        ("Charlie", "Alice", 90),  # Completes a ring
        ("Dave", "Eve", 50),
        ("Eve", "Dave", 45),  # Another ring
        ("Frank", "George", 200),  # No ring
    ]
    
    rings = find_fraud_ring(transactions)
    print(f"Detected fraud rings: {rings}")
    assert len(rings) == 2, "Should detect 2 fraud rings"
    
    print("Fraud ring detection tests passed!")
    
    print("\nAll graph algorithm tests passed!")


if __name__ == "__main__":
    test_graph_algorithms()
