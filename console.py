from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, BarColumn, TimeRemainingColumn
from rich.layout import Layout
import platform

# Check if running under PyPy
is_pypy = platform.python_implementation() == 'PyPy'

class LiveConsole:
    def __init__(self):
        # Skip initialization if running under PyPy
        if is_pypy:
            self.enabled = False
            return
            
        self.console = Console()
        self.avg_points = 0
        self.max_points = 0
        self.live = None
        self.total_sims = 0
        self.total_expected_sims = 3000  # Default value, will be updated
        self.enabled = True
        
    def start_live(self, total_simulations=3000):
        # Don't start if disabled or already running
        if not self.enabled or self.live:
            return
            
        # Reset statistics at the start
        self.avg_points = 0
        self.max_points = -1000
        self.total_sims = 0
        self.total_expected_sims = total_simulations
        
        # Create progress bar
        self.progress = Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
        )
        self.task = self.progress.add_task(
            f"[cyan]Running MCTS simulations... (0/{self.total_expected_sims})", 
            total=self.total_expected_sims
        )
        
        # Create results table
        self.table = Table(title="MCTS Simulation Results")
        self.table.add_column("Player", justify="center", style="cyan", no_wrap=True)
        self.table.add_column("Average Score", justify="center", style="magenta")
        self.table.add_column("Max Score", justify="center", style="magenta")
        self.table.add_column("Current Score", justify="center", style="magenta")
        self.table.add_column("Simulations", justify="center", style="green")
        
        # Create a layout
        self.layout = Layout()
        self.layout_progress = Layout(name="progress", size=3)
        self.layout_table = Layout(name="table")
        self.layout.split(
            self.layout_progress,
            self.layout_table
        )
        
        # Set initial content
        self.layout_progress.update(self.progress)
        self.layout_table.update(self.table)
        
        self.live = Live(self.layout, refresh_per_second=4, console=self.console)
        self.live.start()

    def update_display(self, sim_num, player_info):
        """Update the display with new simulation results"""
        if not self.enabled or not self.live:
            return
            
        try:
            # Update the simulation count (add 1 to convert from 0-indexed)
            self.total_sims = sim_num
            
            # Update progress bar
            self.progress.update(
                self.task, 
                completed=self.total_sims,
                description=f"[cyan]Running MCTS simulations... ({self.total_sims}/{self.total_expected_sims})"
            )
                
            # Update the table with the new results
            self.table = Table(title=f"MCTS Simulation Results")
            self.table.add_column("Player", justify="center", style="cyan", no_wrap=True)
            self.table.add_column("Average Score", justify="center", style="magenta")
            self.table.add_column("Max Score", justify="center", style="magenta")
            self.table.add_column("Current Score", justify="center", style="magenta")
            self.table.add_column("Simulations", justify="center", style="green")
            
            # Calculate running average
            player_points = player_info.get('points', 0)
            
            # Initialize if first update
            if self.total_sims == 10:
                # Initialize the points sum on first update
                if not hasattr(self, 'points_sum'):
                    self.points_sum = 0
                    self.update_count = 0
                self.avg_points = player_points
            else:
                # Keep track of sum and count for accurate average
                if not hasattr(self, 'points_sum'):
                    self.points_sum = self.avg_points * (self.total_sims - 1)
                    self.update_count = self.total_sims - 1
                
                # Add current points to the sum
                self.points_sum += player_points
                self.update_count += 1
                
                # Calculate average based on actual updates
                self.avg_points = self.points_sum / self.update_count
            
            self.max_points = max(self.max_points, player_points)
            
            self.table.add_row(
                player_info.get('name', ''), 
                str(round(self.avg_points, 1)), 
                str(self.max_points), 
                str(player_points),
                str(self.total_sims)
            )
            
            # Update the layout
            self.layout_progress.update(self.progress)
            self.layout_table.update(self.table)
            
            self.live.update(self.layout)
        except Exception as e:
            print(f"Error updating display: {e}")

    def stop(self):
        """Stop the live display"""
        if self.enabled and self.live:
            self.progress.update(self.task, completed=self.total_expected_sims)
            self.live.stop()
            self.live = None