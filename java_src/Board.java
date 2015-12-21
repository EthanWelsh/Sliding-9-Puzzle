import java.util.ArrayList;

class Board implements Comparable<Board>
{

	private int[][] board;
	private final int size;
	private Point blank;


	private Board previous;

	private String apple = null;

	private int moves = 0;


	final char north = 'n';
	final char east = 'e';
	final char south = 's';
	final char west = 'w';
	char whereICameFrom;


	public Board(int[][] blocks, Board p)
	{ // Construct a board from an N-by-N array
		board = new int[blocks.length][blocks.length];
		this.size = blocks.length;

		for (int r = 0; r < size; r++) System.arraycopy(blocks[r], 0, board[r], 0, size);

		for (int r = 0; r < size; r++)
		{
			for (int c = 0; c < size; c++)
			{
				if (board[r][c] == 0)
				{
					blank = new Point(r, c);
					break;
				}
			}
		}

		previous = p;

	}

	public Board getPrevious()
	{
		return previous;
	}

	public boolean hasPrevious()
	{
		return previous != null;
	}

	public ArrayList<Board> neighbors()
	{
		ArrayList<Board> n = new ArrayList<Board>();
		Board temp;
		Point blank = this.getBlank();

		if(whereICameFrom != north && canSwap(blank.getNorth()))
		{
			temp = new Board(this.board, this);

			temp.setDirection(south);

			temp.swap(temp.getBlank().getNorth());
			n.add(temp);
		}

		if(whereICameFrom != east && canSwap(blank.getEast()))
		{
			temp = new Board(this.board, this);

			temp.setDirection(west);

			temp.swap(temp.getBlank().getEast());
			n.add(temp);
		}

		if(whereICameFrom != south && canSwap(blank.getSouth()))
		{
			temp = new Board(this.board, this);
			temp.setDirection(north);
			temp.swap(temp.getBlank().getSouth());
			n.add(temp);
		}

		if(whereICameFrom != west && canSwap(blank.getWest()))
		{
			temp = new Board(this.board, this);
			temp.setDirection(east);
			temp.swap(temp.getBlank().getWest());
			n.add(temp);
		}

		return n;
	}

	public int dimension()
	{ // Dimension N
		return size;
	}

	int manhattan()
	{
		int[][] perfectBoard = new int[size][size];
		int index = 1;

		for (int r = 0; r < size; r++) // Build perfect
			for (int c = 0; c < size; c++)
			{
				if (index < (size * size)) perfectBoard[r][c] = index;
				else perfectBoard[r][c] = 0;
				index++;
			}

		int man = 0;

		for (int r = 0; r < size; r++)
			for (int c = 0; c < size; c++)
			{
				if (board[r][c] != 0 && (board[r][c] != perfectBoard[r][c]))
				{
					int rShould = 0;
					int cShould = 0;

					for (int j = 0; j < size; j++)
						for (int i = 0; i < size; i++)
						{
							if (perfectBoard[j][i] == board[r][c])
							{
								rShould = j;
								cShould = i;
							}
						}
					man = man + Math.abs(rShould - r) + Math.abs(cShould - c);
				}
			}

		return man;

	}

	int hamming()
	{
		int[][] perfectBoard = new int[size][size];
		int index = 1;

		for (int r = 0; r < size; r++)
			for (int c = 0; c < size; c++)
			{
				if (index < (size * size)) perfectBoard[r][c] = index;
				else perfectBoard[r][c] = 0;
				index++;
			}

		int ham = 0;
		for (int r = 0; r < size; r++)
			for (int c = 0; c < size; c++) if (board[r][c] != 0 && (board[r][c] != perfectBoard[r][c])) ham++;

		return ham;
	}

	public int compareTo(Board arg0)
	{
		if (arg0.getPriority() > this.getPriority()) return -1;
		else if (arg0.getPriority() < this.getPriority()) return 1;
		else return 0;
	}

	public boolean isGoal()
	{ // Is this the goal board
		return this.hamming() == 0;
	}

	public boolean isSolvable()
	{ // Is this board solvable
		Board temp = new Board(this.board, this);

		Point p = new Point(size - 1, size - 1);

		while (temp.getNum(p) != 0)
		{ // Get the blank square into the bottom right corner.
			if(canSwap(temp.getBlank().getEast())) temp.swap(temp.getBlank().getEast());
			if(canSwap(temp.getBlank().getSouth())) temp.swap(temp.getBlank().getSouth());
		}

		int inversions = 0;
		ArrayList<Integer> squ = new ArrayList<Integer>();
		for (int r = 0; r < size; r++) for (int c = 0; c < size; c++) squ.add(board[r][c]);

		int totalNumbers = size * size;
		int numOfNumLess;

		for (int whatNumberToStartOn = 0; whatNumberToStartOn < totalNumbers; whatNumberToStartOn++)
		{
			numOfNumLess = 0;
			for (int i = whatNumberToStartOn; i < totalNumbers; i++)
				if (squ.get(i) != 0 && (squ.get(i) < squ.get(whatNumberToStartOn))) numOfNumLess++;
			inversions = inversions + numOfNumLess;
		}

		return inversions % 2 == 0;
	}

	public boolean equals(Object y)
	{  //Does this board equal Y
		return this.toString().equals(y.toString());
	}

	Point getBlank()
	{
		return blank;
	}

	public void setMoves(int x)
	{
		moves = x;
	}

	public int moves()
	{
		return moves;
	}

	int getPriority()
	{
		return moves + this.hamming() + this.manhattan();

		//return moves + this.manhattan();
	}

	public String toString()
	{ // String representation of the board
		String x = "";

		if(apple == null) {
			for (int r = 0; r < size; r++)
			{
				for (int c = 0; c < size; c++)
				{
					x = x + (board[r][c] + " ");
				}
				x = x + "\n";
			}
			return x;
		} else return apple;
	}

	void swap(Point a)
	{
		int currentlyBlank = getNum(blank);
		int blankAfterSwap = getNum(a);

		board[blank.getX()][blank.getY()] = blankAfterSwap;
		board[a.getX()][a.getY()] = currentlyBlank;
		blank.equal(a);

		apple = null;
		apple = this.toString();

	}

	boolean canSwap(Point a)
	{
		return !((a.getX() > size - 1 || a.getY() > size - 1) || (a.getX() < 0 || a.getY() < 0));
	}

	int getNum(Point ccc)
	{
		return board[ccc.getX()][ccc.getY()];
	}

	public int hashCode()
	{
		return this.toString().hashCode();
	}

	private void setDirection(char x) {
		whereICameFrom = x;
	}

}
