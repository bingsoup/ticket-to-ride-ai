import time
from typing import List, Optional,Tuple
import random
from mcts import MCTS
#from console import LiveConsole
#from graph import TicketToRideVisualizer
from fw import FloydWarshall
from map_data import MapData
from helper_classes import UnionFind, Destination, Player, Color, Route
from heuristic_agents import DestinationHeuristic, LongestRouteHeuristic, OpportunisticHeuristic, RandomHeuristic, BestMoveHeuristic
from play import TicketToRideGame
import platform
is_pypy = platform.python_implementation() == 'PyPy'
# Only import GUI modules if not running under PyPy
if not is_pypy:
    try:
        from gui import initialize_gui, update_game_state, shutdown
        gui_available = True
    except ImportError:
        gui_available = False
        print("GUI modules couldn't be imported. Running in console-only mode.")
else:
    # Create dummy functions for GUI operations when running under PyPy
    gui_available = False
    def initialize_gui(): return False
    def update_game_state(game, action=None): pass
    def shutdown(): pass
    print("Running under PyPy - GUI disabled for compatibility.")
# Handles the game state, including the board, players, current player index, score, train deck, destination deck, and face-up cards
class GameState:
    def __init__(self):
        self.routes = {} # Maps city1 -> city2 -> List[Route]
        self.players: List[Player] = [] # List of players
        self.current_player_idx: int = 0 # Index of the current player
        self.current_player: Player = None # Reference to the current player
        self.train_deck: List[Color] = [] # Train deck
        self.discard_deck: List[Color] = [] # Discard deck
        self.destination_deck: List[Destination] = []  # Destination ticket deck
        self.destination_discard_deck: List[Destination] = []  # Discard deck for destination tickets
        self.face_up_cards: List[Color] = [] # Face-up cards
        #self.visualizer = TicketToRideVisualizer(self) # Displays the board state in image form
        self.fw = None # Floyd-Warshall object for shortest path calculations
        self.update = None # Update queue for visualizer
        self.routes_cache = {}    # Player dependent cache for unclaimed routes
        self.routes_cache_valid = {}   # Flag to indicate if cache needs update
        self.best_routes_cache = {}    # Player dependent cache for best routes
        self.best_routes_cache_valid = {} # Flag to indicate if cache needs update
        self.map_type = "USA" # Default map type
        self.map_data = None # Map data object
        
    def init(self, players: List[Player]):
        """
        It got complicated to do in the constructor and I wanted it to happen more sequentially so i split it up.
        """
        self.players = players
        self.map_data = MapData(self.map_type)
        self.initialise_destination_deck()
        self.initialise_routes()
        
        self.fw = FloydWarshall(self.routes)
        # Add 12 of each color (excluding wild) and 14 wild cards
        self.setup_train_deck()
        self.deal_initial_cards()
        # Draw initial face-up cards
        self.face_up_cards = [self.train_deck.pop() for _ in range(5)]
        self.current_player = self.players[self.current_player_idx]

        self.init_uf()
    
    def formatted_trains(self, player: Player) -> List[str]: 
        return [f"{color.name.capitalize()}: {count}" for color, count in player.train_cards.items() if count > 0]

    def formatted_destinations(self, player: Player) -> List[str]: 
        return [f"{destination.city1} to {destination.city2} ({destination.points})" for destination in player.destinations]
    
    def formatted_colors(self, colors: List[Color]) -> List[str]:
        return [color.name.capitalize() for color in colors]

    def deal_initial_cards(self):
        for player in self.players:
            # Deal 4 train cards to each player
            for _ in range(4):
                card = self.train_deck.pop()
                player.train_cards[card] += 1
            # Deal 3 destination cards, player must keep at least 2
            destinations = [self.destination_deck.pop() for _ in range(3)]
            # TODO - player must keep at least 2 & can discard 1
            player.destinations.extend(destinations[:3])
                    
            print(f"{player.name} has been dealt the following destinations: {', '.join(self.formatted_destinations(player))}")
            print(f"{player.name} has been dealt the following train cards: {', '.join(self.formatted_trains(player))}")

    def init_uf(self):
        for player in self.players:
            player.uf = UnionFind(self.routes.keys())

    def initialise_destination_deck(self):
        # Add destination tickets to the deck
        self.destination_deck = self.map_data.get_destinations()
        random.shuffle(self.destination_deck)
        
    def initialise_routes(self):
        """
        Initialise routes datastructure (routes = Dict{"city1", Dict{"city2", List[Route]}})
        It's innefficient as hell but the most readable way I could think of, so I build indices for faster lookups.
        self.routes is only used on initialisation of indices and other datastructures and never again.

        Indices:
            city_to_routes: Maps cities to all routes from that city
            route_pairs: Maps (city1,city2) to its routes
            city_names: List of all city names
            city_to_idx: Maps city name to relative index
            idx_to_city: Maps index to city name
            adjacency: Adjacency matrix (i = city1, j = city2)
        """
        self.routes = self.map_data.get_routes()
         # Add these indices at the end:
        self.city_to_routes = {}  # Maps cities to their routes
        self.route_pairs = {}     # Maps (city1,city2) to route objects
        
        # Build indices
        for city1, connections in self.routes.items():
            if city1 not in self.city_to_routes:
                self.city_to_routes[city1] = []
                
            for city2, routes_list in connections.items():
                # Get canonical order of cities (alphabetical)
                key = (city1, city2) if city1 < city2 else (city2, city1)
                
                # Store in route_pairs
                if key not in self.route_pairs:
                    self.route_pairs[key] = []
                self.route_pairs[key].extend(routes_list)
                
                # Store in city_to_routes
                self.city_to_routes[city1].extend([(city2, route) for route in routes_list])

        self.city_names = sorted(list(set(
            [city for routes in self.routes.values() 
                for city in routes.keys()] + 
            [city for city in self.routes.keys()]
        )))
        self.city_to_idx = {city: i for i, city in enumerate(self.city_names)}
        self.idx_to_city = {i: city for i, city in enumerate(self.city_names)}
        
        # Create adjacency matrix for faster lookups
        n = len(self.city_names)
        self.adjacency = [[[] for _ in range(n)] for _ in range(n)]
        
        for city1, connections in self.routes.items():
            i = self.city_to_idx[city1]
            for city2, routes_list in connections.items():
                j = self.city_to_idx[city2]
                self.adjacency[i][j] = routes_list
        

    def route_lookup(self, city1: str, city2: str) -> List[Route]:
        """
        AM route lookup for adjacency between two cities

        Args:
            city1: First city
            city2: Second city
        
        Returns:
            List of routes between the two cities
        """
        if hasattr(self, 'city_to_idx') and city1 in self.city_to_idx and city2 in self.city_to_idx:
            i = self.city_to_idx[city1]
            j = self.city_to_idx[city2]
            return self.adjacency[i][j]
        return self.get_routes_between_cities(city1, city2)

    def update_player_turn(self):
        """
        Update the current player to the next in the list
        """
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.current_player = self.players[self.current_player_idx]

    def get_routes_between_cities(self, city1: str, city2: str) -> List[Route]:
        """
        Get routes between cities using optimized lookup
        
        Args:
            city1: First city
            city2: Second city

        Returns:
            List of routes between the two cities
        
        """
        # First, try adjacency matrix for fastest lookup
        if hasattr(self, 'city_to_idx') and city1 in self.city_to_idx and city2 in self.city_to_idx:
            i = self.city_to_idx[city1]
            j = self.city_to_idx[city2]
            if self.adjacency[i][j]:  # If routes exist
                return self.adjacency[i][j]
        
        # Next, try route_pairs
        if hasattr(self, 'route_pairs'):
            key = (city1, city2) if city1 < city2 else (city2, city1)
            if key in self.route_pairs:
                return self.route_pairs[key]
        
        print(f"Routes between {city1} and {city2} not found")
        return []
        
    def get_unclaimed_routes(self) -> List[tuple[str, str, Route]]:
        """
        Get all unclaimed routes using adjacency matrix

        Returns:
            List of tuples where each tuple is:
                city1: First city
                city2: Second city
                route: Route object between the two
        """
        
        unclaimed = []
        n = len(self.city_names)
        
        # Iterate through only the upper triangular part of the matrix
        # (since the graph is undirected)
        for i in range(n):
            city1 = self.idx_to_city[i]
            for j in range(i+1, n):  # Start from i+1 to avoid duplicates
                city2 = self.idx_to_city[j]
                
                # Get routes from the adjacency matrix
                routes_list = self.adjacency[i][j]
                
                # Add unclaimed routes
                for route in routes_list:
                    if route.claimed_by is None:
                        unclaimed.append((city1, city2, route))
        
        return unclaimed
    
    def set_player_routes(self):
        """
        Get all unclaimed routes using adjacency matrix, with player-specific caching.

        Returns:
            List of actions where each action is a tuple:
            ("claim_route", city1, city2, color, player)
        """
        current_player = self.current_player
        cache_key = current_player.name
        
        # Return cached result if available
        if cache_key in self.routes_cache and self.routes_cache_valid.get(cache_key, False):
            return self.routes_cache[cache_key].copy()
        
        route_actions = []
        n = len(self.city_names)
        
        # Iterate through adjacency matrix
        for i in range(n):
            city1 = self.idx_to_city[i]
            for j in range(i+1, n):  
                city2 = self.idx_to_city[j]
                routes_list = self.adjacency[i][j]
                for route in routes_list:
                    if route.claimed_by is None:
                        if current_player.remaining_trains > route.length:
                            # For gray routes, check each color
                            if route.color == Color.GRAY:
                                for color in Color:
                                    if color != Color.WILD and color != Color.GRAY:
                                        cards_needed = route.length
                                        cards_available = current_player.train_cards[color]
                                        wilds_available = current_player.train_cards[Color.WILD]
                                        wilds_required = route.num_locomotives
                                        wilds_needed = max(wilds_required,(route.length - current_player.train_cards[color]))
                                        
                                        if cards_available + wilds_available >= cards_needed + wilds_required:
                                            for wilds_used in range(wilds_needed,wilds_available + 1):
                                                wilds_used - 1
                                                route_actions.append(
                                                    ("claim_route", city1, city2, color, wilds_used, route, current_player.name)
                                                )
                            else:
                                # For colored routes
                                color = route.color  
                                cards_needed = route.length
                                cards_available = current_player.train_cards[color]
                                wilds_available = current_player.train_cards[Color.WILD]
                                wilds_needed = max(0,(route.length - current_player.train_cards[color]))
                                if cards_available + wilds_available >= cards_needed:
                                    for wilds_used in range(wilds_needed,wilds_available + 1):
                                        wilds_used - 1
                                        route_actions.append(
                                            ("claim_route", city1, city2, color, wilds_used, route, current_player.name)
                                        )
        
        # Store in cache
        self.routes_cache[cache_key] = route_actions.copy()
        self.routes_cache_valid[cache_key] = True
        
        return route_actions
    
    def claim_route_helper(self, color: Color, player: str, num_hits: int, routes) -> bool:
        """Claims the route if possible, otherwise returns False."""
        claimed = [False] * len(routes)
        for i, route in enumerate(routes):
            claimed[i] = route.is_claimed()
            if (color == Color.WILD or route.color == color or route.color == Color.GRAY) and not claimed[i]:
                if self.current_player.train_cards[color] + self.current_player.train_cards[Color.WILD] >= route.length + num_hits:
                    # Update route state
                    route.claim(player)
                    # Invalidate cache when route is claimed
                    for player in self.players:
                        self.routes_cache_valid[player.name] = False
                else:
                    claimed[i] = True
                    if (num_hits == 0):
                        print(f"Player {player} does not have enough cards to claim route")
                        
        if all(claimed):
            return False
        return True
    
    def claim_route(self, city1: str, city2: str, color: Color, player: str, num_hits: int) -> bool:
        """
        Checks whether any of the routes between cities with a given can be claimed
        I have to to do it like this because you can have multiple gray routes between two cities
        And all of them must be claimable...
        Args:
            city1: First city
            city2: Second city
            color: Color of the route
            player: Player claiming the route
            num_hits: Precomputed number of hits for tunnel routes
        """
        routes = self.route_lookup(city1, city2)
        if len(routes) == 4:
            path1 = [routes[0],routes[2]]
            p1 = self.claim_route_helper(color, player, num_hits, path1)
            if p1: return True
            path2 = [routes[1], routes[3]]
            p2 = self.claim_route_helper(color, player, num_hits, path2)
            if p2: return True
            return False
        else: # Only one direction so can claim both
            if self.claim_route_helper(color, player, num_hits, routes): return True
        return False

    def check_hits(self, route: Route, color) -> bool:
        """Checks if the player can still claim it if tunnel hits"""
        num_hits = 0
        if route.tunnel:
            if len(self.train_deck) > 3:
                for i in range(3):
                    if self.train_deck[i] == Color.WILD or self.train_deck[i] == color:
                        num_hits += 1
        return num_hits
        
    def get_route_length(self, city1: str, city2: str) -> Optional[int]:
        """Get the length of a specific route."""
        routes = self.route_lookup(city1, city2)
        return routes[0].length
    
    def setup_train_deck(self):
        for color in Color:
            if color != Color.WILD and color != Color.GRAY:
                self.train_deck.extend([color] * 12)
        self.train_deck.extend([Color.WILD] * 14)
        random.shuffle(self.train_deck)

    def draw_train_face(self, i: int, card: Color):
        """Draw a face-up card."""
        if len(self.train_deck) == 0:
            if len(self.discard_deck) == 0:
                print("Broken")
                return
            self.train_deck.extend(self.discard_deck)
            self.discard_deck.clear()
        self.face_up_cards.pop(i)
        self.face_up_cards.append(self.train_deck.pop())
        self.players[self.current_player_idx].train_cards[card] += 1
    
    def draw_train_deck(self):
        """Draw a card from the train deck."""
        if len(self.train_deck) == 0:
            if len(self.discard_deck) == 0:
                print("Broken")
                return
            self.train_deck.extend(self.discard_deck)
            self.discard_deck.clear()
        card = self.train_deck.pop()
        self.players[self.current_player_idx].train_cards[card] += 1

    def check_all_destinations(self, player) -> List[Tuple[Destination, bool]]:
        # Check if the player has completed all destination tickets using union-find
        destination_results = []
        for destination in player.destinations:
            city1, city2 = destination.city1, destination.city2
            if player.uf.is_connected(city1, city2):
                destination_results.append((destination, True))
            else:
                destination_results.append((destination, False))
        return destination_results
    
    def calc_route_points(self, route_length: int) -> int:  
        if route_length == 1:
            return 1
        elif route_length == 2:
            return 2
        elif route_length == 3:
            return 4
        elif route_length == 4:
            return 7
        elif route_length == 5:
            return 10
        elif route_length == 6:
            return 15
        elif route_length == 8:
            return 21
        
    def print_owned_routes(self):
        for player in self.players:
            num_trains = 45 - player.remaining_trains
            used_trains = 0
            print(f"{player.name} has claimed the following routes:")
            for city1, city2, color in player.claimed_connections:
                used_trains += self.get_route_length(city1, city2)
                print(f"{city1} to {city2} with {color} and length {self.get_route_length(city1, city2)}")
            
            if used_trains != num_trains:
                print(f"Bug occurred, printing entire route list:")
                for city1 in self.adjacency:
                    for city2 in city1:
                        for route in city2:
                            if route.claimed_by == player.name:
                                print(f"{city1} to {city2} with {route.color} and length {route.length}")
                    

    # MCTS methods
    def copy(self):
        # Create a new instance
        new_state = GameState()
        
        # Copy id values
        new_state.current_player_idx = self.current_player_idx
        
        # Copy simple collections directly
        new_state.train_deck = self.train_deck.copy() if self.train_deck else []
        new_state.destination_deck = self.destination_deck.copy() if self.destination_deck else []
        new_state.face_up_cards = self.face_up_cards.copy() if self.face_up_cards else []
        
        # Copy indexing structures (these are mostly immutable after creation)
        if hasattr(self, 'city_names'):
            new_state.city_names = self.city_names.copy()
        if hasattr(self, 'city_to_idx'):
            new_state.city_to_idx = self.city_to_idx.copy()
        if hasattr(self, 'idx_to_city'):
            new_state.idx_to_city = self.idx_to_city.copy()
        
        # More efficient copying of lookup structures
        if hasattr(self, 'city_to_routes'):
            new_state.city_to_routes = {}
            for city, routes in self.city_to_routes.items():
                new_state.city_to_routes[city] = routes.copy()
        
        if hasattr(self, 'route_pairs'):
            new_state.route_pairs = {}
            for key, routes in self.route_pairs.items():
                new_state.route_pairs[key] = [Route(r.length, r.color, r.claimed_by) for r in routes]
        
        # Efficiently copy adjacency matrix if it exists
        if hasattr(self, 'adjacency') and self.adjacency:
            n = len(self.adjacency)
            new_state.adjacency = [[[] for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    if self.adjacency[i][j]:  # Only copy non-empty lists
                        new_state.adjacency[i][j] = [Route(r.length, r.color, r.claimed_by) for r in self.adjacency[i][j]]
        
        # Copy caches over
        new_state.routes_cache = self.routes_cache.copy() if self.routes_cache else {}
        new_state.routes_cache_valid = self.routes_cache_valid.copy() if self.routes_cache_valid else {}
        new_state.best_routes_cache = self.best_routes_cache.copy() if self.best_routes_cache else {}
        new_state.best_routes_cache_valid = self.best_routes_cache_valid.copy() if self.best_routes_cache_valid else {}
        
        # Handle FloydWarshall - lazy instantiation
        new_state.fw = self.fw
        
        # Don't copy update reference
        new_state.update = None
    
        # Copy players
        new_state.players = []
        for player in self.players:
            # Create new player with basic attributes
            new_player = Player(name=player.name, remaining_trains=player.remaining_trains)
            
            # Copy collections
            new_player.train_cards = {color: count for color, count in player.train_cards.items()}
            new_player.destinations = player.destinations.copy() if player.destinations else []
            new_player.claimed_connections = player.claimed_connections.copy() if player.claimed_connections else []
            new_player.claimed_cities = set(player.claimed_cities) if player.claimed_cities else set()
            # Copy integer values
            new_player.points = player.points
            new_player.turn = player.turn
            
            # Recreate UnionFind instead of copying it
            if player.uf:
                new_player.uf = UnionFind(self.city_names)
                # Only rebuild connections that matter
                for city1, city2, _ in player.claimed_connections:
                    new_player.uf.union(city1, city2)
            
            new_state.players.append(new_player)
        
        # Fix current player reference
        new_state.current_player = new_state.players[new_state.current_player_idx] if new_state.players else None
        return new_state
        
    def apply_action(self, action):
        player = self.current_player
        match action:
            case ["draw_two_train_cards", idx1, card1, idx2, card2, player_name]:
                if card1 != "deck":
                    self.draw_train_face(idx1, card1)
                else:
                    self.draw_train_deck()
                if card2 != "nodraw":
                    if card2 != "deck":
                        self.draw_train_face(idx2, card2)
                    else:
                        self.draw_train_deck()
            case ["claim_route", city1, city2, color, wilds_used, route, player_name]:    
                num_hits = self.check_hits(route, color)                    
                if self.claim_route(city1, city2, color, player_name, num_hits):
                    route_length = self.get_route_length(city1, city2)
                    total_length = (route_length + num_hits)

                    # Calculate the minimum number of wilds the player now has to use to complete the route
                    # Or return False if not possible because of too many tunnel hits.
                    if num_hits > 0:
                        if total_length > player.train_cards[color]:
                            wilds_used += total_length - player.train_cards[color]
                            if wilds_used > player.train_cards[Color.WILD]:
                                if wilds_used > player.train_cards[Color.WILD]:
                                    return False
                                
                    # If the route is in the best routes cache, invalidate it
                    if self.best_routes_cache.get(player_name, False):
                        for i in range(len(self.best_routes_cache[player.name])):
                            if (self.best_routes_cache[player.name][i][1] == (city1 or city2) and self.best_routes_cache[player.name][i][2] == (city1 or city2)):
                                self.best_routes_cache_valid[player.name] = False

                    player.train_cards[Color.WILD] -= wilds_used
                    player.train_cards[color] -= max(0, total_length - wilds_used)
                    self.discard_deck.extend([Color.WILD] * wilds_used)
                    self.discard_deck.extend([color] * (total_length - wilds_used))
                    player.claimed_connections.append((city1, city2, color))
                    player.claimed_cities.add(city1)
                    player.claimed_cities.add(city2)
                    points = self.calc_route_points(route_length)
                    if points is not None:
                        player.points += points
                    else:
                        print(f"Error: route length is {route_length}")
                    player.uf.union(city1, city2)
                    player.remaining_trains -= route_length
                    return True
                return False
            case ["draw_destination_tickets", i, j, k, player_name]:
                choices = []
                destinations = []
                # If we draw a destination ticket, invalidate the best routes cache
                if self.best_routes_cache_valid.get(player_name, False):
                    self.best_routes_cache_valid[player_name] = False

                if len(self.destination_deck) < 3:
                    self.destination_deck.extend(self.destination_discard_deck)
                    self.destination_discard_deck.clear()
                    random.shuffle(self.destination_deck)
                for p in range(3):
                    choices.append(self.destination_deck.pop(0)) 
                if i == 1:
                    destinations.append(choices[0])
                if j == 1:
                    destinations.append(choices[1])
                if k == 1:
                    destinations.append(choices[2])
                if i + j + k == 0:
                    destinations.append(choices[random.randint(0,2)])
                self.destination_discard_deck.extend([dest for dest in choices if dest not in destinations])
                self.current_player.destinations.extend(destinations)

    def apply_action_final(self, action):
        success = self.apply_action(action)

        print(f"{self.current_player.name}'s hand:")
        for color, count in self.current_player.train_cards.items():
            if count > 0:
                print(f"{color.name.capitalize()}: {count}")
        match action:
            case ["draw_two_train_cards", idx1, card1, idx2, card2, player_name]:
                print(f"{player_name} has drawn two train cards: {card1}, {card2}")
            
            case ["claim_route", city1, city2, color, wilds_used, route, player_name]:
                route_length = self.get_route_length(city1, city2)
                num_hits = self.check_hits(route, color)
                if success:
                    if num_hits > 0:
                        print(f"{player_name} has claimed a route of length {route_length} between {city1} and {city2} with {color} using {wilds_used} wild cards and {num_hits} hits")
                    elif wilds_used > 0:
                        print(f"{player_name} has claimed a route of length {route_length} between {city1} and {city2} with {color} using {wilds_used} wild cards")
                    else:
                        print(f"{player_name} has claimed a route of length {route_length} between {city1} and {city2} with {color}")
                else:
                    print(f"{player_name} got too many hits between {city1} and {city2} with {color}")
                
            case ["draw_destination_tickets", i, j, k, player_name]:
                ijk = sum([i,j,k])
                print(f"{player_name} has drawn destination tickets and kept {ijk}")
        
        print(f"Remaining trains {self.current_player.name}: {self.current_player.remaining_trains}")
        dest_completion = self.get_distance(self.current_player)
        for destination in dest_completion:
            distance = destination[1]
            dest = destination[0]
            if distance == 0:
                print(f"{self.current_player.name} has completed destination ticket {dest.city1} to {dest.city2} ({dest.points} points)")
            else:
                print(f"{self.current_player.name} is {distance} trains away from completing destination ticket {dest.city1} to {dest.city2} ({dest.points} points)")
        print("")
            
    def is_end(self):
        # Check if the game state is terminal
        return any([True for player in self.players if player.remaining_trains <= 2])
    
    def get_legal_actions(self):
        legal_actions = []
        current_player = self.current_player
        
        legal_actions = self.set_player_routes()
        
        # Draw two train cards. Enumerate all possible combinations of face-up cards and deck cards
        if len(self.train_deck) + len(self.discard_deck) > 10: # Dont hog cards
            for i, card1 in enumerate(self.face_up_cards):
                if card1 != Color.WILD:
                    for j, card2 in enumerate(self.face_up_cards):
                        if j == i:
                            if len(self.train_deck) > 0:
                                card2 = self.train_deck[0]
                        if card2 != Color.WILD:
                            legal_actions.append(("draw_two_train_cards", i, card1, j, card2, current_player.name))
                    legal_actions.append(("draw_two_train_cards", i, card1, "deck", "deck", current_player.name))
                else:
                    legal_actions.append(("draw_two_train_cards", i, card1, "nodraw", "nodraw", current_player.name))
            legal_actions.append(("draw_two_train_cards", "deck", "deck", "deck", "deck", current_player.name))
        # TODO - Definitely should bias towards not drawing destinations if the player hasnt completed many yet
        num_destinations = len(current_player.destinations)
        if num_destinations < 10:
            if len(self.destination_deck) >= 5:
                # Draw destination tickets: scry three, keep minimum one
                for i in range(2):
                    for j in range(2):
                        for k in range(2):
                            if i + j + k >= 1:
                                legal_actions.append(("draw_destination_tickets", i, j, k, current_player.name))
        return legal_actions

    
    def one_off(self,) -> bool:
        #Check if the player only needs one more turn to finish a destination ticket.
        player = self.current_player
        for destination in player.destinations:
            city1, city2 = destination.city1, destination.city2
            if player.uf.is_connected(city1,city2):
                continue #destination is already connected, skip
            
            one_off = self.fw.get_one_off_cities(city1)
            if any(player.uf.is_connected(city2, city1off) for city1off in one_off):
                return True
            # other direction
            one_off = self.fw.get_one_off_cities(city2)
            if any(player.uf.is_connected(city1, city2off) for city2off in one_off):
                return True
        return False
    
    def get_longest_route_length(self, player):
        """Calculate the longest continuous route for a player by counting train cars"""
        if not player.claimed_connections:
            return 0
        
        # Build weighted adjacency list from player's claimed connections
        connections = {}
        for city1, city2, _ in player.claimed_connections:
            route_length = self.get_route_length(city1, city2)
            
            if city1 not in connections:
                connections[city1] = []
            if city2 not in connections:
                connections[city2] = []
                
            # Store the destination city and the route length
            connections[city1].append((city2, route_length))
            connections[city2].append((city1, route_length))
        
        # DFS to find longest path from each starting city
        max_length = 0
        
        def dfs(city, visited, path_length):
            visited.add(city)
            longest = path_length
            
            for next_city, route_length in connections.get(city, []):
                if next_city not in visited:
                    # Add the actual route length to the path
                    longest = max(longest, dfs(next_city, visited, path_length + route_length))
            
            visited.remove(city)  # Backtrack
            return longest
        
        # Try each city as a starting point
        for city in player.claimed_cities:
            if city in connections:
                length = dfs(city, set(), 0)
                max_length = max(max_length, length)
        
        return max_length
    
    def remove_destination_tickets(self, player, destinations_remove):
        player.destinations = [dest for i, dest in enumerate(player.destinations) if destinations_remove[i] == 1]

    def get_distance(self, player):
        """
        Calculate how close a player is to completing each destination ticket by checking
        all controlled cities against all destination endpoints.
        
        Returns a list of tuples (destination, distance) where distance is the
        minimum number of train pieces needed to connect the destination cities.
        A distance of 0 means the destination is already completed.
        """
        results = []
        
        # For each destination ticket
        for destination in player.destinations:
            city1, city2 = destination.city1, destination.city2
            
            # If already completed
            if player.uf.is_connected(city1, city2):
                results.append((destination, 0))
                continue
            
            # Direct distance between endpoints as fallback
            direct_distance = self.fw.get_distance(city1, city2)
            min_distance = direct_distance
            
            # Check every controlled city for potential connections
            for controlled_city in player.claimed_cities:
                # Calculate distances from this controlled city to both endpoints
                dist_to_city1 = float('inf')
                dist_to_city2 = float('inf')
                
                # Check if the controlled city is directly one of the endpoints
                if controlled_city == city1:
                    dist_to_city1 = 0
                elif controlled_city == city2:
                    dist_to_city2 = 0
                
                # Find the shortest path from this city to each endpoint
                # (Only if we need to calculate it - if it's not already 0)
                if dist_to_city1 > 0:
                    # Check if controlled_city is connected to city1 through the network
                    if player.uf.is_connected(controlled_city, city1):
                        dist_to_city1 = 0
                    else:
                        # Use Floyd-Warshall to get shortest path
                        dist_to_city1 = self.fw.get_distance(controlled_city, city1)
                
                if dist_to_city2 > 0:
                    # Check if controlled_city is connected to city2 through the network
                    if player.uf.is_connected(controlled_city, city2):
                        dist_to_city2 = 0
                    else:
                        # Use Floyd-Warshall to get shortest path
                        dist_to_city2 = self.fw.get_distance(controlled_city, city2)
                
                # If either distance is invalid, skip this city
                if dist_to_city1 < 0 or dist_to_city2 < 0:
                    continue
                    
                # Calculate combined distance (from controlled city to both endpoints)
                total_distance = dist_to_city1 + dist_to_city2
                
                # Update minimum distance if this is better
                if total_distance < min_distance:
                    min_distance = total_distance
            
            # Sanity check for extreme values
            if min_distance < 0 or min_distance > 25:
                min_distance = direct_distance
                
            results.append((destination, min_distance))
        
        return results
    
    def select_best_route_action(self, route_actions):
        """
        Selects a route action that helps complete destination tickets,
        with a penalty for routes requiring additional cards.
        
        Args:
            route_actions: List of claim_route actions
            
        Returns:
            A claim_route action that helps complete a destination ticket,
            or None if none are particularly beneficial
        """
        if not route_actions:
            return None
            
        player = self.current_player
        beneficial_actions = []
        
        # Group destination tickets by cities for faster lookup
        city_to_dest = {}
        for i, dest in enumerate(player.destinations):
            if dest.city1 not in city_to_dest:
                city_to_dest[dest.city1] = []
            if dest.city2 not in city_to_dest:
                city_to_dest[dest.city2] = []
            # Store index instead of Destination object
            city_to_dest[dest.city1].append(i)
            city_to_dest[dest.city2].append(i)
        
        # Check if claiming a route directly completes a destination
        for action in route_actions:
            city1, city2 = action[1], action[2]
            color = action[3]
            wilds_used = action[4]
            route = action[5]
            score = 0

            # Calculate card penalty (100 points per card needed)
            route_length = route.length
            cards_available = player.train_cards[color]
            cards_needed = max(0, route_length - cards_available - player.train_cards[Color.WILD])
            card_penalty = cards_needed * 100
            
            # Check if this route directly connects the endpoints of a destination
            for dest in player.destinations:
                if (city1 == dest.city1 and city2 == dest.city2) or (city1 == dest.city2 and city2 == dest.city1):
                    if not player.uf.is_connected(dest.city1, dest.city2):
                        # Direct completion - highest priority, but with card penalty
                        beneficial_actions.append((action, 1000 + dest.points - card_penalty))
                        continue
            
            # Check if route connects clusters that contain destination endpoints
            connects_clusters = False
            for dest in player.destinations:
                # Skip completed destinations
                if player.uf.is_connected(dest.city1, dest.city2):
                    continue
                    
                c1_connected = player.uf.is_connected(dest.city1, city1) or player.uf.is_connected(dest.city1, city2)
                c2_connected = player.uf.is_connected(dest.city2, city1) or player.uf.is_connected(dest.city2, city2)
                
                if c1_connected and c2_connected:
                    # This route will connect two clusters containing our destination endpoints
                    beneficial_actions.append((action, 500 + dest.points - card_penalty))
                    connects_clusters = True
                    break
            
            if connects_clusters:
                continue
                
            # Check if route extends a cluster towards a destination endpoint
            # This is less valuable but still good
            relevant_dest_indices = []
            if city1 in city_to_dest:
                relevant_dest_indices.extend(city_to_dest[city1])
            if city2 in city_to_dest:
                relevant_dest_indices.extend(city_to_dest[city2])
            
            # Use a set for the indices to remove duplicates
            for idx in set(relevant_dest_indices):
                dest = player.destinations[idx]
                # Skip completed destinations
                if player.uf.is_connected(dest.city1, dest.city2):
                    continue
                    
                # Award points based on destination value
                score += dest.points // 2
            
            if score > 0:
                # Apply card penalty to this score too
                beneficial_actions.append((action, score - card_penalty))
        
        # If we found beneficial actions, choose from the top ones
        if beneficial_actions:
            # Sort by score (higher is better)
            beneficial_actions.sort(key=lambda x: x[1], reverse=True)
            
            # Choose from the top 3 or fewer if there aren't that many
            top_count = min(3, len(beneficial_actions))
            top_actions = []
            for i in range(top_count):
                top_actions.append(beneficial_actions[i][0])

            return top_actions
        
        # If no beneficial actions found, return no action
        return None
        
    def select_best_draw_action(self, draw_actions):
        """
        Selects a draw action that helps complete destination tickets,
        with a penalty for routes requiring additional cards.
        
        Args:
            draw_actions: List of draw actions
            
        Returns:
            The most beneficial draw action,
            or None if none are beneficial
        """
        # Assume the player can claim any route
        n = len(self.city_names)

        current_player = self.current_player
        cache_key = current_player.name
        
        if cache_key in self.best_routes_cache and self.best_routes_cache_valid.get(cache_key, False):
            best_routes = self.best_routes_cache[cache_key]
        else:
            # Construct a list of all possible route actions with no card expectations
            route_actions = []
            for i in range(n):
                city1 = self.idx_to_city[i]
                for j in range(i+1, n):  
                    city2 = self.idx_to_city[j]
                    routes_list = self.adjacency[i][j]
                    for route in routes_list:
                        if route.claimed_by is None:
                            if current_player.remaining_trains > route.length:
                                # For gray routes, check each color
                                if route.color == Color.GRAY:
                                    for color in Color:
                                        if color != Color.WILD and color != Color.GRAY:
                                            route_actions.append(
                                                        ("claim_route", city1, city2, color, 0, route, current_player.name)
                                                    )  
                                else:
                                    # For colored routes
                                    color = route.color  
                                    route_actions.append(
                                                        ("claim_route", city1, city2, color, 0, route, current_player.name)
                                                    )
            # Best possible route
            best_routes = self.select_best_route_action(route_actions)
            # Cache them
            self.best_routes_cache_valid[cache_key] = True 
            self.best_routes_cache[cache_key] = best_routes

        if not best_routes:
            return None
        
        # Set best and second best colors
        best_color = best_routes[0][3]
        if len(best_routes) > 1:
            best_color_2 = best_routes[1][3]
            if best_color_2 == best_color:
                if len(best_routes) > 2:
                    best_color_2 = best_routes[2][3]
                else:
                    best_color_2 = best_color
        else:
            best_color_2 = best_color

        # Store actions which include the best color
        best_draw_actions = []
        for action in draw_actions:
            if (action[2] or action[4]) == best_color:
                best_draw_actions.append(action)
        
        # If there are any actions that draw two of the best colour or a combo of best and second best, return that
        if len(best_draw_actions) > 0:
            
            for action in best_draw_actions:
                if action[2] == action[4]:
                    return action
                elif (action[2] or action[4]) == best_color_2:
                    return action
                
            # Otherwise just return any action that draws the best colour
            return best_draw_actions[0]

        # If no actions draw the best colour, try with second best colour
        best_draw_actions = []
        for action in draw_actions:
             if (action[2] or action[4]) == best_color_2:
                best_draw_actions.append(action)
        
        if len(best_draw_actions) > 0:
            for action in best_draw_actions:
                if (action[2] and action[4]) == best_color_2:
                    return action
            return best_draw_actions[0]
        
        # Couldn't find any actions that draw the best or second best color
        return None

    def select_initial_destinations(self, current_player):
        """
        Pick the destinations which are most likely to be completed using a simple heuristic.
        
        Returns:
            List of binary values [1,1,0] indicating which tickets to keep
        """
        options = current_player.destinations
        if not options or len(options) == 0:
            return []
        
        # Get minimum number of tickets required to keep
        min_to_keep = 2
        num_options = len(options)
        
        # Get Floyd-Warshall paths for optimal routing
        fw = self.fw
        
        # Store complete path sequences (not just sets of cities)
        path_sequences = []
        for dest in options:
            # Get optimal path cities - preserve order to check for shared edges
            if hasattr(fw, 'get_path'):
                path = fw.get_path(dest.city1, dest.city2)
            else:
                # Fallback if get_path doesn't exist
                path = [dest.city1, dest.city2]
            path_sequences.append((dest, path))
        
        # Calculate a score for each destination ticket
        ticket_scores = []
        for dest_idx, (dest, path) in enumerate(path_sequences):
            # Get direct distance between cities
            distance = fw.get_distance(dest.city1, dest.city2)
            
            # Calculate points-per-train ratio (higher is better)
            points_per_distance = dest.points / max(distance, 1)
            
            # Calculate path segment overlap and city intersections with other destinations
            path_overlap_score = 0
            intersection_score = 0
            
            for other_idx, (other_dest, other_path) in enumerate(path_sequences):
                if dest_idx == other_idx:
                    continue
                
                # Look for shared edges (consecutive city pairs)
                shared_edges = 0
                for i in range(len(path)-1):
                    city1, city2 = path[i], path[i+1]
                    # Check if this edge (city1->city2) exists in the other path
                    for j in range(len(other_path)-1):
                        if (other_path[j] == city1 and other_path[j+1] == city2) or \
                        (other_path[j] == city2 and other_path[j+1] == city1):
                            shared_edges += 1
                            break
                
                # Add value for shared edges (major bonus - saves actual trains)
                if shared_edges > 0:
                    path_overlap_score += (shared_edges * other_dest.points / 15)
                
                # Add intersection bonus (minor bonus - potential hub cities)
                # Check for city intersections that aren't already counted in shared edges
                path_set = set(path)
                other_set = set(other_path)
                intersections = path_set.intersection(other_set)
                
                # Don't double-count: subtract cities that are part of shared edges
                edge_cities = set()
                for i in range(len(path)-1):
                    city1, city2 = path[i], path[i+1]
                    for j in range(len(other_path)-1):
                        if (other_path[j] == city1 and other_path[j+1] == city2) or \
                        (other_path[j] == city2 and other_path[j+1] == city1):
                            edge_cities.add(city1)
                            edge_cities.add(city2)
                
                # Only count intersections that aren't part of shared edges
                unique_intersections = intersections - edge_cities
                if unique_intersections:
                    # Small bonus for intersecting cities (much less than shared edges)
                    intersection_score += (len(unique_intersections) * other_dest.points / 40)
            
            # Calculate final score with bonuses for shared edges, intersections, and endpoints
            final_score = points_per_distance + (path_overlap_score * 0.8) + (intersection_score * 0.2) 
            
            # Small penalty for very long tickets (higher risk)
            if distance > 12:
                final_score *= 0.9
                
            ticket_scores.append((dest, final_score))
        
        # Sort tickets by score (descending)
        ticket_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create result array (1 = keep, 0 = discard)
        result = [0] * num_options
        
        # Keep the highest scoring tickets
        if len(ticket_scores) >= 3 and ticket_scores[2][1] >= 1.4:
            tickets_to_keep = 3
        else: 
            tickets_to_keep = min(min_to_keep, max(num_options, len(ticket_scores)))
        
        # Get the indices of the best tickets
        best_tickets = [options.index(t[0]) for t in ticket_scores[:tickets_to_keep]]
        
        # Set those indices to 1 (keep)
        for idx in best_tickets:
            result[idx] = 1
        
        # Print info about selection
        print("Destination ticket selection:")
        for i, dest in enumerate(options):
            status = "Keep" if result[i] == 1 else "Discard"
            score = next((s for d, s in ticket_scores if d == dest), 0)
            print(f"{status}: {dest.city1} to {dest.city2} ({dest.points} points, score: {score:.2f})")
        
        return result

    def switch_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.current_player = self.players[self.current_player_idx]

    def game_result(self, game_num):
        player = self.current_player
        opponent = self.players[(self.current_player_idx + 1) % len(self.players)]
        
        # Calculate destination ticket points
        destination_results = self.check_all_destinations(player)
        for destination, is_complete in destination_results:
            if is_complete:
                player.points += destination.points
            else:
                player.points -= destination.points
        
        # Award longest route bonus (10 points)
        player_longest = self.get_longest_route_length(player)
        opponent_longest = self.get_longest_route_length(opponent)
        
        # Store the length for potential display/debugging
        player.longest_route_length = player_longest
        opponent.longest_route_length = opponent_longest
        
        # Award bonus to player with longer route
        if player_longest > opponent_longest:
            player.points += 10  # Bonus for longest route
        elif player_longest < opponent_longest:
            opponent.points += 10
        else:
            player.points += 10  # Award to both players in case of tie
            opponent.points += 10  
        if self.update:
            self.update.publish("mcts_update", game_num, player)
        return player.points
    
    def print_score(self):
        longest_route = 5
        for player in self.players:
            temp_points = player.points
            destination_results = self.check_all_destinations(player)
            longest = self.get_longest_route_length(player)

            if longest >= longest_route:
                temp_points += 10
                longest_route = longest
    
            for destination, is_complete in destination_results:
                if is_complete:
                    temp_points += destination.points
                else:
                    temp_points -= destination.points
            print(f"Perceived Score {player.name}: {temp_points}")
    
    def game_result_final(self, game_num):
        print(f"Game {game_num}:")
        
        # First calculate longest routes
        longest_routes = [(player, self.get_longest_route_length(player)) for player in self.players]
        longest_routes.sort(key=lambda x: x[1], reverse=True) # Sort by length
        
        # Award bonus to player with longest route
        if longest_routes[0][1] >= 5:
            if longest_routes[0][1] > longest_routes[1][1]:
                longest_player = longest_routes[0][0]
                longest_player.points += 10
                print(f"{longest_player.name} gets 10 bonus points for the longest continuous route of length {longest_routes[0][1]}!")
            else:
                longest_player1, longest_player2 = longest_routes[0][0], longest_routes[1][0]
                longest_player1.points += 10
                longest_player2.points += 10
                print(f"{longest_player1.name} and {longest_player2.name} both get 10 bonus points for the longest continuous route of length {longest_routes[0][1]}!")
        else:
            print("No player gets longest route.")
        
        # Calculate and display final scores for each player
        for player in self.players:
            print(f"Score {player.name}: {player.points}")
            destination_results = self.check_all_destinations(player)
            for destination, is_complete in destination_results:
                if is_complete:
                    player.points += destination.points
                    print(f"Destination between {destination.city1} and {destination.city2} has been completed. Total score: {player.points}")
                else:
                    player.points -= destination.points
                    print(f"Destination between {destination.city1} and {destination.city2} has not been completed. Total score: {player.points}")
            
            # Show longest route length for each player
            print(f"Longest continuous route: {self.get_longest_route_length(player)}")
            print("Final score: ", player.points)
        

def main():
    timestart = time.time()
    game = GameState()

    use_gui = input("Do you want to use the GUI? (y/n): ").lower() == 'y'
    if use_gui:
        initialize_gui()
    
    # Ask user for number of players and agent types
    print("\nWelcome to Ticket to Ride!")
    
    while True:
        try:
            num_players = int(input("How many players? (2-4): "))
            if 2 <= num_players <= 4:
                break
            else:
                print("Please enter a number between 2 and 4.")
        except ValueError:
            print("Please enter a valid number.")
    while True:
        try:
            map_type = input("Which map would you like to play on? (USA or Europe): ").lower()
            if map_type == "usa":
                game.map_type = "USA"
                break
            elif map_type == "europe":
                game.map_type = "Europe"
                break
            else:
                print("Please enter USA or Europe.")
        except ValueError:
            print("Please enter text.")
    
    # Define agent options
    agent_options = {
        1: "Human Player (Untested)",
        2: "MCTS AI",
        3: "Destination Heuristic AI",
        4: "Longest Route Heuristic AI",
        5: "Opportunistic Heuristic AI",
        6: "Best Move Heuristic AI",
        7: "Random AI"
    }
    
    # Create players array and agent mapping
    players = []
    player_agents = {}  # Maps player name to agent type
    mcts_params = {}    # Store custom MCTS parameters for each player
    
    for i in range(num_players):
        print(f"\nPlayer {i+1} options:")
        for key, value in agent_options.items():
            print(f"{key}: {value}")
        
        while True:
            try:
                agent_type = int(input(f"Select agent type for Player {i+1}: "))
                if 1 <= agent_type <= len(agent_options):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(agent_options)}.")
            except ValueError:
                print("Please enter a valid number.")
        
        # If MCTS AI is selected, prompt for parameters
        if agent_type == 2:
            # Get number of simulations
            while True:
                try:
                    num_sims = int(input(f"Enter number of simulations for MCTS (500-20000, default: 3000)"))
                    if 500 <= num_sims <= 20000:
                        break
                    else:
                        print("Please enter a number between 500 and 20000.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Get max depth
            while True:
                try:
                    max_depth = int(input(f"Enter maximum search depth for MCTS (5-50, default: 15)"))
                    if 5 <= max_depth <= 50:
                        break
                    else:
                        print("Please enter a number between 5 and 50.")
                except ValueError:
                    print("Please enter a valid number.")
                    
            # Store MCTS parameters for this player
            player_name = f"Player {i+1}"
            mcts_params[player_name] = {
                "num_sims": num_sims,
                "max_depth": max_depth
            }
        
        # Create player
        player_name = f"Player {i+1}"
        player = Player(
            name=player_name, 
            train_cards={color: 0 for color in Color},
            destinations=[], 
            claimed_connections=[], 
            points=0, 
            turn=1
        )
        players.append(player)
        player_agents[player_name] = agent_type  # Store the agent type
    
    print("\n" + "_" * 200 + "\n")
    # Set up and start the game
    game.init(players)

    game.player_agents = player_agents
    game.agent_options = agent_options

    print("You can type back to go to the previous menu option")
    print("Enjoy Ticket to Ride!")
    
    # Default MCTS parameters (used if not customized)
    default_num_sims = 3000
    default_max_depth = 15
    
    # Main game loop
    while not game.is_end():
        current_player = game.players[game.current_player_idx]
        agent_type = player_agents[current_player.name]
        
        print(f"\n{current_player.name} ({agent_options[agent_type]}) Turn: {current_player.turn}")
        tst = time.time()
        
        # Handle first turn destination selection
        if current_player.turn == 1:
            destinations = game.select_initial_destinations(current_player)
            game.remove_destination_tickets(current_player, destinations)
        
        # Execute agent-specific logic using match-case
        match agent_type:
            case 1:  # Human Player (not implemented)
                player = TicketToRideGame(game)
                best_action = player.play_turn(current_player)
            case 2:  # MCTS AI
                # Get player-specific MCTS parameters or use defaults
                if current_player.name in mcts_params:
                    params = mcts_params[current_player.name]
                    num_sims = params["num_sims"]
                    max_depth = params["max_depth"]
                    print(f"Using custom MCTS parameters: {num_sims} simulations, max depth {max_depth}")
                else:
                    num_sims = default_num_sims
                    max_depth = default_max_depth
                
                mcts_player = MCTS(game)
                best_action = mcts_player.best_action(num_sims, max_depth)
            case 3:  # Destination Heuristic AI
                heuristic_player = DestinationHeuristic(game)
                best_action = heuristic_player.choose_action()
            case 4:  # Longest Route Heuristic AI
                heuristic_player = LongestRouteHeuristic(game)
                best_action = heuristic_player.choose_action()
            case 5:  # Opportunistic Heuristic AI
                heuristic_player = OpportunisticHeuristic(game)
                best_action = heuristic_player.choose_action()
            case 6:  # Best Move Heuristic AI
                heuristic_player = BestMoveHeuristic(game)
                best_action = heuristic_player.choose_action()
            case 7:  # Random AI
                random_agent = RandomHeuristic(game)
                best_action = random_agent.choose_action()
            
        
        # Apply the action and update game state
        game.apply_action_final(best_action)
        if use_gui:
            update_game_state(game, best_action)
            #pygame.event.pump()
        current_player.turn += 1
        tet = time.time()
        print(f"Time taken for turn: {tet-tst} seconds")
        
        game.update_player_turn()
    
    # Calculate final scores
    game.game_result_final(1)

    timeend = time.time()
    elapsed_time = timeend - timestart
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"Time taken: {minutes} minutes and {seconds} seconds")
    if use_gui:
        shutdown()

    game.print_owned_routes()

if __name__ == "__main__":
    main()