from collections import deque
from dataclasses import dataclass
import time
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import random
import copy
from mcts import MCTS
from console import LiveConsole
from graph import TicketToRideVisualizer

class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"
    ORANGE = "orange"
    WHITE = "white"
    PINK = "pink"
    GRAY = "gray"
    WILD = "wild"

# City class to store city name and connections
@dataclass
class City:
    name: str
    connections: Dict[str, List[Tuple[int, Color]]]  # city_name -> [(length, color)]

# Destination class to store destination cities and points
@dataclass
class Destination:
    city1: str
    city2: str
    points: int

# Player class to store player information # TODO - move turn into gamestate
@dataclass
class Player:
    name: str
    remaining_trains: int = 45
    train_cards: Dict[Color, int] = None
    destinations: List[Destination] = None
    claimed_connections: List[Tuple[str, str, Color]] = None
    points: int = 0
    turn: int = 1
    
    def __post_init__(self):
        if self.train_cards is None:
            self.train_cards = {color: 0 for color in Color}
        if self.destinations is None:
            self.destinations = []
        if self.claimed_connections is None:
            self.claimed_connections = []
        
    def getTrainCards(self) -> List[Tuple[Color, int]]:
        return [(color, count) for color, count in self.train_cards.items() if count > 0]

@dataclass
class Route:
    length: int
    color: Color
    claimed_by: str = None

    def claim(self, player: str):
        self.claimed_by = player

    def is_claimed(self) -> bool:
        return self.claimed_by is not None
    
console = LiveConsole()

# Disjointed set for efficient connectivity checking
class UnionFind:
    def __init__(self, cities):
        self.parent = {city: city for city in cities}  # Each city is its own parent
        self.rank = {city: 1 for city in cities}       # Used for union by rank

    def find(self, city):
        if self.parent[city] != city:
            self.parent[city] = self.find(self.parent[city])  # Path compression
        return self.parent[city]

    def union(self, city1, city2):
        root1 = self.find(city1)
        root2 = self.find(city2)

        if root1 != root2:  # If they're not already connected
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1  # Increase rank

    def is_connected(self, city1, city2):
        return self.find(city1) == self.find(city2)

