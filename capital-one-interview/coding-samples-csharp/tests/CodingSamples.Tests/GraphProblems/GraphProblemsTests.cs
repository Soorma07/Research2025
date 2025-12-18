using CodingSamples.Core.GraphProblems;

namespace CodingSamples.Tests.GraphProblems;

public class GraphTests
{
    [Fact]
    public void Bfs_SimpleGraph_ReturnsCorrectOrder()
    {
        var graph = new Graph<string>(directed: true);
        graph.AddEdge("A", "B", 1);
        graph.AddEdge("A", "C", 4);
        graph.AddEdge("B", "C", 2);
        graph.AddEdge("B", "D", 5);
        graph.AddEdge("C", "D", 1);

        var result = graph.Bfs("A");

        Assert.Equal("A", result[0]);
        Assert.Contains("B", result);
        Assert.Contains("C", result);
        Assert.Contains("D", result);
    }

    [Fact]
    public void Dfs_SimpleGraph_ReturnsCorrectOrder()
    {
        var graph = new Graph<string>(directed: true);
        graph.AddEdge("A", "B", 1);
        graph.AddEdge("A", "C", 4);
        graph.AddEdge("B", "C", 2);
        graph.AddEdge("B", "D", 5);
        graph.AddEdge("C", "D", 1);

        var result = graph.Dfs("A");

        Assert.Equal("A", result[0]);
        Assert.Contains("B", result);
        Assert.Contains("C", result);
        Assert.Contains("D", result);
    }

    [Fact]
    public void ShortestPathDijkstra_SimpleGraph_ReturnsCorrectPath()
    {
        var graph = new Graph<string>(directed: true);
        graph.AddEdge("A", "B", 1);
        graph.AddEdge("A", "C", 4);
        graph.AddEdge("B", "C", 2);
        graph.AddEdge("B", "D", 5);
        graph.AddEdge("C", "D", 1);

        var (distance, path) = graph.ShortestPathDijkstra("A", "D");

        Assert.Equal(4, distance);
        Assert.Equal("A", path[0]);
        Assert.Equal("D", path[^1]);
    }

    [Fact]
    public void HasCycle_CyclicGraph_ReturnsTrue()
    {
        var graph = new Graph<string>(directed: true);
        graph.AddEdge("A", "B");
        graph.AddEdge("B", "C");
        graph.AddEdge("C", "A");

        Assert.True(graph.HasCycle());
    }

    [Fact]
    public void HasCycle_AcyclicGraph_ReturnsFalse()
    {
        var graph = new Graph<string>(directed: true);
        graph.AddEdge("A", "B");
        graph.AddEdge("B", "C");
        graph.AddEdge("A", "C");

        Assert.False(graph.HasCycle());
    }

    [Fact]
    public void TopologicalSort_Dag_ReturnsValidOrder()
    {
        var graph = new Graph<string>(directed: true);
        graph.AddEdge("A", "B");
        graph.AddEdge("A", "C");
        graph.AddEdge("B", "D");
        graph.AddEdge("C", "D");

        var topo = graph.TopologicalSort();

        Assert.True(topo.IndexOf("A") < topo.IndexOf("B"));
        Assert.True(topo.IndexOf("A") < topo.IndexOf("C"));
        Assert.True(topo.IndexOf("B") < topo.IndexOf("D"));
    }

    [Fact]
    public void TopologicalSort_CyclicGraph_ReturnsEmptyList()
    {
        var graph = new Graph<string>(directed: true);
        graph.AddEdge("A", "B");
        graph.AddEdge("B", "C");
        graph.AddEdge("C", "A");

        var topo = graph.TopologicalSort();

        Assert.Empty(topo);
    }
}

public class FraudRingDetectorTests
{
    private readonly IFraudRingDetector _detector = new FraudRingDetector();

    [Fact]
    public void FindFraudRings_WithCycles_DetectsRings()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("Alice", "Bob", 100m),
            ("Bob", "Charlie", 95m),
            ("Charlie", "Alice", 90m),
            ("Dave", "Eve", 50m),
            ("Eve", "Dave", 45m),
            ("Frank", "George", 200m)
        };

        var rings = _detector.FindFraudRings(transactions);

        Assert.Equal(2, rings.Count);
    }

    [Fact]
    public void FindFraudRings_NoCycles_ReturnsEmpty()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("Alice", "Bob", 100m),
            ("Bob", "Charlie", 95m),
            ("Charlie", "Dave", 90m)
        };

        var rings = _detector.FindFraudRings(transactions);

        Assert.Empty(rings);
    }

    [Fact]
    public void FindFraudRings_SingleCycle_DetectsOne()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("A", "B", 100m),
            ("B", "C", 100m),
            ("C", "A", 100m)
        };

        var rings = _detector.FindFraudRings(transactions);

        Assert.Single(rings);
        Assert.Contains("A", rings[0]);
        Assert.Contains("B", rings[0]);
        Assert.Contains("C", rings[0]);
    }
}

public class TransactionPathFinderTests
{
    private readonly ITransactionPathFinder _pathFinder = new TransactionPathFinder();

    [Fact]
    public void FindShortestPath_DirectPath_ReturnsCorrectHops()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("A", "B", 100m),
            ("B", "C", 100m),
            ("C", "D", 100m)
        };

        var (hops, path) = _pathFinder.FindShortestPath(transactions, "A", "D");

        Assert.Equal(3, hops);
        Assert.Equal(new List<string> { "A", "B", "C", "D" }, path);
    }

    [Fact]
    public void FindShortestPath_NoPath_ReturnsNegativeOne()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("A", "B", 100m),
            ("C", "D", 100m)
        };

        var (hops, path) = _pathFinder.FindShortestPath(transactions, "A", "D");

        Assert.Equal(-1, hops);
        Assert.Empty(path);
    }

    [Fact]
    public void FindShortestPath_MultipleRoutes_ReturnsShortestPath()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("A", "B", 100m),
            ("A", "C", 100m),
            ("B", "D", 100m),
            ("C", "D", 100m)
        };

        var (hops, path) = _pathFinder.FindShortestPath(transactions, "A", "D");

        Assert.Equal(2, hops);
        Assert.Equal("A", path[0]);
        Assert.Equal("D", path[^1]);
    }
}

public class PageRankCalculatorTests
{
    private readonly IPageRankCalculator _calculator = new PageRankCalculator();

    [Fact]
    public void Calculate_SimpleGraph_ReturnsRankings()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("A", "B", 100m),
            ("B", "C", 100m),
            ("C", "A", 100m)
        };

        var ranks = _calculator.Calculate(transactions, damping: 0.85, iterations: 100);

        Assert.Equal(3, ranks.Count);
        Assert.True(ranks.Values.All(r => r > 0));
    }

    [Fact]
    public void Calculate_StarTopology_CenterHasHigherRank()
    {
        var transactions = new List<(string, string, decimal)>
        {
            ("A", "Center", 100m),
            ("B", "Center", 100m),
            ("C", "Center", 100m),
            ("D", "Center", 100m)
        };

        var ranks = _calculator.Calculate(transactions, damping: 0.85, iterations: 100);

        Assert.True(ranks["Center"] > ranks["A"]);
        Assert.True(ranks["Center"] > ranks["B"]);
        Assert.True(ranks["Center"] > ranks["C"]);
        Assert.True(ranks["Center"] > ranks["D"]);
    }

    [Fact]
    public void Calculate_EmptyTransactions_ReturnsEmpty()
    {
        var transactions = new List<(string, string, decimal)>();

        var ranks = _calculator.Calculate(transactions);

        Assert.Empty(ranks);
    }
}
