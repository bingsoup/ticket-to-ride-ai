from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import random

class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"
    ORANGE = "orange"
    WHITE = "white"
    PINK = "pink"
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

# Player class to store player information TODO - Restructure to store some of this into a gamestate dataclass that stores board state
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

# Handles the game state, including the board, players, current player index, score, train deck, destination deck, and face-up cards
class GameState:
    def __init__(self):
        # TODO - put this into a function
        self.routes = {}
        self.players: List[Player] = []
        self.current_player_idx: int = 0
        self.score: Dict[str, int] = {}
        self.train_deck: List[Color] = []
        self.destination_deck: List[Destination] = []
        self.face_up_cards: List[Color] = []

    def initialise_destination_deck(self):
        # Add destination tickets to the deck
        destinations = [
            Destination("Los Angeles", "New York City", 21),
            Destination("Duluth", "Houston", 8),
            Destination("Sault St. Marie", "Nashville", 8),
            Destination("New York City", "Atlanta", 6),
            Destination("Portland", "Nashville", 17),
            Destination("Vancouver", "Montreal", 20),
            Destination("Duluth", "El Paso", 10),
            Destination("Toronto", "Miami", 10),
            Destination("Portland", "Phoenix", 11),
            Destination("Dallas", "New York City", 11),
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
            Destination("Seattle", "New York City", 22),
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
                ]
            },
            "Boston": {
                "New York": [
                    Route(length=2, color=Color.YELLOW),
                    Route(length=2, color=Color.RED)
                ],
                "Montreal": [
                    Route(length=2, color=Color.BLUE)
                ]
            },
            "Pittsburgh": {
                "New York": [
                    Route(length=2, color=Color.WHITE),
                    Route(length=2, color=Color.GREEN)
                ],
                "Washington": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Raleigh": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Nashville": [
                    Route(length=3, color=Color.YELLOW)
                ],
                "Saint Louis": [
                    Route(length=5, color=Color.GREEN)
                ]
            },
            "Washington": {
                "New York": [
                    Route(length=2, color=Color.ORANGE),
                    Route(length=2, color=Color.BLACK)
                ],
                "Raleigh": [
                    Route(length=2, color=Color.GREEN)
                ]
            },
            "Montreal": {
                "Boston": [
                    Route(length=2, color=Color.BLUE)
                ],
                "Toronto": [
                    Route(length=3, color=Color.BLACK)
                ]
            },
            "Toronto": {
                "Montreal": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Pittsburgh": [
                    Route(length=2, color=Color.WHITE)
                ]
            },
            "Raleigh": {
                "Washington": [
                    Route(length=2, color=Color.GREEN)
                ],
                "Pittsburgh": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Charleston": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Atlanta": [
                    Route(length=2, color=Color.YELLOW)
                ]
            },
            "Charleston": {
                "Raleigh": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Atlanta": [
                    Route(length=2, color=Color.BLUE)
                ]
            },
            "Atlanta": {
                "Raleigh": [
                    Route(length=2, color=Color.YELLOW)
                ],
                "Charleston": [
                    Route(length=2, color=Color.BLUE)
                ],
                "Nashville": [
                    Route(length=1, color=Color.ORANGE)
                ],
                "Miami": [
                    Route(length=5, color=Color.BLUE)
                ]
            },
            "Nashville": {
                "Pittsburgh": [
                    Route(length=3, color=Color.YELLOW)
                ],
                "Atlanta": [
                    Route(length=1, color=Color.ORANGE)
                ],
                "Saint Louis": [
                    Route(length=2, color=Color.BLACK)
                ]
            },
            "Saint Louis": {
                "Pittsburgh": [
                    Route(length=5, color=Color.GREEN)
                ],
                "Nashville": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Kansas City": [
                    Route(length=2, color=Color.BLUE),
                    Route(length=2, color=Color.PINK)
                ],
                "Chicago": [
                    Route(length=2, color=Color.GREEN)
                ]
            },
            "Chicago": {
                "Saint Louis": [
                    Route(length=2, color=Color.GREEN)
                ],
                "Pittsburgh": [
                    Route(length=3, color=Color.ORANGE)
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
                    Route(length=2, color=Color.YELLOW),
                    Route(length=2, color=Color.RED)
                ],
                "Denver": [
                    Route(length=4, color=Color.BLACK),
                    Route(length=4, color=Color.ORANGE)
                ],
                "Omaha": [
                    Route(length=1, color=Color.BLACK)
                ]
            },
            "Oklahoma City": {
                "Kansas City": [
                    Route(length=2, color=Color.YELLOW),
                    Route(length=2, color=Color.RED)
                ],
                "Dallas": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Little Rock": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Santa Fe": [
                    Route(length=3, color=Color.BLUE)
                ]
            },
            "Dallas": {
                "Oklahoma City": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Little Rock": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Houston": [
                    Route(length=1, color=Color.BLACK)
                ]
            },
            "Little Rock": {
                "Oklahoma City": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Dallas": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Saint Louis": [
                    Route(length=2, color=Color.BLACK)
                ],
                "New Orleans": [
                    Route(length=3, color=Color.GREEN)
                ]
            },
            "Houston": {
                "Dallas": [
                    Route(length=1, color=Color.BLACK)
                ],
                "New Orleans": [
                    Route(length=2, color=Color.ORANGE)
                ]
            },
            "New Orleans": {
                "Little Rock": [
                    Route(length=3, color=Color.GREEN)
                ],
                "Houston": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Miami": [
                    Route(length=6, color=Color.RED)
                ],
                "Atlanta": [
                    Route(length=4, color=Color.YELLOW)
                ]
            },
            "Miami": {
                "Atlanta": [
                    Route(length=5, color=Color.BLUE)
                ],
                "New Orleans": [
                    Route(length=6, color=Color.RED)
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
                    Route(length=2, color=Color.BLACK)
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
                ]
            },
            "Santa Fe": {
                "Denver": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Oklahoma City": [
                    Route(length=3, color=Color.BLUE)
                ],
                "Phoenix": [
                    Route(length=3, color=Color.BLACK)
                ],
                "El Paso": [
                    Route(length=2, color=Color.BLACK)
                ]
            },
            "Phoenix": {
                "Santa Fe": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Denver": [
                    Route(length=5, color=Color.WHITE)
                ],
                "Los Angeles": [
                    Route(length=6, color=Color.BLACK)
                ],
                "El Paso": [
                    Route(length=3, color=Color.BLACK)
                ]
            },
            "El Paso": {
                "Phoenix": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Santa Fe": [
                    Route(length=2, color=Color.BLACK)
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
                "Seattle": [
                    Route(length=6, color=Color.YELLOW)
                ]
            },
            "Omaha": {
                "Chicago": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Kansas City": [
                    Route(length=1, color=Color.BLACK)
                ],
                "Denver": [
                    Route(length=4, color=Color.PINK)
                ],
                "Helena": [
                    Route(length=5, color=Color.RED)
                ],
                "Duluth": [
                    Route(length=2, color=Color.BLACK)
                ]
            },
            "Duluth": {
                "Chicago": [
                    Route(length=3, color=Color.RED)
                ],
                "Omaha": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Helena": [
                    Route(length=6, color=Color.ORANGE)
                ],
                "Winnipeg": [
                    Route(length=4, color=Color.BLACK)
                ],
                "Sault St. Marie": [
                    Route(length=3, color=Color.BLACK)
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
                    Route(length=6, color=Color.BLACK)
                ]
            },
            "Sault St. Marie": {
                "Duluth": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Winnipeg": [
                    Route(length=6, color=Color.BLACK)
                ],
                "Toronto": [
                    Route(length=2, color=Color.BLACK)
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
                    Route(length=2, color=Color.BLACK)
                ]
            },
            "Los Angeles": {
                "Las Vegas": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Phoenix": [
                    Route(length=6, color=Color.BLACK)
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
                    Route(length=5, color=Color.GREEN)
                ]
            },
            "Portland": {
                "San Francisco": [
                    Route(length=5, color=Color.GREEN)
                ],
                "Seattle": [
                    Route(length=1, color=Color.BLACK)
                ],
                "Salt Lake City": [
                    Route(length=6, color=Color.BLUE)
                ]
            },
            "Seattle": {
                "Portland": [
                    Route(length=1, color=Color.BLACK)
                ],
                "Helena": [
                    Route(length=6, color=Color.YELLOW)
                ],
                "Calgary": [
                    Route(length=4, color=Color.BLACK)
                ],
                "Vancouver": [
                    Route(length=1, color=Color.BLACK)
                ]
            },
            "Vancouver": {
                "Seattle": [
                    Route(length=1, color=Color.BLACK)
                ],
                "Calgary": [
                    Route(length=3, color=Color.BLACK)
                ]
            },
            "Calgary": {
                "Vancouver": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Seattle": [
                    Route(length=4, color=Color.BLACK)
                ],
                "Helena": [
                    Route(length=4, color=Color.BLACK)
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

    def claim_route(self, city1: str, city2: str, color: Color, player: str) -> bool:
        """Attempt to claim a route between two cities."""
        routes: List[Route] = []
        routes.append(self.get_routes_between_cities(city1, city2))
        routes.append(self.get_routes_between_cities(city2, city1))
        for route in routes:
            if color == Color.WILD and not route[0].is_claimed():
                route[0].claim(player)
                route[1].claim(player)
                return True
            if route[0].color == color and not route[0].is_claimed():
                route[0].claim(player)
                route[1].claim(player)
                return True
        return False

    def get_route_length(self, city1: str, city2: str, color: Color) -> Optional[int]:
        """Get the length of a specific route."""
        routes = self.get_routes_between_cities(city1, city2)
        for route in routes:
            if route.color == color:
                return route.length
        return None

# General game class which stores players, current player index, train deck, destination deck, face-up cards, and board
class TicketToRide:
    def __init__(self):
        self.game_state = GameState()
        
    def setup_game(self, players: List[Player]):
        self.game_state.players = players
        self.initialise_train_deck()
        self.game_state.initialise_routes()
        self.game_state.initialise_destination_deck()
        
        # Deal initial cards to each player
        for player in self.game_state.players:
            self.deal_initial_cards(player)
            
    def initialise_train_deck(self):
        # Add 12 of each color (excluding wild) and 14 wild cards
        for color in Color:
            if color != Color.WILD:
                self.game_state.train_deck.extend([color] * 12)
        self.game_state.train_deck.extend([Color.WILD] * 14)
        random.shuffle(self.game_state.train_deck)
        
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
            if player.train_cards[Color.WILD] >= route.length:
                # TODO allow combinations of wild and other colors
                available_routes.append((city1, city2, route))
            if player.train_cards[route.color] >= route.length:
                available_routes.append((city1, city2, route))
        
        if available_routes:
            print("\nRoutes you can complete:")
            for city1, city2, route in available_routes:
                print(f"{city1} -> {city2} ({route.color} * {route.length})")
        else:
            print("\nNo routes available to claim with your current cards.")

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
        elif choice == "exit":
            exit()
        else:
            print("Invalid choice, please try again.")
            self.play_turn(player)
        
        for player in self.game_state.players:
            player.turn += 1

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
            route_length = next(route.length for route in routes if route.color == color)
            player.train_cards[color] -= route_length
            player.claimed_connections.append((city1, city2, color))
            player.points += route_length
            print(f"{player.name} has claimed the route between {city1} and {city2} with {color}")
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
            destinations=[], claimed_connections=[], points=0, turn=0),
        Player(name="Player 2", train_cards={color: 0 for color in Color}, 
            destinations=[], claimed_connections=[], points=0, turn=0)
    ]
    print("\n" + "_" * 200 + "\n")
    # Set up and start the game
    game.setup_game(players)
    print("You can type back to go to the previous menu option")
    print("Enjoy Ticket to Ride!")
    
    # Main game loop
    game_end = False
    while not game_end:
        current_player = game.game_state.players[game.game_state.current_player_idx]
        
        game.play_turn(current_player)

        game.game_state.current_player_idx = (game.game_state.current_player_idx + 1) % len(game.game_state.players)
        
        # Check end game condition
        if current_player.remaining_trains <= 2:
            game_end = True
    
    # Calculate final scores
    game.calculate_final_scores()

if __name__ == "__main__":
    main()