# Handles the game state, including the board, players, current player index, score, train deck, destination deck, and face-up cards
class GameState:
    def __init__(self):
        self.routes = {}
        self.players: List[Player] = []
        self.current_player_idx: int = 0
        self.score: Dict[str, int] = {}
        self.train_deck: List[Color] = []
        self.destination_deck: List[Destination] = []
        self.face_up_cards: List[Color] = []
        self.visualizer = TicketToRideVisualizer(self)
        self.union_find = None
    
    def init(self):
        self.initialise_destination_deck()
        self.initialise_routes()
        self.union_find = UnionFind(self.routes.keys())

    def initialise_destination_deck(self):
        # Add destination tickets to the deck
        destinations = [
            Destination("Los Angeles", "New York", 21),
            Destination("Duluth", "Houston", 8),
            Destination("Sault St. Marie", "Nashville", 8),
            Destination("New York", "Atlanta", 6),
            Destination("Portland", "Nashville", 17),
            Destination("Vancouver", "Montreal", 20),
            Destination("Duluth", "El Paso", 10),
            Destination("Toronto", "Miami", 10),
            Destination("Portland", "Phoenix", 11),
            Destination("Dallas", "New York", 11),
            Destination("Calgary", "Salt Lake City", 7),
            Destination("Calgary", "Phoenix", 13),
            Destination("Los Angeles", "Miami", 20),
            Destination("Winnipeg", "Little Rock", 11),
            Destination("San Francisco", "Atlanta", 17),
            Destination("Kansas City", "Houston", 5),
            Destination("Los Angeles", "Chicago", 16),
            Destination("Denver", "Pittsburgh", 11),
            Destination("Chicago", "Santa Fe", 9),
            Destination("Vancouver", "Santa Fe", 13),
            Destination("Boston", "Miami", 12),
            Destination("Chicago", "New Orleans", 7),
            Destination("Montreal", "Atlanta", 9),
            Destination("Seattle", "New York", 22),
            Destination("Denver", "El Paso", 4),
            Destination("Helena", "Los Angeles", 8),
            Destination("Winnipeg", "Houston", 12),
            Destination("Montreal", "New Orleans", 13),
            Destination("Sault St. Marie", "Oklahoma City", 9),
            Destination("Seattle", "Los Angeles", 9),
        ]
        self.destination_deck = destinations
        random.shuffle(self.destination_deck)
        
    def initialise_routes(self):
        self.routes = {
            "New York": {
                "Boston": [
                    Route(length=2, color=Color.YELLOW),
                    Route(length=2, color=Color.RED)
                ],
                "Pittsburgh": [
                    Route(length=2, color=Color.WHITE),
                    Route(length=2, color=Color.GREEN)
                ],
                "Washington": [
                    Route(length=2, color=Color.ORANGE),
                    Route(length=2, color=Color.BLACK)
                ],
                "Montreal": [
                    Route(length=3, color=Color.BLUE)
                ]
            },
            "Boston": {
                "New York": [
                    Route(length=2, color=Color.YELLOW),
                    Route(length=2, color=Color.RED)
                ],
                "Montreal": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Pittsburgh": {
                "New York": [
                    Route(length=2, color=Color.WHITE),
                    Route(length=2, color=Color.GREEN)
                ],
                "Washington": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Raleigh": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Nashville": [
                    Route(length=4, color=Color.YELLOW)
                ],
                "Saint Louis": [
                    Route(length=5, color=Color.GREEN)
                ],
                "Toronto": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Washington": {
                "New York": [
                    Route(length=2, color=Color.ORANGE),
                    Route(length=2, color=Color.BLACK)
                ],
                "Raleigh": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Pittsburgh": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Montreal": {
                "Boston": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Toronto": [
                    Route(length=3, color=Color.GRAY)
                ],
                "New York": [
                    Route(length=3, color=Color.BLUE)
                ],
                "Sault St. Marie": [
                    Route(length=5, color=Color.BLACK)
                ]
            },
            "Toronto": {
                "Montreal": [
                    Route(length=3, color=Color.GRAY)
                ],
                "Pittsburgh": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Chicago": [
                    Route(length=4, color=Color.WHITE)
                ],
                "Sault St. Marie": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Duluth": [
                    Route(length=6, color=Color.PINK)
                ]
            },
            "Raleigh": {
                "Washington": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Pittsburgh": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Charleston": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Atlanta": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Nashville": [
                    Route(length=3, color=Color.BLACK)
                ]
            },
            "Charleston": {
                "Raleigh": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Atlanta": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Miami": [
                    Route(length=4, color=Color.PINK)
                ]
            },
            "Atlanta": {
                "Raleigh": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Charleston": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Nashville": [
                    Route(length=1, color=Color.GRAY)
                ],
                "Miami": [
                    Route(length=5, color=Color.BLUE)
                ],
                "New Orleans": [
                    Route(length=4, color=Color.YELLOW),
                    Route(length=4, color=Color.ORANGE)
                ]
            },
            "Nashville": {
                "Pittsburgh": [
                    Route(length=4, color=Color.YELLOW)
                ],
                "Atlanta": [
                    Route(length=1, color=Color.GRAY)
                ],
                "Saint Louis": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Raleigh": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Little Rock": [
                    Route(length=3, color=Color.WHITE)
                ]
            },
            "Saint Louis": {
                "Pittsburgh": [
                    Route(length=5, color=Color.GREEN)
                ],
                "Nashville": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Kansas City": [
                    Route(length=2, color=Color.BLUE),
                    Route(length=2, color=Color.PINK)
                ],
                "Chicago": [
                    Route(length=2, color=Color.GREEN),
                    Route(length=2, color=Color.WHITE)
                ],
                "Little Rock": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Chicago": {
                "Saint Louis": [
                    Route(length=2, color=Color.GREEN),
                    Route(length=2, color=Color.WHITE)
                ],
                "Pittsburgh": [
                    Route(length=3, color=Color.ORANGE),
                    Route(length=3, color=Color.BLACK)
                ],
                "Toronto": [
                    Route(length=4, color=Color.WHITE)
                ],
                "Omaha": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Duluth": [
                    Route(length=3, color=Color.RED)
                ]
            },
            "Kansas City": {
                "Saint Louis": [
                    Route(length=2, color=Color.BLUE),
                    Route(length=2, color=Color.PINK)
                ],
                "Oklahoma City": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Denver": [
                    Route(length=4, color=Color.BLACK),
                    Route(length=4, color=Color.ORANGE)
                ],
                "Omaha": [
                    Route(length=1, color=Color.GRAY)
                ]
            },
            "Oklahoma City": {
                "Kansas City": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Dallas": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Little Rock": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Santa Fe": [
                    Route(length=3, color=Color.BLUE)
                ],
                "El Paso": [
                    Route(length=5, color=Color.YELLOW)
                ],
                "Denver": [
                    Route(length=4, color=Color.RED)
                ]
            },
            "Dallas": {
                "Oklahoma City": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Little Rock": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Houston": [
                    Route(length=1, color=Color.GRAY),
                    Route(length=1, color=Color.GRAY)
                ],
                "El Paso": [
                    Route(length=4, color=Color.RED)
                ]
            },
            "Little Rock": {
                "Oklahoma City": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Dallas": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Saint Louis": [
                    Route(length=2, color=Color.GRAY)
                ],
                "New Orleans": [
                    Route(length=3, color=Color.GREEN)
                ],
                "Nashville": [
                    Route(length=3, color=Color.WHITE)
                ]
            },
            "Houston": {
                "Dallas": [
                    Route(length=1, color=Color.GRAY),
                    Route(length=1, color=Color.GRAY)
                ],
                "New Orleans": [
                    Route(length=2, color=Color.GRAY)
                ],
                "El Paso": [
                    Route(length=6, color=Color.GREEN)
                ]
            },
            "New Orleans": {
                "Little Rock": [
                    Route(length=3, color=Color.GREEN)
                ],
                "Houston": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Miami": [
                    Route(length=6, color=Color.RED)
                ],
                "Atlanta": [
                    Route(length=4, color=Color.YELLOW),
                    Route(length=4, color=Color.ORANGE)
                ]
            },
            "Miami": {
                "Atlanta": [
                    Route(length=5, color=Color.BLUE)
                ],
                "New Orleans": [
                    Route(length=6, color=Color.RED)
                ],
                "Charleston": [
                    Route(length=4, color=Color.PINK)
                ]
            },
            "Denver": {
                "Kansas City": [
                    Route(length=4, color=Color.BLACK),
                    Route(length=4, color=Color.ORANGE)
                ],
                "Oklahoma City": [
                    Route(length=4, color=Color.RED)
                ],
                "Santa Fe": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Phoenix": [
                    Route(length=5, color=Color.WHITE)
                ],
                "Salt Lake City": [
                    Route(length=3, color=Color.RED),
                    Route(length=3, color=Color.YELLOW)
                ],
                "Helena": [
                    Route(length=4, color=Color.GREEN)
                ],
                "Omaha": [
                    Route(length=4, color=Color.PINK)
                ]
            },
            "Santa Fe": {
                "Denver": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Oklahoma City": [
                    Route(length=3, color=Color.BLUE)
                ],
                "Phoenix": [
                    Route(length=3, color=Color.GRAY)
                ],
                "El Paso": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Phoenix": {
                "Santa Fe": [
                    Route(length=3, color=Color.GRAY)
                ],
                "Denver": [
                    Route(length=5, color=Color.WHITE)
                ],
                "Los Angeles": [
                    Route(length=3, color=Color.GRAY)
                ],
                "El Paso": [
                    Route(length=3, color=Color.GRAY)
                ]
            },
            "El Paso": {
                "Phoenix": [
                    Route(length=3, color=Color.GRAY)
                ],
                "Santa Fe": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Houston": [
                    Route(length=6, color=Color.GREEN)
                ],
                "Dallas": [
                    Route(length=4, color=Color.RED)
                ],
                "Oklahoma City": [
                    Route(length=5, color=Color.YELLOW)
                ],
                "Los Angeles": [
                    Route(length=6, color=Color.BLACK)
                ]
            },
            "Salt Lake City": {
                "Denver": [
                    Route(length=3, color=Color.RED),
                    Route(length=3, color=Color.YELLOW)
                ],
                "Helena": [
                    Route(length=3, color=Color.PINK)
                ],
                "Las Vegas": [
                    Route(length=3, color=Color.ORANGE)
                ],
                "San Francisco": [
                    Route(length=5, color=Color.ORANGE),
                    Route(length=5, color=Color.WHITE)
                ],
                "Portland": [
                    Route(length=6, color=Color.BLUE)
                ]
            },
            "Helena": {
                "Salt Lake City": [
                    Route(length=3, color=Color.PINK)
                ],
                "Denver": [
                    Route(length=4, color=Color.GREEN)
                ],
                "Omaha": [
                    Route(length=5, color=Color.RED)
                ],
                "Duluth": [
                    Route(length=6, color=Color.ORANGE)
                ],
                "Winnipeg": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Calgary": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Seattle": [
                    Route(length=6, color=Color.YELLOW)
                ]
            },
            "Omaha": {
                "Chicago": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Kansas City": [
                    Route(length=1, color=Color.GRAY),
                    Route(length=1, color=Color.GRAY)
                ],
                "Denver": [
                    Route(length=4, color=Color.PINK)
                ],
                "Helena": [
                    Route(length=5, color=Color.RED)
                ],
                "Duluth": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Duluth": {
                "Chicago": [
                    Route(length=3, color=Color.RED)
                ],
                "Omaha": [
                    Route(length=2, color=Color.GRAY),
                    Route(length=2, color=Color.GRAY)
                ],
                "Helena": [
                    Route(length=6, color=Color.ORANGE)
                ],
                "Winnipeg": [
                    Route(length=4, color=Color.BLACK)
                ],
                "Sault St. Marie": [
                    Route(length=3, color=Color.GRAY)
                ],
                "Toronto": [
                    Route(length=6, color=Color.PINK)
                ]
            },
            "Winnipeg": {
                "Duluth": [
                    Route(length=4, color=Color.BLACK)
                ],
                "Helena": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Sault St. Marie": [
                    Route(length=6, color=Color.GRAY)
                ],
                "Calgary": [
                    Route(length=6, color=Color.WHITE)
                ]
            },
            "Sault St. Marie": {
                "Duluth": [
                    Route(length=3, color=Color.GRAY)
                ],
                "Winnipeg": [
                    Route(length=6, color=Color.GRAY)
                ],
                "Toronto": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Montreal": [
                    Route(length=5, color=Color.BLACK)
                ]
            },
            "Las Vegas": {
                "Salt Lake City": [
                    Route(length=3, color=Color.ORANGE)
                ],
                "Los Angeles": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Los Angeles": {
                "Las Vegas": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Phoenix": [
                    Route(length=3, color=Color.GRAY)
                ],
                "El Paso": [
                    Route(length=6, color=Color.BLACK)
                ],
                "San Francisco": [
                    Route(length=3, color=Color.PINK),
                    Route(length=3, color=Color.YELLOW)
                ]
            },
            "San Francisco": {
                "Salt Lake City": [
                    Route(length=5, color=Color.ORANGE),
                    Route(length=5, color=Color.WHITE)
                ],
                "Los Angeles": [
                    Route(length=3, color=Color.PINK),
                    Route(length=3, color=Color.YELLOW)
                ],
                "Portland": [
                    Route(length=5, color=Color.GREEN),
                    Route(length=5, color=Color.PINK)
                ]
            },
            "Portland": {
                "San Francisco": [
                    Route(length=5, color=Color.GREEN),
                    Route(length=5, color=Color.PINK)
                ],
                "Seattle": [
                    Route(length=1, color=Color.GRAY),
                    Route(length=1, color=Color.GRAY)
                ],
                "Salt Lake City": [
                    Route(length=6, color=Color.BLUE)
                ]
            },
            "Seattle": {
                "Portland": [
                    Route(length=1, color=Color.GRAY),
                    Route(length=1, color=Color.GRAY)
                ],
                "Helena": [
                    Route(length=6, color=Color.YELLOW)
                ],
                "Calgary": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Vancouver": [
                    Route(length=1, color=Color.GRAY),
                    Route(length=1, color=Color.GRAY)
                ]
            },
            "Vancouver": {
                "Seattle": [
                    Route(length=1, color=Color.GRAY),
                    Route(length=1, color=Color.GRAY)
                ],
                "Calgary": [
                    Route(length=3, color=Color.GRAY)
                ]
            },
            "Calgary": {
                "Vancouver": [
                    Route(length=3, color=Color.GRAY)
                ],
                "Seattle": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Helena": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Winnipeg": [
                    Route(length=6, color=Color.WHITE)
                ]
            }
        }

    def get_routes_from_city(self, city: str) -> Dict[str, List[Route]]:
        """Get all routes from a specific city."""
        return self.routes.get(city, {})

    def get_routes_between_cities(self, city1: str, city2: str) -> List[Route]:
        """Get both routes between two specific cities."""
        routes = []
        # Check direct routes
        if city2 in self.routes.get(city1, {}):
            routes.extend(self.routes[city1][city2])
        # Check reverse routes
        if city1 in self.routes.get(city2, {}):
            routes.extend(self.routes[city2][city1])
        return routes

    def get_unclaimed_routes(self) -> List[tuple[str, str, Route]]:
        """Get all unclaimed routes in the game."""
        unclaimed = []
        for city1, connections in self.routes.items():
            for city2, routes in connections.items():
                for route in routes:
                    if route.claimed_by is None:
                        unclaimed.append((city1, city2, route))
        return unclaimed

    def claim_route_helper(self, color: Color, player: str, routes) -> bool:
        for route in routes:
            claimed = route.is_claimed()
            if (color == Color.WILD or route.color == color or route.color == Color.GRAY) and not (claimed):
                route.claim(player)

                return True
            return False

    def claim_route(self, city1: str, city2: str, color: Color, player: str) -> bool:
        """Attempt to claim a route between two cities."""
        routes = self.get_routes_between_cities(city1, city2)
        if len(routes) == 4:
            direction1 = [routes[0],routes[2]]
            d1 = self.claim_route_helper(color, player, direction1)
            direction2 = [routes[1], routes[3]]
            d2 = self.claim_route_helper(color, player, direction2)
            return d1 or d2
        else: # Only one direction so can claim both
            if self.claim_route_helper(color, player, routes): return True
              
        #print(f"Failed to claim route between {city1} and {city2} with {color}")
        #print (f"Color: {color} is not valid for route between {city1} and {city2}")
        return False

    def get_route_length(self, city1: str, city2: str, color: Color) -> Optional[int]:
        """Get the length of a specific route."""
        routes = self.get_routes_between_cities(city1, city2)
        for route in routes:
            return route.length
        return None
    
    def setup_train_deck(self):
        for color in Color:
            if color != Color.WILD and color != Color.GRAY:
                self.train_deck.extend([color] * 12)
            
        self.train_deck.extend([Color.WILD] * 14)
        random.shuffle(self.train_deck)

    def draw_train_face(self, i: int, card: Color, player: str):
        """Draw a face-up card."""
        self.face_up_cards.pop(i)
        if self.train_deck.__len__() == 0:
            self.setup_train_deck()
        self.face_up_cards.append(self.train_deck.pop())
        self.players[self.current_player_idx].train_cards[card] += 1
    
    def draw_train_deck(self, player: str):
        """Draw a card from the train deck."""
        if self.train_deck.__len__() == 0:
            self.setup_train_deck()
        card = self.train_deck.pop()
        self.players[self.current_player_idx].train_cards[card] += 1

    def check_all_destinations(self, player) -> List[Tuple[Destination, bool]]:
        # Check if the player has completed all destination tickets using union-find
        destination_results = []
        for destination in player.destinations:
            city1, city2 = destination.city1, destination.city2
            if self.union_find.is_connected(city1, city2):
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
    
    # MCTS methods
    def copy(self):
        # Create a deep copy of the game state
        new_state = GameState()
        new_state = copy.deepcopy(self)
        return new_state
    
    def apply_action(self, action):
        action_type = action[0]
        if action_type == "draw_two_train_cards":
            idx1, card1, idx2, card2, player_name = action[1:]
            if card1 != "deck":
                self.draw_train_face(idx1, card1, player_name)
            else:
                self.draw_train_deck(player_name)
            if card2 != "deck":
                self.draw_train_face(idx2, card2, player_name)
            else:
                self.draw_train_deck(player_name)
        elif action_type == "claim_route":
            city1, city2, color, player_name = action[1:]
            if self.claim_route(city1, city2, color, player_name):
                route_length = self.get_route_length(city1, city2, color)
                if color == Color.WILD:
                    self.players[self.current_player_idx].train_cards[Color.WILD] -= route_length
                else:
                    self.players[self.current_player_idx].train_cards[color] -= route_length
                self.players[self.current_player_idx].claimed_connections.append((city1, city2, color))
                self.players[self.current_player_idx].points += self.calc_route_points(route_length)
                self.union_find.union(city1, city2)
                if route_length >= 4:
                    #print("long route attempted at length", route_length)
                    pass
                self.players[self.current_player_idx].remaining_trains -= route_length
            else:
                pass

    def apply_action_final(self, action):
        self.apply_action(action)
        action_type = action[0]
        if action_type == "draw_two_train_cards":
            idx1, card1, idx2, card2, player_name = action[1:]
            print(f"{player_name} has drawn two train cards: {card1}, {card2}")
        elif action_type == "claim_route":
            city1, city2, color, player_name = action[1:]
            print(f"{player_name} has claimed a route between {city1} and {city2} with {color}")
            
    
    def is_end(self):
        # Check if the game state is terminal
        if (self.players[self.current_player_idx].remaining_trains <= 2):
            return True
        return False
    
    def get_legal_actions(self):
        # TODO Need to support adding destination tickets
        legal_actions = []
        current_player = self.players[self.current_player_idx]
        unclaimed_routes = self.get_unclaimed_routes()
        for city1, city2, route in unclaimed_routes:
            if route.color == Color.GRAY:
                for color in Color:
                    if current_player.train_cards[color] >= route.length:
                        legal_actions.append(("claim_route",city1, city2, color, current_player.name))
            if current_player.train_cards[route.color] >= route.length:
                legal_actions.append(("claim_route",city1, city2, route.color, current_player.name))
            if current_player.train_cards[Color.WILD] >= route.length:
                legal_actions.append(("claim_route",city1, city2, Color.WILD, current_player.name))
        
        num_cards = sum(current_player.train_cards.values())
        if num_cards <= 12:
        # Draw two train cards. Enumerate all possible combinations of face-up cards and deck cards
            for i, card1 in enumerate(self.face_up_cards):
                for j, card2 in enumerate(self.face_up_cards):
                    if i != j:
                        legal_actions.append(("draw_two_train_cards", i, card1, j, card2, current_player.name))
                legal_actions.append(("draw_two_train_cards", i, card1, "deck", "deck", current_player.name))
            legal_actions.append(("draw_two_train_cards", "deck", "deck", "deck", "deck", current_player.name))
        else:
            pass
    
        return legal_actions
    
    def get_missing_routes(self):
        # Estimates how many more connections the player requires to complete each of their destination tickets
        # TODO - Incomplete
        missing_routes = []
        player = self.players[self.current_player_idx]
        for destination in player.destinations:
            return False

    
    def game_result(self,game_num):
        #print(f"Game {game_num}:")
        player = self.players[self.current_player_idx]
        destination_results = self.check_all_destinations(player)

        for destination, is_complete in destination_results:
            if is_complete:
                player.points += destination.points
                #print(f"Destination between {destination.city1} and {destination.city2} has been completed. Total score: {player.points}")
            else:
                player.points -= destination.points
                #print(f"Destination between {destination.city1} and {destination.city2} has not been completed. Total score: {player.points}")
        console.print_results(game_num,player)
        return player.points
    
    def game_result_final(self,game_num):
        console.stop()
        print(f"Game {game_num}:")
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
            print("Final score: ", player.points)
        

