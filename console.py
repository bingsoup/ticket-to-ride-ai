from rich.live import Live
from rich.table import Table
from rich.console import Console

class LiveConsole:
    def __init__(self):
        self.console = Console()
        self.avg_points = 0
        self.max_points = 0
        self.live = None
        self.start_live()

    def start_live(self):
        self.table = Table(title="Game Results")
        self.table.add_column("Player", justify="center", style="cyan", no_wrap=True)
        self.table.add_column("Average", justify="center", style="magenta")
        self.table.add_column("Max", justify="center", style="magenta")
        self.table.add_column("Current", justify="center", style="magenta")
        self.live = Live(self.table, refresh_per_second=1, console=self.console)
        self.live.start()

    def print_results(self, game_num, player):
        # Update the table with the new results
        self.table = Table(title=f"Game {game_num} Results")
        self.table.add_column("Player", justify="center", style="cyan", no_wrap=True)
        self.table.add_column("Average", justify="center", style="magenta")
        self.table.add_column("Max", justify="center", style="magenta")
        self.table.add_column("Current", justify="center", style="magenta")
        
        self.avg_points = (self.avg_points * (game_num - 1) + player.points) / game_num
        self.max_points = max(self.max_points, player.points)
        
        self.table.add_row(player.name, str(round(self.avg_points)), str(self.max_points), str(player.points))
        
        self.live.update(self.table)

    def stop(self):
        self.live.stop()
        self.table = None
        self.max_points = 0
        self.avg_points = 0