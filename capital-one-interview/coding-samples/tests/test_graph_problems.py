"""
Unit tests for graph problems module.
Run with: pytest tests/test_graph_problems.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from importlib.machinery import SourceFileLoader

# Load the module with numeric prefix
graph_problems = SourceFileLoader(
    "graph_problems",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "06_graph_problems.py")
).load_module()

Graph = graph_problems.Graph
find_fraud_ring = graph_problems.find_fraud_ring
find_shortest_transaction_path = graph_problems.find_shortest_transaction_path
calculate_pagerank = graph_problems.calculate_pagerank


class TestGraph:
    """Test cases for Graph class."""
    
    @pytest.fixture
    def sample_graph(self):
        """Create a sample directed graph."""
        g = Graph(directed=True)
        g.add_edge("A", "B", 1)
        g.add_edge("A", "C", 4)
        g.add_edge("B", "C", 2)
        g.add_edge("B", "D", 5)
        g.add_edge("C", "D", 1)
        return g
    
    def test_bfs_traversal(self, sample_graph):
        """Test BFS traversal."""
        result = sample_graph.bfs("A")
        assert result[0] == "A", "BFS should start with source node"
        assert set(result) == {"A", "B", "C", "D"}, "BFS should visit all nodes"
    
    def test_dfs_traversal(self, sample_graph):
        """Test DFS traversal."""
        result = sample_graph.dfs("A")
        assert result[0] == "A", "DFS should start with source node"
        assert set(result) == {"A", "B", "C", "D"}, "DFS should visit all nodes"
    
    def test_shortest_path_dijkstra(self, sample_graph):
        """Test Dijkstra's shortest path algorithm."""
        dist, path = sample_graph.shortest_path_dijkstra("A", "D")
        assert dist == 4, "Shortest distance A->D should be 4 (A->B->C->D)"
        assert path[0] == "A", "Path should start with A"
        assert path[-1] == "D", "Path should end with D"
    
    def test_shortest_path_direct(self):
        """Test shortest path with direct edge."""
        g = Graph(directed=True)
        g.add_edge("A", "B", 5)
        dist, path = g.shortest_path_dijkstra("A", "B")
        assert dist == 5
        assert path == ["A", "B"]
    
    def test_no_path(self):
        """Test when no path exists."""
        g = Graph(directed=True)
        g.add_edge("A", "B", 1)
        g.add_edge("C", "D", 1)
        dist, path = g.shortest_path_dijkstra("A", "D")
        assert dist == float('inf'), "Distance should be infinity when no path"


class TestCycleDetection:
    """Test cases for cycle detection."""
    
    def test_has_cycle(self):
        """Test graph with cycle."""
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")  # Creates cycle
        assert g.has_cycle(), "Should detect cycle"
    
    def test_no_cycle(self):
        """Test graph without cycle."""
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        assert not g.has_cycle(), "Should not detect cycle in DAG"
    
    def test_self_loop(self):
        """Test self-loop detection."""
        g = Graph(directed=True)
        g.add_edge("A", "A")  # Self loop
        assert g.has_cycle(), "Should detect self-loop as cycle"
    
    def test_empty_graph(self):
        """Test empty graph has no cycle."""
        g = Graph(directed=True)
        assert not g.has_cycle(), "Empty graph should have no cycle"


class TestTopologicalSort:
    """Test cases for topological sort."""
    
    def test_basic_topological_sort(self):
        """Test basic topological sort."""
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        
        result = g.topological_sort()
        
        # Verify ordering constraints
        assert result.index("A") < result.index("B"), "A should come before B"
        assert result.index("A") < result.index("C"), "A should come before C"
        assert result.index("B") < result.index("D"), "B should come before D"
        assert result.index("C") < result.index("D"), "C should come before D"
    
    def test_topological_sort_with_cycle(self):
        """Test topological sort returns empty for cyclic graph."""
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")  # Creates cycle
        
        result = g.topological_sort()
        assert result == [], "Cyclic graph should return empty list"
    
    def test_single_node(self):
        """Test topological sort with single node."""
        g = Graph(directed=True)
        g.add_edge("A", "A")  # Just to add the node
        g.adj["A"] = []  # Remove self-loop
        g.nodes = {"A"}
        
        result = g.topological_sort()
        assert result == ["A"], "Single node should return itself"


