namespace CodingSamples.Core.AccountMerging;

public class DfsAccountMerger : IAccountMerger
{
    public List<List<string>> MergeAccounts(List<List<string>> accounts)
    {
        var graph = new Dictionary<string, HashSet<string>>();
        var emailToName = new Dictionary<string, string>();

        foreach (var account in accounts)
        {
            string name = account[0];
            var emails = account.Skip(1).ToList();

            foreach (var email in emails)
            {
                emailToName[email] = name;
                if (!graph.ContainsKey(email))
                {
                    graph[email] = new HashSet<string>();
                }
            }

            for (int i = 0; i < emails.Count; i++)
            {
                for (int j = i + 1; j < emails.Count; j++)
                {
                    graph[emails[i]].Add(emails[j]);
                    graph[emails[j]].Add(emails[i]);
                }
            }
        }

        var visited = new HashSet<string>();
        var result = new List<List<string>>();

        void Dfs(string email, List<string> component)
        {
            visited.Add(email);
            component.Add(email);

            if (graph.TryGetValue(email, out var neighbors))
            {
                foreach (var neighbor in neighbors)
                {
                    if (!visited.Contains(neighbor))
                    {
                        Dfs(neighbor, component);
                    }
                }
            }
        }

        foreach (var email in emailToName.Keys)
        {
            if (!visited.Contains(email))
            {
                var component = new List<string>();
                Dfs(email, component);
                string name = emailToName[email];
                var merged = new List<string> { name };
                merged.AddRange(component.OrderBy(e => e));
                result.Add(merged);
            }
        }

        return result;
    }
}