# General game class which stores players, current player index, train deck, destination deck, face-up cards
# TODO - Implement final scoring
class TicketToRide:
    def __init__(self):
        self.game_state = GameState()
        self.god_mode = False
        
    def setup_game(self, players: List[Player]):
        self.game_state.players = players
        self.game_state.init()
        self.initialise_train_deck()
        
        # Deal initial cards to each player
        for player in self.game_state.players:
            self.deal_initial_cards(player)
            
    def initialise_train_deck(self):
        # Add 12 of each color (excluding wild) and 14 wild cards
        self.game_state.setup_train_deck()
        
        # Draw initial face-up cards
        self.game_state.face_up_cards = [self.game_state.train_deck.pop() for _ in range(5)]
    
    def deal_initial_cards(self, player: Player):
        # Deal 4 train cards to each player
        for _ in range(4):
            card = self.game_state.train_deck.pop()
            player.train_cards[card] += 1
        # Deal 3 destination cards, player must keep at least 2
        destinations = [self.game_state.destination_deck.pop() for _ in range(3)]
        # TODO - player must keep at least 2 & can discard 1
        player.destinations.extend(destinations[:3])
                
        print(f"{player.name} has been dealt the following destinations: {', '.join(self.formatted_destinations(player))}")
        print(f"{player.name} has been dealt the following train cards: {', '.join(self.formatted_trains(player))}")

    def formatted_trains(self, player: Player) -> List[str]: 
        return [f"{color.name.capitalize()}: {count}" for color, count in player.train_cards.items() if count > 0]

    def formatted_destinations(self, player: Player) -> List[str]: 
        return [f"{destination.city1} to {destination.city2} ({destination.points})" for destination in player.destinations]

    def print_board(self):
        self.visualizer = TicketToRideVisualizer(self.game_state)
        self.visualizer.visualize_game_map()
        print("=== Ticket to Ride Board ===")
        for city1, connections in sorted(self.game_state.routes.items()):
            print(f"\n{city1}:")
            for city2, routes in sorted(connections.items()):
                for route in routes:
                    status = "Claimed by " + route.claimed_by if route.claimed_by else "Available"
                    print(f"  -> {city2} ({route.color} * {route.length}): {status}")
        print("===========================")

    def print_available_routes(self, player: Player):
        unclaimed_routes = self.game_state.get_unclaimed_routes()
        available_routes = []
        
        for city1, city2, route in unclaimed_routes:
            # Check if player has enough cards to claim the route
            # TODO allow combinations of wild and other colors
            if route.color == Color.GRAY:
                for color in Color:
                    if player.train_cards[color] >= route.length:
                        if available_routes.__contains__((city1, city2, route, color)): #if the route is already in the list, skip (avoids duplicates in case of multiple paths /wild cards)
                            continue
                        else:
                            available_routes.append((city1, city2, route, color))
            if player.train_cards[Color.WILD] >= route.length:
                if available_routes.__contains__((city1, city2, route, Color.WILD)):
                    continue
                else:
                    available_routes.append((city1, city2, route, Color.WILD))
            if player.train_cards[route.color] >= route.length:
                if available_routes.__contains__((city1, city2, route, route.color)):
                    continue
                else:
                    available_routes.append((city1, city2, route, route.color))
                
        
        if available_routes:
            print("\nRoutes you can complete:")
            for city1, city2, route, color in available_routes:
                print(f"{city1} -> {city2} ({color} * {route.length})")
        else:
            print("\nNo routes available to claim with your current cards.")

    def destination_completion_check(self, player: Player):
        results = self.game_state.check_all_destinations(player)
        
        completed_count = 0
        for destination, is_completed in results:
            status = "completed" if is_completed else "not completed"
            print(f"Destination {destination.city1} to {destination.city2} is {status}")
            if is_completed:
                completed_count += 1
                
        print(f"\nTotal completed destinations: {completed_count}/{len(results)}")
        
    def play_turn(self, player: Player):
        print("\n" + "_" * 200)
        print(f"Turn {player.turn}" + "\n")
        print(f"\n{player.name}'s turn")
        print(f"{player.name}'s train cards: {', '.join(self.formatted_trains(player))}")
        print(f"{player.name}'s destination tickets: {', '.join(self.formatted_destinations(player))}")
        print(f"Face-up cards: {', '.join([card.name for card in self.game_state.face_up_cards])}" + "\n")

        choice = input("<1: Draw Train cards, 2: Claim a route, 3: Draw destination tickets, 4: Print board, 5: Print routes you can complete, 6: Print score, exit: Exit game>\n")

        if choice == "1":
            self.draw_train_cards(player)
        elif choice == "2":
            self.handle_claim_route(player)
            if self.god_mode:
                self.play_turn(player)
        elif choice == "3":
            self.draw_destination_tickets(player)
        elif choice == "4":
            self.print_board()
            self.play_turn(player)
        elif choice == "5":
            self.print_available_routes(player)
            self.play_turn(player)
        elif choice == "6":
            print(f"{player.name}'s score: {player.points}")
            self.play_turn(player)
        elif choice == "7": #temporary testing
            self.destination_completion_check(player)
            self.play_turn(player)
        elif choice == "godmode":
            # testing cheats
            self.god_mode = True
            self.game_state.players[0].train_cards[Color.WILD] += 100
            self.game_state.players[1].train_cards[Color.WILD] += 100
            self.play_turn(player)
        elif choice == "exit":
            exit()
        else:
            print("Invalid choice, please try again.")
            self.play_turn(player)
        

    def handle_claim_route(self, player: Player):
        print("Choose a route to claim:")
        city1 = input("Enter the first city: ")
        if city1 == "back":
            self.play_turn(player)
            return
            
        city2 = input("Enter the second city: ")
        if city2 == "back":
            self.play_turn(player)
            return

        routes = self.game_state.get_routes_between_cities(city1, city2)
        if not routes:
            print("No route exists between these cities.")
            self.play_turn(player)
            return

        available_colors = []
        
        route = routes[0]
        if route.claimed_by is None:
            # TODO allow player to use a combination of wild and other colors
            if route.color == Color.GRAY:
                for color in Color:
                    if player.train_cards[color] >= route.length:
                        available_colors.append(color)
            if player.train_cards[route.color] >= route.length:
                available_colors.append(route.color)
            

            if player.train_cards[Color.WILD] >= route.length:
                available_colors.append(Color.WILD)

        if available_colors == []:
            print("You don't have enough cards to claim any routes between these cities.")
            self.play_turn(player)
            return 
        
        if len(available_colors) > 1:
            color = input(f"Choose a color to claim the route ({', '.join([colors.name for colors in available_colors])}): ")
            if color == "back":
                self.play_turn(player)
                return
            for colors in available_colors:
                if color == colors.name:
                    color = colors
            if color not in available_colors:
                print("Invalid color choice, please try again.")
                # TODO probably make a color choice function
                self.handle_claim_route(player)
                return
        else:
            color = available_colors[0]
        if self.game_state.claim_route(city1, city2, color, player.name):
            # Remove cards from player's hand
            route_length = self.game_state.get_route_length(city1, city2, color)
            if color == Color.WILD:
                player.train_cards[Color.WILD] -= route_length
            else:
                player.train_cards[color] -= route_length
            player.claimed_connections.append((city1, city2, color))
            player.points += self.game_state.calc_route_points(route_length)
            print(f"{player.name} has claimed the route between {city1} and {city2} with {color}")
            self.game_state.union_find.union(city1, city2)
        else:
            print("Failed to claim route.")
            self.play_turn(player)

    def draw_train_cards(self, player: Player):
        drawn = 0
        while drawn < 2:
            # TODO only allow play to pick up 1 card if they take a wild card, disallow from taking a wild as second card
            choice = input("Would you like to draw from the face-up cards? (y/n)")
            if choice == "y":
                print("Choose a card to draw:")
                for i, card in enumerate(self.game_state.face_up_cards):
                    print(f"{i+1}: {card.name}")
                card_choice = int(input("Enter the card number: ")) - 1
                card = self.game_state.face_up_cards.pop(card_choice)
                player.train_cards[card] += 1
                print(f"{player.name} has drawn {card.name}")
                self.game_state.face_up_cards.append(self.game_state.train_deck.pop())
                print(f"New face-up cards: {', '.join([card.name for card in self.game_state.face_up_cards])}")
                drawn += 1
            elif choice == "n":
                card = self.game_state.train_deck.pop()
                player.train_cards[card] += 1
                print(f"{player.name} has drawn {card.name}")
                drawn += 1
            elif choice == "back":
                self.play_turn(player)
                return
            else:
                print("Invalid choice, please try again.")

        print(f"{player.name}'s train cards: {', '.join(self.formatted_trains(player))}")

    def draw_destination_tickets(self, player: Player):
        destinations = [self.game_state.destination_deck.pop() for _ in range(3)]
        print("You have drawn the following destinations:")
        for i, dest in enumerate(destinations, 1):
            print(f"{i}: {dest.city1} to {dest.city2} ({dest.points} points)")
        
        to_keep = destinations.copy()
        while len(to_keep) > 1:  # Must keep at least one
            choice = input("Would you like to remove any destinations? (y/n)")
            if choice == "y":
                print("Which destination would you like to remove?")
                for i, dest in enumerate(to_keep, 1):
                    print(f"{i}: {dest.city1} to {dest.city2} ({dest.points} points)")
                try:
                    remove_idx = int(input("Enter the destination number to remove: ")) - 1
                    removed = to_keep.pop(remove_idx)
                    print(f"Removed: {removed.city1} to {removed.city2}")
                except (ValueError, IndexError):
                    print("Invalid choice, please try again.")
            elif choice == "n":
                break
            elif choice == "back":
                self.play_turn(player)
                return

        player.destinations.extend(to_keep)
        print(f"{player.name}'s current destinations: {', '.join(self.formatted_destinations(player))}")

