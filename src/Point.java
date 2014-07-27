public class Point {

    private int x;
    private int y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public void equal(Point a) {
        this.x = a.getX();
        this.y = a.getY();
    }

    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }

    public Point getNorth()
	{
        return new Point(this.x - 1, y);
    }

    public Point getEast()
	{
        return new Point(this.x, y + 1);
    }

    public Point getSouth()
	{
        return new Point(this.x + 1, y);
    }

    public Point getWest()
	{
        return new Point(this.x, y - 1);
    }

    public String toString()
	{
        return "( " + x + ", " + y + " )";
    }
}
