import java.util.PriorityQueue;
import java.util.Stack;

class Solver
{
	private PriorityQueue<Board> optionsQueue = new PriorityQueue<Board>();
	private int move = 0;

	public Solver(Board initial)
	{
		if(initial.isSolvable())
		{
			Board finishedBoard = solveHe(initial);
			move = finishedBoard.moves();
		}
	}

	private Board solveHe(Board currentBoard)
	{
		while(!currentBoard.isGoal())
		{
			for(Board neighborOfBoard : currentBoard.neighbors())
			{  // For ever neighbor in your board

				neighborOfBoard.setMoves(currentBoard.moves() + 1); // Set the number of moves equal to the number of moves to reach the previous path, plus 1
				optionsQueue.offer(neighborOfBoard);  // Add the board into the que.

			}
			currentBoard = optionsQueue.poll(); // Take the next best option of the queue.
		}
		return currentBoard;
	}


	public void printPath(Board temp)
	{
		Stack<Board> printStack = new Stack<Board>();
		while(temp.hasPrevious())
		{
			printStack.push(temp);
			temp = temp.getPrevious();
		}

		for(int i = printStack.size() -1 ; i >= 0; i--) System.out.println(printStack.get(i));
	}

	public int moves()
	{
		return move;
	}


}