def main():
    game = TicketToRide()
    # Create players
    players = [
        Player(name="Player 1", train_cards={color: 0 for color in Color}, 
            destinations=[], claimed_connections=[], points=0, turn=1),
        Player(name="Player 2", train_cards={color: 0 for color in Color}, 
            destinations=[], claimed_connections=[], points=0, turn=1)
    ]
    print("\n" + "_" * 200 + "\n")
    # Set up and start the game
    game.setup_game(players)

    print("You can type back to go to the previous menu option")
    print("Enjoy Ticket to Ride!")

    # Main game loop
    game_end = False
    while not game_end:
        # Instantiate MCTS for Player 1
        mcts_player = MCTS(game.game_state)
        mcts_player2 = MCTS(game.game_state)
        current_player = game.game_state.players[game.game_state.current_player_idx]
        if current_player.name == "Player 1":
            # Use MCTS to determine the best action for Player 1
            best_action = mcts_player.best_action(simulations_number=400)
            game.game_state.apply_action_final(best_action)
            console.stop()
        
        elif current_player.name == "Player 2":
            best_action = mcts_player2.best_action(simulations_number=400)
            game.game_state.apply_action_final(best_action)
            console.stop()
        
        """
        else:
            # Let Player 2 play their turn manually
            game.play_turn(current_player)
        """
        
        for player in game.game_state.players:
            player.turn += 1
        print(f"\nTurn: {player.turn}")
        console.start_live()
        
        game.game_state.current_player_idx = (game.game_state.current_player_idx + 1) % len(game.game_state.players)
        
        # Check end game condition
        if current_player.remaining_trains <= 2:
            game_end = True
    
    # Calculate final scores
    game.game_state.game_result_final(1)
    game.game_state.visualizer = TicketToRideVisualizer(game.game_state)
    game.game_state.visualizer.visualize_game_map()

    print("End of game")
if __name__ == "__main__":
    main()