class TestFraudRingDetection:
    """Test cases for fraud ring detection."""
    
    def test_simple_fraud_ring(self):
        """Test detection of simple fraud ring."""
        transactions = [
            ("Alice", "Bob", 100),
            ("Bob", "Charlie", 95),
            ("Charlie", "Alice", 90),  # Completes a ring
        ]
        rings = find_fraud_ring(transactions)
        assert len(rings) == 1, "Should detect 1 fraud ring"
        assert {"Alice", "Bob", "Charlie"} in rings
    
    def test_multiple_fraud_rings(self):
        """Test detection of multiple fraud rings."""
        transactions = [
            ("Alice", "Bob", 100),
            ("Bob", "Charlie", 95),
            ("Charlie", "Alice", 90),  # Ring 1
            ("Dave", "Eve", 50),
            ("Eve", "Dave", 45),  # Ring 2
        ]
        rings = find_fraud_ring(transactions)
        assert len(rings) == 2, "Should detect 2 fraud rings"
    
    def test_no_fraud_ring(self):
        """Test when no fraud ring exists."""
        transactions = [
            ("Alice", "Bob", 100),
            ("Bob", "Charlie", 95),
            ("Charlie", "Dave", 90),  # No cycle
        ]
        rings = find_fraud_ring(transactions)
        assert len(rings) == 0, "Should detect no fraud rings"
    
    def test_empty_transactions(self):
        """Test with empty transaction list."""
        rings = find_fraud_ring([])
        assert rings == [], "Empty transactions should return empty list"


class TestShortestTransactionPath:
    """Test cases for shortest transaction path."""
    
    def test_direct_path(self):
        """Test direct path between accounts."""
        transactions = [
            ("A", "B", 100),
        ]
        hops, path = find_shortest_transaction_path(transactions, "A", "B")
        assert hops == 1, "Direct path should be 1 hop"
        assert path == ["A", "B"]
    
    def test_multi_hop_path(self):
        """Test multi-hop path."""
        transactions = [
            ("A", "B", 100),
            ("B", "C", 100),
            ("C", "D", 100),
        ]
        hops, path = find_shortest_transaction_path(transactions, "A", "D")
        assert hops == 3, "Should be 3 hops"
        assert path == ["A", "B", "C", "D"]
    
    def test_no_path(self):
        """Test when no path exists."""
        transactions = [
            ("A", "B", 100),
            ("C", "D", 100),
        ]
        hops, path = find_shortest_transaction_path(transactions, "A", "D")
        assert hops == -1, "Should return -1 when no path"
        assert path == []
    
    def test_shortest_among_multiple(self):
        """Test finding shortest among multiple paths."""
        transactions = [
            ("A", "B", 100),
            ("B", "D", 100),  # Short path: A->B->D
            ("A", "C", 100),
            ("C", "E", 100),
            ("E", "D", 100),  # Long path: A->C->E->D
        ]
        hops, path = find_shortest_transaction_path(transactions, "A", "D")
        assert hops == 2, "Should find shortest path (2 hops)"


class TestPageRank:
    """Test cases for PageRank calculation."""
    
    def test_basic_pagerank(self):
        """Test basic PageRank calculation."""
        transactions = [
            ("A", "B", 100),
            ("A", "C", 100),
            ("B", "C", 100),
        ]
        pr = calculate_pagerank(transactions)
        
        # C should have highest rank (receives from both A and B)
        assert pr["C"] > pr["A"], "C should rank higher than A"
        assert pr["C"] > pr["B"], "C should rank higher than B"
    
    def test_pagerank_sum_approximately_one(self):
        """Test that PageRank values sum to approximately 1."""
        transactions = [
            ("A", "B", 100),
            ("B", "C", 100),
            ("C", "A", 100),
        ]
        pr = calculate_pagerank(transactions)
        total = sum(pr.values())
        assert 0.99 < total < 1.01, f"PageRank should sum to ~1, got {total}"
    
    def test_empty_transactions(self):
        """Test PageRank with empty transactions."""
        pr = calculate_pagerank([])
        assert pr == {}, "Empty transactions should return empty dict"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
