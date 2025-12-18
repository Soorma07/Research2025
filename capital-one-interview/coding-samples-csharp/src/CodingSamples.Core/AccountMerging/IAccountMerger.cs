namespace CodingSamples.Core.AccountMerging;

public interface IAccountMerger
{
    List<List<string>> MergeAccounts(List<List<string>> accounts);
}
