using CodingSamples.Core.TransactionAnalysis;
using CodingSamples.Core.TransactionAnalysis.Rules;

namespace CodingSamples.Tests.TransactionAnalysis;

public class TransactionAnalysisTests
{
    private readonly ISuspiciousAccountDetector _detector;
    private readonly ISuspiciousAccountDetector _optimizedDetector;

    public TransactionAnalysisTests()
    {
        var rules = new ISuspiciousActivityRule[]
        {
            new HighVelocityRule(maxTransactions: 3, windowSeconds: 60),
            new HighAmountRule(maxAmount: 10000m, windowSeconds: 60),
            new MultipleCitiesRule(maxCities: 2, windowSeconds: 600)
        };
        
        _detector = new SuspiciousAccountDetector(rules);
        _optimizedDetector = new OptimizedSuspiciousAccountDetector();
    }

    private List<Transaction> GetSampleTransactions()
    {
        return new List<Transaction>
        {
            new("t1", "acc1", 5000m, 1000, "NYC"),
            new("t2", "acc1", 3000m, 1010, "NYC"),
            new("t3", "acc1", 4000m, 1020, "NYC"),
            
            new("t4", "acc2", 100m, 2000, "LA"),
            new("t5", "acc2", 100m, 2010, "SF"),
            new("t6", "acc2", 100m, 2020, "NYC"),
            new("t7", "acc2", 100m, 2030, "Chicago"),
            
            new("t8", "acc3", 100m, 3000, "Boston"),
            new("t9", "acc3", 100m, 3001, "Boston"),
            new("t10", "acc3", 100m, 3002, "Boston"),
            new("t11", "acc3", 100m, 3003, "Boston"),
            new("t12", "acc3", 100m, 3004, "Boston"),
            
            new("t13", "acc4", 500m, 4000, "Miami"),
            new("t14", "acc4", 500m, 4100, "Miami")
        };
    }

    [Fact]
    public void FindSuspiciousAccounts_HighAmount_FlagsAccount()
    {
        var transactions = GetSampleTransactions();
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.Contains("acc1", result);
    }

    [Fact]
    public void FindSuspiciousAccounts_MultipleCities_FlagsAccount()
    {
        var transactions = GetSampleTransactions();
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.Contains("acc2", result);
    }

    [Fact]
    public void FindSuspiciousAccounts_HighVelocity_FlagsAccount()
    {
        var transactions = GetSampleTransactions();
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.Contains("acc3", result);
    }

    [Fact]
    public void FindSuspiciousAccounts_NormalAccount_NotFlagged()
    {
        var transactions = GetSampleTransactions();
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.DoesNotContain("acc4", result);
    }

    [Fact]
    public void FindSuspiciousAccounts_OptimizedMatchesBasic()
    {
        var transactions = GetSampleTransactions();
        
        var basicResult = _detector.FindSuspiciousAccounts(transactions);
        var optimizedResult = _optimizedDetector.FindSuspiciousAccounts(transactions);
        
        Assert.Equal(basicResult.OrderBy(x => x), optimizedResult.OrderBy(x => x));
    }

    [Fact]
    public void FindSuspiciousAccounts_EmptyTransactions_ReturnsEmptySet()
    {
        var result = _detector.FindSuspiciousAccounts(new List<Transaction>());
        
        Assert.Empty(result);
    }

    [Fact]
    public void FindSuspiciousAccounts_SingleTransaction_NotSuspicious()
    {
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 100m, 1000, "NYC")
        };
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.DoesNotContain("acc1", result);
    }

    [Fact]
    public void FindSuspiciousAccounts_ExactlyThreeTransactions_NotSuspicious()
    {
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 100m, 1000, "NYC"),
            new("t2", "acc1", 100m, 1020, "NYC"),
            new("t3", "acc1", 100m, 1040, "NYC")
        };
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.DoesNotContain("acc1", result);
    }

    [Fact]
    public void FindSuspiciousAccounts_Exactly10000_NotSuspicious()
    {
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 5000m, 1000, "NYC"),
            new("t2", "acc1", 5000m, 1020, "NYC")
        };
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.DoesNotContain("acc1", result);
    }

    [Fact]
    public void FindSuspiciousAccounts_ExactlyTwoCities_NotSuspicious()
    {
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 100m, 1000, "NYC"),
            new("t2", "acc1", 100m, 1100, "LA")
        };
        
        var result = _detector.FindSuspiciousAccounts(transactions);
        
        Assert.DoesNotContain("acc1", result);
    }
}

public class HighVelocityRuleTests
{
    [Fact]
    public void IsSuspicious_MoreThanThreeTransactionsIn60Seconds_ReturnsTrue()
    {
        var rule = new HighVelocityRule(maxTransactions: 3, windowSeconds: 60);
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 100m, 1000, "NYC"),
            new("t2", "acc1", 100m, 1010, "NYC"),
            new("t3", "acc1", 100m, 1020, "NYC"),
            new("t4", "acc1", 100m, 1030, "NYC")
        };
        
        Assert.True(rule.IsSuspicious(transactions));
    }

    [Fact]
    public void IsSuspicious_ExactlyThreeTransactionsIn60Seconds_ReturnsFalse()
    {
        var rule = new HighVelocityRule(maxTransactions: 3, windowSeconds: 60);
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 100m, 1000, "NYC"),
            new("t2", "acc1", 100m, 1020, "NYC"),
            new("t3", "acc1", 100m, 1040, "NYC")
        };
        
        Assert.False(rule.IsSuspicious(transactions));
    }
}

public class HighAmountRuleTests
{
    [Fact]
    public void IsSuspicious_AmountExceeds10000In60Seconds_ReturnsTrue()
    {
        var rule = new HighAmountRule(maxAmount: 10000m, windowSeconds: 60);
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 5000m, 1000, "NYC"),
            new("t2", "acc1", 6000m, 1020, "NYC")
        };
        
        Assert.True(rule.IsSuspicious(transactions));
    }

    [Fact]
    public void IsSuspicious_AmountExactly10000In60Seconds_ReturnsFalse()
    {
        var rule = new HighAmountRule(maxAmount: 10000m, windowSeconds: 60);
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 5000m, 1000, "NYC"),
            new("t2", "acc1", 5000m, 1020, "NYC")
        };
        
        Assert.False(rule.IsSuspicious(transactions));
    }
}

public class MultipleCitiesRuleTests
{
    [Fact]
    public void IsSuspicious_MoreThanTwoCitiesIn10Minutes_ReturnsTrue()
    {
        var rule = new MultipleCitiesRule(maxCities: 2, windowSeconds: 600);
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 100m, 1000, "NYC"),
            new("t2", "acc1", 100m, 1100, "LA"),
            new("t3", "acc1", 100m, 1200, "Chicago")
        };
        
        Assert.True(rule.IsSuspicious(transactions));
    }

    [Fact]
    public void IsSuspicious_ExactlyTwoCitiesIn10Minutes_ReturnsFalse()
    {
        var rule = new MultipleCitiesRule(maxCities: 2, windowSeconds: 600);
        var transactions = new List<Transaction>
        {
            new("t1", "acc1", 100m, 1000, "NYC"),
            new("t2", "acc1", 100m, 1100, "LA")
        };
        
        Assert.False(rule.IsSuspicious(transactions));
    }
}
