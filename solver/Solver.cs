// ─────────────────────────────────────────────────────────────
//  Solver — bir tahta durumunun kalan hamlelerle cozulup cozulemedigini
//  BFS ile dogrular. Shuffle booster'i bunu kullanir.
// ─────────────────────────────────────────────────────────────
using System.Collections.Generic;
using System.Text;

namespace Quest2048
{
    public static class Solver
    {
        /// Islenen durum sayisi ust siniri. Asilirsa "cozulemez" kabul edilir (temkinli davranis).
        private const int DEFAULT_NODE_CAP = 250000;

        /// Verilen tahtadan, movesLeft hamle icinde hedeflere ulasilabiliyor mu?
        public static bool IsSolvable(Cell[,] start, List<GoalDef> goals, int iceBrokenSoFar,
                                      int movesLeft, int nodeCap = DEFAULT_NODE_CAP)
        {
            if (movesLeft <= 0) return GameLogic.GoalsMet(start, goals, iceBrokenSoFar);
            if (GameLogic.GoalsMet(start, goals, iceBrokenSoFar)) return true;

            var visited = new HashSet<string>();
            var queue = new Queue<(Cell[,] board, int iceBroken, int depth)>();

            queue.Enqueue((start, iceBrokenSoFar, 0));
            visited.Add(Key(start, iceBrokenSoFar));

            int processed = 0;
            var dirs = new[] { Direction.Left, Direction.Right, Direction.Up, Direction.Down };

            while (queue.Count > 0)
            {
                if (++processed > nodeCap) return false;

                var (board, iceBroken, depth) = queue.Dequeue();
                if (depth >= movesLeft) continue;

                foreach (var dir in dirs)
                {
                    var res = GameLogic.Move(board, dir);
                    if (!res.moved) continue;

                    int newIce = iceBroken + res.iceBroken;
                    if (GameLogic.GoalsMet(res.board, goals, newIce)) return true;

                    string key = Key(res.board, newIce);
                    if (visited.Add(key))
                        queue.Enqueue((res.board, newIce, depth + 1));
                }
            }
            return false;
        }

        private static string Key(Cell[,] b, int iceBroken)
        {
            int n = b.GetLength(0);
            var sb = new StringBuilder(n * n * 4 + 4);
            for (int r = 0; r < n; r++)
                for (int c = 0; c < n; c++)
                {
                    var cell = b[r, c];
                    sb.Append((int)cell.type).Append(':').Append(cell.value).Append(':').Append(cell.color).Append('|');
                }
            sb.Append('#').Append(iceBroken);
            return sb.ToString();
        }
    }
}
