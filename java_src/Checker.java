import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class Checker
{
    public static void main(String[] args) throws IOException
	{
        Scanner in;
        // for each command-line argument
        for (String filename : args)
		{
            // read in the board specified in the filename
            in = new Scanner(new File(filename));
            int N = in.nextInt();
            int[][] tiles = new int[N][N];
            for (int i = 0; i < N; i++) {
                for (int j = 0; j < N; j++) {
                    tiles[i][j] = in.nextInt();
                }
            }

            // solve the slider puzzle
            Board initial = new Board(tiles, null);
			Solver s;

			s = new Solver(initial);

            System.out.println(filename + ": " + s.moves());
        }
    }
}
