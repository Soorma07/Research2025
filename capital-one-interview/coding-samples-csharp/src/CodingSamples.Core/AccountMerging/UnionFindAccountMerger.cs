namespace CodingSamples.Core.AccountMerging;

public class UnionFindAccountMerger : IAccountMerger
{
    public List<List<string>> MergeAccounts(List<List<string>> accounts)
    {
        var uf = new UnionFind();
        var emailToName = new Dictionary<string, string>();
        var emailToId = new Dictionary<string, int>();

        for (int i = 0; i < accounts.Count; i++)
        {
            var account = accounts[i];
            string name = account[0];
            var emails = account.Skip(1).ToList();

            foreach (var email in emails)
            {
                emailToName[email] = name;

                if (!emailToId.ContainsKey(email))
                {
                    emailToId[email] = i;
                }

                uf.Union(emails[0], email);
            }
        }

        var rootToEmails = new Dictionary<string, HashSet<string>>();
        foreach (var email in emailToName.Keys)
        {
            string root = uf.Find(email);
            if (!rootToEmails.ContainsKey(root))
            {
                rootToEmails[root] = new HashSet<string>();
            }
            rootToEmails[root].Add(email);
        }

        var result = new List<List<string>>();
        foreach (var (root, emails) in rootToEmails)
        {
            string name = emailToName[root];
            var merged = new List<string> { name };
            merged.AddRange(emails.OrderBy(e => e));
            result.Add(merged);
        }

        return result;
    }
}
