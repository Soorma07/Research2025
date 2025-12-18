namespace CodingSamples.Core.GraphProblems;

public interface IGraph<TNode> where TNode : notnull
{
    void AddEdge(TNode u, TNode v, int weight = 1);
    List<TNode> Bfs(TNode start);
    List<TNode> Dfs(TNode start);
    (int Distance, List<TNode> Path) ShortestPathDijkstra(TNode start, TNode end);
    bool HasCycle();
    List<TNode> TopologicalSort();
}
