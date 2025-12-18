using CodingSamples.Core.AccountMerging;

namespace CodingSamples.Tests.AccountMerging;

public class AccountMergingTests
{
    private readonly IAccountMerger _unionFindMerger;
    private readonly IAccountMerger _dfsMerger;

    public AccountMergingTests()
    {
        _unionFindMerger = new UnionFindAccountMerger();
        _dfsMerger = new DfsAccountMerger();
    }

    private List<List<string>> GetSampleAccounts()
    {
        return new List<List<string>>
        {
            new() { "John", "john@mail.com", "john_work@mail.com" },
            new() { "John", "john@mail.com", "john_home@mail.com" },
            new() { "Mary", "mary@mail.com" },
            new() { "John", "johnny@mail.com" }
        };
    }

    [Fact]
    public void MergeAccounts_UnionFind_MergesSharedEmails()
    {
        var accounts = GetSampleAccounts();
        
        var result = _unionFindMerger.MergeAccounts(accounts);
        
        var johnAccounts = result.Where(a => a[0] == "John").ToList();
        Assert.Equal(2, johnAccounts.Count);
        
        var mergedAccount = johnAccounts.MaxBy(a => a.Count)!;
        Assert.Contains("john@mail.com", mergedAccount);
        Assert.Contains("john_work@mail.com", mergedAccount);
        Assert.Contains("john_home@mail.com", mergedAccount);
    }

    [Fact]
    public void MergeAccounts_Dfs_MergesSharedEmails()
    {
        var accounts = GetSampleAccounts();
        
        var result = _dfsMerger.MergeAccounts(accounts);
        
        var johnAccounts = result.Where(a => a[0] == "John").ToList();
        Assert.Equal(2, johnAccounts.Count);
        
        var mergedAccount = johnAccounts.MaxBy(a => a.Count)!;
        Assert.Contains("john@mail.com", mergedAccount);
        Assert.Contains("john_work@mail.com", mergedAccount);
        Assert.Contains("john_home@mail.com", mergedAccount);
    }

    [Fact]
    public void MergeAccounts_BothImplementations_ProduceSameResult()
    {
        var accounts = GetSampleAccounts();
        
        var unionFindResult = _unionFindMerger.MergeAccounts(accounts);
        var dfsResult = _dfsMerger.MergeAccounts(accounts);
        
        var normalizedUnionFind = unionFindResult
            .Select(a => string.Join(",", a.OrderBy(x => x)))
            .OrderBy(x => x)
            .ToList();
        
        var normalizedDfs = dfsResult
            .Select(a => string.Join(",", a.OrderBy(x => x)))
            .OrderBy(x => x)
            .ToList();
        
        Assert.Equal(normalizedUnionFind, normalizedDfs);
    }

    [Fact]
    public void MergeAccounts_NoSharedEmails_KeepsSeparate()
    {
        var accounts = new List<List<string>>
        {
            new() { "Alice", "alice@mail.com" },
            new() { "Bob", "bob@mail.com" }
        };
        
        var result = _unionFindMerger.MergeAccounts(accounts);
        
        Assert.Equal(2, result.Count);
    }

    [Fact]
    public void MergeAccounts_SingleAccount_ReturnsUnchanged()
    {
        var accounts = new List<List<string>>
        {
            new() { "Alice", "alice@mail.com", "alice_work@mail.com" }
        };
        
        var result = _unionFindMerger.MergeAccounts(accounts);
        
        Assert.Single(result);
        Assert.Equal("Alice", result[0][0]);
        Assert.Contains("alice@mail.com", result[0]);
        Assert.Contains("alice_work@mail.com", result[0]);
    }

    [Fact]
    public void MergeAccounts_EmailsSorted_InResult()
    {
        var accounts = new List<List<string>>
        {
            new() { "Alice", "z@mail.com", "a@mail.com", "m@mail.com" }
        };
        
        var result = _unionFindMerger.MergeAccounts(accounts);
        
        var emails = result[0].Skip(1).ToList();
        Assert.Equal(new List<string> { "a@mail.com", "m@mail.com", "z@mail.com" }, emails);
    }
}

public class UnionFindTests
{
    [Fact]
    public void Find_NewElement_ReturnsItself()
    {
        var uf = new UnionFind();
        
        Assert.Equal("a", uf.Find("a"));
    }

    [Fact]
    public void Union_TwoElements_ShareSameRoot()
    {
        var uf = new UnionFind();
        
        uf.Union("a", "b");
        
        Assert.Equal(uf.Find("a"), uf.Find("b"));
    }

    [Fact]
    public void Union_TransitiveRelation_AllShareSameRoot()
    {
        var uf = new UnionFind();
        
        uf.Union("a", "b");
        uf.Union("b", "c");
        
        Assert.Equal(uf.Find("a"), uf.Find("c"));
    }

    [Fact]
    public void Find_PathCompression_Works()
    {
        var uf = new UnionFind();
        
        uf.Union("a", "b");
        uf.Union("b", "c");
        uf.Union("c", "d");
        
        string root = uf.Find("d");
        Assert.Equal(root, uf.Find("a"));
        Assert.Equal(root, uf.Find("b"));
        Assert.Equal(root, uf.Find("c"));
    }
}

public class DuplicateTransactionDetectorTests
{
    private readonly IDuplicateTransactionDetector _detector;

    public DuplicateTransactionDetectorTests()
    {
        _detector = new DuplicateTransactionDetector(timeWindowSeconds: 60);
    }

    [Fact]
    public void FindDuplicateTransactions_WithinWindow_GroupsTogether()
    {
        var transactions = new List<DuplicateTransaction>
        {
            new(1, "A", "B", 100m, "food", 1000),
            new(2, "A", "B", 100m, "food", 1030),
            new(3, "A", "B", 100m, "food", 1045)
        };
        
        var duplicates = _detector.FindDuplicateTransactions(transactions);
        
        Assert.Single(duplicates);
        Assert.Equal(3, duplicates[0].Count);
    }

    [Fact]
    public void FindDuplicateTransactions_OutsideWindow_SeparateGroups()
    {
        var transactions = new List<DuplicateTransaction>
        {
            new(1, "A", "B", 100m, "food", 1000),
            new(2, "A", "B", 100m, "food", 1030),
            new(3, "A", "B", 100m, "food", 2000)
        };
        
        var duplicates = _detector.FindDuplicateTransactions(transactions);
        
        Assert.Single(duplicates);
        Assert.Equal(2, duplicates[0].Count);
    }

    [Fact]
    public void FindDuplicateTransactions_DifferentAttributes_NotGrouped()
    {
        var transactions = new List<DuplicateTransaction>
        {
            new(1, "A", "B", 100m, "food", 1000),
            new(2, "C", "D", 200m, "gas", 1030)
        };
        
        var duplicates = _detector.FindDuplicateTransactions(transactions);
        
        Assert.Empty(duplicates);
    }

    [Fact]
    public void FindDuplicateTransactions_SingleTransaction_NoDuplicates()
    {
        var transactions = new List<DuplicateTransaction>
        {
            new(1, "A", "B", 100m, "food", 1000)
        };
        
        var duplicates = _detector.FindDuplicateTransactions(transactions);
        
        Assert.Empty(duplicates);
    }
}
