import pygame
import threading
import time
import queue
import sys
import copy

class TicketToRideGUI:
    # City coordinates for USA map
    USA_CITY_POSITIONS = {
    "Seattle": (100, 100),
    "Portland": (120, 150),
    "San Francisco": (100, 300),
    "Los Angeles": (150, 350),
    "Salt Lake City": (250, 250),
    "Las Vegas": (200, 320),
    "Phoenix": (230, 370),
    "Denver": (300, 280),
    "Santa Fe": (300, 350),
    "Oklahoma City": (400, 350),
    "Dallas": (420, 400),
    "Houston": (440, 430),
    "El Paso": (320, 400),
    "Winnipeg": (400, 100),
    "Duluth": (450, 200),
    "Omaha": (400, 250),
    "Kansas City": (400, 300),
    "Chicago": (500, 250),
    "Saint Louis": (480, 320),
    "Nashville": (520, 360),
    "New Orleans": (500, 450),
    "Little Rock": (450, 370),
    "Toronto": (600, 200),
    "Pittsburgh": (580, 260),
    "Washington": (620, 300),
    "Raleigh": (600, 340),
    "Atlanta": (550, 380),
    "Charleston": (600, 380),
    "Miami": (620, 480),
    "New York": (640, 260),
    "Boston": (670, 230),
    "Montreal": (650, 180),
    "Sault St. Marie": (520, 180),
    "Calgary": (200, 100),
    "Helena": (250, 180),
    "Vancouver": (80, 80),
    }

    # City coordinates for Europe map
    EUROPE_CITY_POSITIONS = {
        "Edinburgh": (280, 150),
        "London": (300, 220),
        "Amsterdam": (380, 220),
        "Bruxelles": (370, 250),
        "Paris": (350, 300),
        "Dieppe": (320, 270),
        "Brest": (250, 300),
        "Pamplona": (300, 400),
        "Madrid": (250, 450),
        "Lisboa": (180, 470),
        "Cadiz": (230, 520),
        "Barcelona": (350, 430),
        "Marseille": (400, 380),
        "Zurich": (420, 320),
        "Frankfurt": (430, 270),
        "Munchen": (470, 300),
        "Venezia": (470, 350),
        "Roma": (470, 410),
        "Brindisi": (520, 440),
        "Palermo": (480, 480),
        "Kobenhavn": (450, 180),
        "Essen": (430, 230),
        "Berlin": (480, 230),
        "Danzic": (530, 200),
        "Stockholm": (500, 130),
        "Riga": (570, 170),
        "Petrograd": (630, 150),
        "Warszawa": (550, 250),
        "Wien": (510, 300),
        "Budapest": (550, 330),
        "Kyiv": (630, 310),
        "Wilno": (600, 230),
        "Smolensk": (650, 230),
        "Moskva": (700, 200),
        "Kharkov": (680, 320),
        "Rostov": (720, 350),
        "Bucuresti": (600, 370),
        "Sofia": (580, 400),
        "Constantinople": (620, 430),
        "Angora": (680, 450),
        "Sevastopol": (670, 390),
        "Erzurum": (750, 430),
        "Athina": (570, 460),
        "Smyrna": (620, 470),
    }
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Constants
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.BACKGROUND_COLOR = (240, 230, 200)
        self.TEXT_COLOR = (0, 0, 0)
        self.HIGHLIGHT_COLOR = (255, 255, 0)
        self.PLAYER_COLORS = [(255, 0, 0), (0, 0, 255), (0, 128, 0), (255, 165, 0)]
        self.CITY_COLOR = (100, 100, 100)
        self.ROUTE_COLOR = (150, 150, 150)
        self.FONT_SIZE = 20
        
        # State variables
        self.city_positions = {}
        self.screen = None
        self.font = None
        self.action_log = []
        self.running = False
        
        # Thread management
        self.update_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.gui_thread = None
    
    def initialize(self):
        """Initialize the GUI in a separate thread"""
        # Don't start a new thread if one is already running
        if self.gui_thread and self.gui_thread.is_alive():
            return True
        
        # Initially set city_positions to empty (will be populated later)
        self.city_positions = {}
        
        try:
            # Create and start the GUI thread
            self.gui_thread = self._GUIThread(self)
            self.gui_thread.start()
            
            # Wait for the thread to be ready
            if not self.gui_thread.ready.wait(timeout=5.0):
                print("GUI thread initialization timed out")
                return False
                
            return True
        except Exception as e:
            print(f"Failed to initialize GUI: {e}")
            return False
    
    def update_game_state(self, game, action=None):
        """Update the GUI with the current game state"""
        if not self.running or not self.gui_thread or not self.gui_thread.is_alive():
            return
        
        try:
            # Determine which map type is being used (only needs to be done once)
            if not self.city_positions:
                self.set_map_type(game)
            
            # Create a thread-safe copy of the game state
            game_state = {
                'players': [],
                'current_player_idx': game.current_player_idx,
                'connections': []
            }
            
            # Add action if provided
            if action:
                game_state['action'] = self.format_action(action)
            
            # Get connections from game state
            if hasattr(game, 'routes') and game.routes:
                for city1, destinations in game.routes.items():
                    for city2 in destinations:
                        if city1 < city2:  # Only add each connection once
                            game_state['connections'].append((city1, city2))
            
            # Convert players to dict
            for i, player in enumerate(game.players):
                # Get agent type
                agent_type = ""
                if hasattr(game, 'player_agents') and player.name in game.player_agents:
                    agent_id = game.player_agents[player.name]
                    if hasattr(game, 'agent_options') and agent_id in game.agent_options:
                        agent_type = game.agent_options[agent_id]
                    else:
                        agent_types = {
                            1: "Human Player",
                            2: "MCTS AI",
                            3: "Destination Heuristic AI",
                            4: "Longest Route Heuristic AI",
                            5: "Opportunistic Heuristic AI", 
                            6: "Best Move Heuristic AI",
                            7: "Random AI",
                            8: "Neural Network AI"
                        }
                        agent_type = agent_types.get(agent_id, f"Agent {agent_id}")
                
                player_dict = {
                    'name': player.name,
                    'agent_type': agent_type,
                    'points': player.points,
                    'remaining_trains': player.remaining_trains,
                    'train_cards': dict(player.train_cards),
                    'destinations': list(player.destinations),
                    'claimed_connections': [list(conn) for conn in player.claimed_connections],
                }
                game_state['players'].append(player_dict)
            
            # Send to GUI thread through queue
            self.update_queue.put(game_state)
        except Exception as e:
            print(f"Error updating game state: {e}")
    
    def shutdown(self):
        """Safely shutdown the GUI thread"""
        if self.running and self.gui_thread and self.gui_thread.is_alive():
            print("Sending shutdown command to GUI thread...")
            self.command_queue.put("quit")
            
            # Wait for thread to finish (with timeout)
            self.gui_thread.join(timeout=2.0)
            
            # If thread is still alive, it might be stuck
            if self.gui_thread.is_alive():
                print("GUI thread did not terminate gracefully")
            else:
                print("GUI thread terminated successfully")
        
        self.running = False
    
    def set_map_type(self, game):
        """Determine which map is being used and set the appropriate city positions"""
        # Check if this is a Europe map by looking for European cities
        europe_cities = ["London", "Paris", "Berlin", "Roma"]
        usa_cities = ["Seattle", "New York", "Chicago", "Los Angeles"]
        
        # Check which cities are in the game's city_to_idx dictionary
        if hasattr(game, 'city_to_idx'):
            # Check if European cities are present
            europe_count = sum(1 for city in europe_cities if city in game.city_to_idx)
            usa_count = sum(1 for city in usa_cities if city in game.city_to_idx)
            
            if europe_count > usa_count:
                self.city_positions = self.EUROPE_CITY_POSITIONS
                print("Detected Europe map")
                return "Europe"
            else:
                self.city_positions = self.USA_CITY_POSITIONS
                print("Detected USA map")
                return "USA"
        
        # If we can't determine, default to USA map
        self.city_positions = self.USA_CITY_POSITIONS
        print("Defaulting to USA map")
        return "USA"
    
    def format_action(self, action):
        """Format an action for display"""
        if not action:
            return "No action"
        
        try:
            action_type = action[0]
            player_name = action[-1]  # Player name is the last element
            
            if action_type == "claim_route":
                return f"{player_name} claimed route: {action[1]} to {action[2]} with {action[3]} cards"
            elif action_type == "draw_two_train_cards":
                if action[1] == "deck":
                    return f"{player_name} drew card from deck"
                else:
                    return f"{player_name} drew {action[2]} card from position {action[1]}"
            elif action_type == "draw_destination_tickets":
                kept_count = action[1] + action[2] + action[3]
                return f"{player_name} drew destination tickets and kept {kept_count}"
            else:
                return f"{player_name}: {str(action)}"
        except Exception as e:
            print(f"Error formatting action: {e}")
            return str(action)
    
    class _GUIThread(threading.Thread):
        """Internal thread class that handles the pygame display loop"""
        def __init__(self, parent):
            threading.Thread.__init__(self, daemon=True)
            self.parent = parent
            self.game_state = None
            self.ready = threading.Event()
        
        def run(self):
            try:
                # Initialize pygame display
                print("Initializing GUI thread...")
                self.parent.screen = pygame.display.set_mode((self.parent.WIDTH, self.parent.HEIGHT))
                pygame.display.set_caption("Ticket to Ride AI - Game Viewer")
                self.parent.font = pygame.font.SysFont('Arial', self.parent.FONT_SIZE)
                
                # Signal that we're ready
                self.parent.running = True
                self.ready.set()
                print("GUI thread ready")
                
                # Initial screen setup
                self.parent.screen.fill(self.parent.BACKGROUND_COLOR)
                self._draw_initial_screen()
                pygame.display.flip()
                
                # Main GUI loop
                clock = pygame.time.Clock()
                while self.parent.running:
                    # Process pygame events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self._handle_quit()
                    
                    # Check for commands from main thread
                    try:
                        while not self.parent.command_queue.empty():
                            cmd = self.parent.command_queue.get_nowait()
                            if cmd == "quit":
                                self._handle_quit()
                                break
                    except queue.Empty:
                        pass
                    
                    # Check for game state updates
                    try:
                        while not self.parent.update_queue.empty():
                            self.game_state = self.parent.update_queue.get_nowait()
                            self._update_display()
                    except queue.Empty:
                        pass
                    
                    # Limit frame rate to save CPU
                    clock.tick(30)
                
                print("GUI thread exiting normally")
            except Exception as e:
                print(f"Error in GUI thread: {e}")
            finally:
                # Clean up
                self.parent.running = False
                pygame.quit()
        
        def _handle_quit(self):
            self.parent.running = False
            print("GUI shutdown requested")
        
        def _draw_initial_screen(self):
            """Draw the initial screen before any game state is available"""
            self.parent.screen.fill(self.parent.BACKGROUND_COLOR)
            font = pygame.font.SysFont('Arial', 24)
            text = font.render("Waiting for game to start...", True, self.parent.TEXT_COLOR)
            text_rect = text.get_rect(center=(self.parent.WIDTH//2, self.parent.HEIGHT//2))
            self.parent.screen.blit(text, text_rect)
        
        def _update_display(self):
            """Update the display with current game state"""
            if not self.game_state:
                return
                
            try:
                # Clear screen
                self.parent.screen.fill(self.parent.BACKGROUND_COLOR)
                
                # Draw game elements
                self._draw_map()
                self._draw_player_routes()
                self._draw_cities()
                self._draw_player_info()
                self._draw_action()
                
                # Update display
                pygame.display.flip()
            except Exception as e:
                print(f"Error updating display: {e}")
        
        def _draw_map(self):
            """Draw the game map with cities and routes"""
            try:
                # Draw background
                pygame.draw.rect(self.parent.screen, (220, 200, 160), (50, 50, 700, 500))
                
                # Draw routes from game state connections
                if self.game_state and 'connections' in self.game_state:
                    for city1, city2 in self.game_state['connections']:
                        if city1 in self.parent.city_positions and city2 in self.parent.city_positions:
                            pos1 = self.parent.city_positions[city1]
                            pos2 = self.parent.city_positions[city2]
                            pygame.draw.line(self.parent.screen, self.parent.ROUTE_COLOR, pos1, pos2, 1)
                
                # Draw cities as dots
                for city, pos in self.parent.city_positions.items():
                    pygame.draw.circle(self.parent.screen, self.parent.CITY_COLOR, pos, 5)
            except Exception as e:
                print(f"Error drawing map: {e}")
        
        def _draw_cities(self):
            """Draw city names on the map"""
            try:
                # Draw all city names (with smaller font to avoid clutter)
                small_font = pygame.font.SysFont('Arial', 12)
                
                for city, pos in self.parent.city_positions.items():
                    text = small_font.render(city, True, self.parent.TEXT_COLOR)
                    self.parent.screen.blit(text, (pos[0] - 15, pos[1] - 15))
            except Exception as e:
                print(f"Error drawing cities: {e}")
        
        def _draw_player_routes(self):
            """Draw claimed routes on the map"""
            try:
                if not self.game_state or 'players' not in self.game_state:
                    return
                    
                # Draw each player's claimed connections
                for i, player in enumerate(self.game_state['players']):
                    color = self.parent.PLAYER_COLORS[i % len(self.parent.PLAYER_COLORS)]
                    if 'claimed_connections' in player:
                        for connection in player['claimed_connections']:
                            if len(connection) >= 2:
                                city1, city2 = connection[0], connection[1]
                                if city1 in self.parent.city_positions and city2 in self.parent.city_positions:
                                    pos1 = self.parent.city_positions[city1]
                                    pos2 = self.parent.city_positions[city2]
                                    pygame.draw.line(self.parent.screen, color, pos1, pos2, 4)
                                    
                                    # Draw a small circle in the middle of the line
                                    mid_x = (pos1[0] + pos2[0]) // 2
                                    mid_y = (pos1[1] + pos2[1]) // 2
                                    pygame.draw.circle(self.parent.screen, color, (mid_x, mid_y), 5)
            except Exception as e:
                print(f"Error drawing player routes: {e}")
        
        def _draw_player_info(self):
            """Draw player information panels"""
            try:
                if not self.game_state or 'players' not in self.game_state:
                    return
                    
                panel_width = 350
                panel_height = 120
                panel_x = 800
                
                for i, player in enumerate(self.game_state['players']):
                    panel_y = 50 + i * (panel_height + 10)
                    
                    # Draw panel background with highlight for current player
                    if i == self.game_state.get('current_player_idx', 0):
                        pygame.draw.rect(self.parent.screen, self.parent.HIGHLIGHT_COLOR, 
                                       (panel_x-5, panel_y-5, panel_width+10, panel_height+10))
                    
                    # Panel background
                    pygame.draw.rect(self.parent.screen, (255, 255, 255), 
                                   (panel_x, panel_y, panel_width, panel_height))
                    
                    # Player name and agent type
                    player_name = f"Player {i+1}"
                    agent_type = player.get('agent_type', '')
                    
                    if agent_type:
                        name_text = self.parent.font.render(f"{player_name}: {agent_type}", True, self.parent.TEXT_COLOR)
                    else:
                        name_text = self.parent.font.render(f"{player_name}", True, self.parent.TEXT_COLOR)
                        
                    self.parent.screen.blit(name_text, (panel_x + 10, panel_y + 10))
                    
                    # Draw player stats
                    self._draw_player_stats(player, panel_x, panel_y)
            except Exception as e:
                print(f"Error drawing player info: {e}")
        
        def _draw_player_stats(self, player, panel_x, panel_y):
            """Draw player statistics in the panel"""
            # Score
            score_text = self.parent.font.render(f"Score: {player.get('points', 0)}", True, self.parent.TEXT_COLOR)
            self.parent.screen.blit(score_text, (panel_x + 10, panel_y + 40))
            
            # Trains remaining
            trains_text = self.parent.font.render(f"Trains: {player.get('remaining_trains', 45)}", True, self.parent.TEXT_COLOR)
            self.parent.screen.blit(trains_text, (panel_x + 10, panel_y + 70))
            
            # Cards (simplified)
            cards_text = self.parent.font.render(f"Cards: {sum(player.get('train_cards', {}).values())}", True, self.parent.TEXT_COLOR)
            self.parent.screen.blit(cards_text, (panel_x + 150, panel_y + 40))
            
            # Destination tickets
            dest_text = self.parent.font.render(f"Destinations: {len(player.get('destinations', []))}", True, self.parent.TEXT_COLOR)
            self.parent.screen.blit(dest_text, (panel_x + 150, panel_y + 70))
        
        def _draw_action(self):
            """Draw the most recent action"""
            try:
                if not self.game_state or 'action' not in self.game_state:
                    return
                    
                # Add action to log
                self.parent.action_log.append(self.game_state['action'])
                if len(self.parent.action_log) > 10:
                    self.parent.action_log.pop(0)
                
                # Draw action log panel
                panel_x = 50
                panel_y = 580
                panel_width = 700
                panel_height = 170
                
                pygame.draw.rect(self.parent.screen, (255, 255, 255), 
                               (panel_x, panel_y, panel_width, panel_height))
                               
                title_text = self.parent.font.render("Recent Actions:", True, self.parent.TEXT_COLOR)
                self.parent.screen.blit(title_text, (panel_x + 10, panel_y + 10))
                
                # Draw action log entries
                for i, log_entry in enumerate(reversed(self.parent.action_log)):
                    if i >= 5:  # Limit to 5 most recent actions
                        break
                    action_text = self.parent.font.render(str(log_entry), True, self.parent.TEXT_COLOR)
                    self.parent.screen.blit(action_text, (panel_x + 10, panel_y + 40 + i * 25))
            except Exception as e:
                print(f"Error drawing action: {e}")

# Create global singleton instance and expose public methods
_gui_instance = None

def initialize_gui():
    global _gui_instance
    if _gui_instance is None:
        _gui_instance = TicketToRideGUI()
    return _gui_instance.initialize()

def update_game_state(game, action=None):
    global _gui_instance
    if _gui_instance:
        _gui_instance.update_game_state(game, action)

def shutdown():
    global _gui_instance
    if _gui_instance:
        _gui_instance.shutdown()