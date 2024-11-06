from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
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

# TODO - Add a state dataclass to store player independent game state (score, board state, decks, etc.)

# General game class which stores players, current player index, train deck, destination deck, face-up cards, and board
# TODO - Restructure such that this class only stores methods for game logic and state is stored in a separate dataclass
class TicketToRide:
    def __init__(self):
        self.players: List[Player] = []
        self.current_player_idx: int = 0
        self.train_deck: List[Color] = []
        self.destination_deck: List[Destination] = []
        self.face_up_cards: List[Color] = []
        self.board: Dict[str, City] = self.initialize_board()
        
    def initialize_board(self) -> Dict[str, City]:
    # Complete board initialization with all cities and routes between them
        board = {
            "New York": City("New York", {
                "Boston": [(2, Color.YELLOW), (2, Color.RED)],
                "Pittsburgh": [(2, Color.WHITE), (2, Color.GREEN)],
                "Washington": [(2, Color.ORANGE), (2, Color.BLACK)]
            }),
            "Boston": City("Boston", {
                "New York": [(2, Color.YELLOW), (2, Color.RED)],
                "Montreal": [(2, Color.BLUE)]
            }),
            "Pittsburgh": City("Pittsburgh", {
                "New York": [(2, Color.WHITE), (2, Color.GREEN)],
                "Washington": [(2, Color.ORANGE)],
                "Raleigh": [(2, Color.BLACK)],
                "Nashville": [(3, Color.YELLOW)],
                "Saint Louis": [(5, Color.GREEN)]
            }),
            "Washington": City("Washington", {
                "New York": [(2, Color.ORANGE), (2, Color.BLACK)],
                "Raleigh": [(2, Color.GREEN)]
            }),
            "Montreal": City("Montreal", {
                "Boston": [(2, Color.BLUE)],
                "Toronto": [(3, Color.BLACK)]
            }),
            "Toronto": City("Toronto", {
                "Montreal": [(3, Color.BLACK)],
                "Pittsburgh": [(2, Color.WHITE)]
            }),
            "Raleigh": City("Raleigh", {
                "Washington": [(2, Color.GREEN)],
                "Pittsburgh": [(2, Color.BLACK)],
                "Charleston": [(2, Color.ORANGE)],
                "Atlanta": [(2, Color.YELLOW)]
            }),
            "Charleston": City("Charleston", {
                "Raleigh": [(2, Color.ORANGE)],
                "Atlanta": [(2, Color.BLUE)]
            }),
            "Atlanta": City("Atlanta", {
                "Raleigh": [(2, Color.YELLOW)],
                "Charleston": [(2, Color.BLUE)],
                "Nashville": [(1, Color.ORANGE)],
                "Miami": [(5, Color.BLUE)]
            }),
            "Nashville": City("Nashville", {
                "Pittsburgh": [(3, Color.YELLOW)],
                "Atlanta": [(1, Color.ORANGE)],
                "Saint Louis": [(2, Color.BLACK)]
            }),
            "Saint Louis": City("Saint Louis", {
                "Pittsburgh": [(5, Color.GREEN)],
                "Nashville": [(2, Color.BLACK)],
                "Kansas City": [(2, Color.BLUE), (2, Color.PINK)],
                "Chicago": [(2, Color.GREEN)]
            }),
            "Chicago": City("Chicago", {
                "Saint Louis": [(2, Color.GREEN)],
                "Pittsburgh": [(3, Color.ORANGE)],
                "Toronto": [(4, Color.WHITE)],
                "Omaha": [(4, Color.BLUE)],
                "Duluth": [(3, Color.RED)]
            }),
            "Kansas City": City("Kansas City", {
                "Saint Louis": [(2, Color.BLUE), (2, Color.PINK)],
                "Oklahoma City": [(2, Color.YELLOW), (2, Color.RED)],
                "Denver": [(4, Color.BLACK), (4, Color.ORANGE)],
                "Omaha": [(1, Color.BLACK)]
            }),
            "Oklahoma City": City("Oklahoma City", {
                "Kansas City": [(2, Color.YELLOW), (2, Color.RED)],
                "Dallas": [(2, Color.BLACK)],
                "Little Rock": [(2, Color.BLACK)],
                "Santa Fe": [(3, Color.BLUE)]
            }),
            "Dallas": City("Dallas", {
                "Oklahoma City": [(2, Color.BLACK)],
                "Little Rock": [(2, Color.BLACK)],
                "Houston": [(1, Color.BLACK)]
            }),
            "Little Rock": City("Little Rock", {
                "Oklahoma City": [(2, Color.BLACK)],
                "Dallas": [(2, Color.BLACK)],
                "Saint Louis": [(2, Color.BLACK)],
                "New Orleans": [(3, Color.GREEN)]
            }),
            "Houston": City("Houston", {
                "Dallas": [(1, Color.BLACK)],
                "New Orleans": [(2, Color.ORANGE)],
                "El Paso": [(6, Color.GREEN)]
            }),
            "New Orleans": City("New Orleans", {
                "Little Rock": [(3, Color.GREEN)],
                "Houston": [(2, Color.ORANGE)],
                "Miami": [(6, Color.RED)],
                "Atlanta": [(4, Color.YELLOW)]
            }),
            "Miami": City("Miami", {
                "Atlanta": [(5, Color.BLUE)],
                "New Orleans": [(6, Color.RED)]
            }),
            "Denver": City("Denver", {
                "Kansas City": [(4, Color.BLACK), (4, Color.ORANGE)],
                "Oklahoma City": [(4, Color.RED)],
                "Santa Fe": [(2, Color.BLACK)],
                "Phoenix": [(5, Color.WHITE)],
                "Salt Lake City": [(3, Color.RED), (3, Color.YELLOW)],
                "Helena": [(4, Color.GREEN)]
            }),
            "Santa Fe": City("Santa Fe", {
                "Denver": [(2, Color.BLACK)],
                "Oklahoma City": [(3, Color.BLUE)],
                "Phoenix": [(3, Color.BLACK)],
                "El Paso": [(2, Color.BLACK)]
            }),
            "Phoenix": City("Phoenix", {
                "Santa Fe": [(3, Color.BLACK)],
                "Denver": [(5, Color.WHITE)],
                "Los Angeles": [(6, Color.BLACK)],
                "El Paso": [(3, Color.BLACK)]
            }),
            "El Paso": City("El Paso", {
                "Phoenix": [(3, Color.BLACK)],
                "Santa Fe": [(2, Color.BLACK)],
                "Houston": [(6, Color.GREEN)],
                "Dallas": [(4, Color.RED)],
                "Oklahoma City": [(5, Color.YELLOW)],
                "Los Angeles": [(6, Color.BLACK)]
            }),
            "Salt Lake City": City("Salt Lake City", {
                "Denver": [(3, Color.RED), (3, Color.YELLOW)],
                "Helena": [(3, Color.PINK)],
                "Las Vegas": [(3, Color.ORANGE)],
                "San Francisco": [(5, Color.ORANGE), (5, Color.WHITE)]
            }),
            "Helena": City("Helena", {
                "Salt Lake City": [(3, Color.PINK)],
                "Denver": [(4, Color.GREEN)],
                "Omaha": [(5, Color.RED)],
                "Duluth": [(6, Color.ORANGE)],
                "Winnipeg": [(4, Color.BLUE)],
                "Seattle": [(6, Color.YELLOW)]
            }),
            "Omaha": City("Omaha", {
                "Chicago": [(4, Color.BLUE)],
                "Kansas City": [(1, Color.BLACK)],
                "Denver": [(4, Color.PINK)],
                "Helena": [(5, Color.RED)],
                "Duluth": [(2, Color.BLACK)]
            }),
            "Duluth": City("Duluth", {
                "Chicago": [(3, Color.RED)],
                "Omaha": [(2, Color.BLACK)],
                "Helena": [(6, Color.ORANGE)],
                "Winnipeg": [(4, Color.BLACK)],
                "Sault St. Marie": [(3, Color.BLACK)],
                "Toronto": [(6, Color.PINK)]
            }),
            "Winnipeg": City("Winnipeg", {
                "Duluth": [(4, Color.BLACK)],
                "Helena": [(4, Color.BLUE)],
                "Sault St. Marie": [(6, Color.BLACK)]
            }),
            "Sault St. Marie": City("Sault St. Marie", {
                "Duluth": [(3, Color.BLACK)],
                "Winnipeg": [(6, Color.BLACK)],
                "Toronto": [(2, Color.BLACK)],
                "Montreal": [(5, Color.BLACK)]
            }),
            "Las Vegas": City("Las Vegas", {
                "Salt Lake City": [(3, Color.ORANGE)],
                "Los Angeles": [(2, Color.BLACK)]
            }),
            "Los Angeles": City("Los Angeles", {
                "Las Vegas": [(2, Color.BLACK)],
                "Phoenix": [(6, Color.BLACK)],
                "El Paso": [(6, Color.BLACK)],
                "San Francisco": [(3, Color.PINK), (3, Color.YELLOW)]
            }),
            "San Francisco": City("San Francisco", {
                "Salt Lake City": [(5, Color.ORANGE), (5, Color.WHITE)],
                "Los Angeles": [(3, Color.PINK), (3, Color.YELLOW)],
                "Portland": [(5, Color.GREEN)]
            }),
            "Portland": City("Portland", {
                "San Francisco": [(5, Color.GREEN)],
                "Seattle": [(1, Color.BLACK)],
                "Salt Lake City": [(6, Color.BLUE)]
            }),
            "Seattle": City("Seattle", {
                "Portland": [(1, Color.BLACK)],
                "Helena": [(6, Color.YELLOW)],
                "Calgary": [(4, Color.BLACK)],
                "Vancouver": [(1, Color.BLACK)]
            }),
            "Vancouver": City("Vancouver", {
                "Seattle": [(1, Color.BLACK)],
                "Calgary": [(3, Color.BLACK)]
            }),
            "Calgary": City("Calgary", {
                "Vancouver": [(3, Color.BLACK)],
                "Seattle": [(4, Color.BLACK)],
                "Helena": [(4, Color.BLACK)],
                "Winnipeg": [(6, Color.WHITE)]
            })
        }
        return board
     
    def setup_game(self):
        # Initialise decks
        self.initialise_train_deck()
        self.initialise_destination_deck()
        
        # Deal initial cards
        for player in self.players:
            self.deal_initial_cards(player)
            
    def initialise_train_deck(self):
        # Add 12 of each color (excluding wild) and 14 wild cards
        for color in Color:
            if color != Color.WILD:
                self.train_deck.extend([color] * 12)
        self.train_deck.extend([Color.WILD] * 14)
        random.shuffle(self.train_deck)
        
        # Draw initial face-up cards
        self.face_up_cards = [self.train_deck.pop() for _ in range(5)]
    
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
    
    def deal_initial_cards(self, player: Player):
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

    def formatted_trains(self, player: Player) -> List[str]: return [f"{color.name.capitalize()}: {count}" for color, count in player.train_cards.items() if count > 0]

    def formatted_destinations(self, player: Player) -> List[str]: return [f"{destination.city1} to {destination.city2} ({destination.points})" for destination in player.destinations]

    def print_board(self):
        # Helper function to format the route status
        def format_route_status(city2: str, color: Color, claimed_by: str) -> str:
            if claimed_by:
                return f"{city2} ({color.name.capitalize()} * {length}): Claimed by {claimed_by}"
            else:
                return f"{city2} ({color.name.capitalize()} * {length}): Available"

        print("=== Ticket to Ride Board ===")
        for city_name, city in sorted(self.board.items()):
            print(f"\n{city_name}:")
            for destination, routes in sorted(city.connections.items()):
                for route in routes:
                    length, color = route
                    claimed_by = None
                    for player in self.players:
                        if (city_name, destination, color) in player.claimed_connections or \
                        (destination, city_name, color) in player.claimed_connections:
                            claimed_by = player.name
                            break
                    
                    print("  -> " + format_route_status(destination, color, claimed_by))
        print("===========================")

    def print_available_routes(self, player: Player):
        # Only show routes that player can claim with current train cards
        for city_name, city in self.board.items():
            for destination, routes in city.connections.items():
                for route in routes:
                    city1, city2 = city_name, destination
                    color = route[1]
                    length = route[0]
                    claimed = self.route_claimed(city1, city2, color)
                    if claimed is None:
                        if self.route_completable(player, city1, city2, color):
                            route_status = "Available"
                            print(f"{city_name}:")
                            print(f"  -> {destination} ({length}, {color}): {route_status}")

    def route_exists(self, city1: str, city2: str) -> bool:
        # Check both directions
        if (city1 in self.board and city2 in self.board[city1].connections) or \
        (city2 in self.board and city1 in self.board[city2].connections):
            return True
        return False

    def route_completable(self, player: Player, city1: str, city2: str, color: Color) -> bool:
        # Check first direction
        if city1 in self.board and city2 in self.board[city1].connections:
            for route_length, route_color in self.board[city1].connections[city2]:
                if color == route_color and player.train_cards[color] >= route_length:
                    return True
        
        # Check reverse direction
        if city2 in self.board and city1 in self.board[city2].connections:
            for route_length, route_color in self.board[city2].connections[city1]:
                if color == route_color and player.train_cards[color] >= route_length:
                    return True
        return False
    
    def route_claimed(self, city1: str, city2: str, color: Color):
        for player in self.players:
            if (city1, city2, color) in player.claimed_connections or \
            (city2, city1, color) in player.claimed_connections:
                return player.name
        return None

    def play_turn(self, player: Player):
        # Players can:
        # 1. Draw train cards (2 cards)
        # 2. Claim a route
        # 3. Draw destination tickets
        print("\n" + "_" * 200 )
        print(f"Turn {player.turn}" + "\n")
        print (f"\n{player.name}'s turn")
        print(f"{player.name}'s train cards: {', '.join(self.formatted_trains(player))}")
        print(f"{player.name}'s destination tickets: {', '.join(self.formatted_destinations(player))}")
        print(f"Face-up cards: {', '.join([card.name for card in self.face_up_cards])}" + "\n") 

        choice: Enum = input("<1: Draw Train cards, 2: Claim a route, 3: Draw destination tickets, 4: Print board, 5: Print routes you can complete, 6: Print score, exit: Exit game>\n")

        # Draw train cards
        if choice == "1":
            self.draw_train_cards(player)
        # Claim a route
        elif choice == "2":
            print("Choose a route to claim:")
            city1 = input("Enter the first city: ")
            if city1 == "back":
                self.play_turn(player)
            city2 = input("Enter the second city: ")
            if city2 == "back":
                self.play_turn(player)

            possibleColors: List[Color] = []
            if self.route_exists(city1, city2):
                for color in Color:
                    if self.route_completable(player, city1, city2, color):
                        possibleColors.append(color)
                        print(f"Claim route with {color}")
                # TODO - player may be in a position where they can claim a route with two color choices
                #colorChoice = input("Choose a color to claim: ")
                self.claim_route(player, city1, city2, possibleColors[0])
            else:
                print("Invalid route, going back.")
                self.play_turn(player)
        # Draw destination tickets
        elif choice == "3":
            self.draw_destination_tickets(player)
        # Print board
        elif choice == "4":
            self.print_board()
            self.play_turn(player)
        # Print routes you can complete
        elif choice == "5":
            print("Routes you can complete:")
            self.print_available_routes(player)
            self.play_turn(player)
        # Print score
        elif choice == "6":
            print(f"{player.name}'s score: {player.points}")
            self.play_turn(player)
        # Exit game
        elif choice == "exit":
            exit()
        else:
            print("Invalid choice, please try again.")
            self.play_turn(player)
        for player in self.players:
            player.turn += 1

    def draw_train_cards(self, player: Player):
        # Draw two cards from the deck or face-up cards
        drawn = 0
        while drawn < 2:
            choice = input("Would you like to draw from the face-up cards? (y/n)")
            if choice == "y":
                # Draw from face-up cards
                print("Choose a card to draw:")
                for i, card in enumerate(self.face_up_cards):
                    print(f"{i+1}: {card.name}")
                card_choice = int(input("Enter the card number: ")) - 1
                card = self.face_up_cards.pop(card_choice)
                player.train_cards[card] += 1
                print(f"{player.name} has drawn {card.name}")
                # Draw a new face-up card
                self.face_up_cards.append(self.train_deck.pop())
                print(f"New face-up cards: {', '.join([card.name for card in self.face_up_cards])}")
                drawn += 1
            elif choice == "n":
                # Draw from the deck
                card = self.train_deck.pop()
                player.train_cards[card] += 1
                print(f"{player.name} has drawn {card.name}")
                drawn += 1
            elif choice == "back":
                self.play_turn(player)
            else:
                print("Invalid choice, please try again.")

        print(f"{player.name}'s train cards: {', '.join(self.formatted_trains(player))}")
    
    def claim_route(self, player: Player, city1: str, city2: str, color: Color):
        # Find the required number of cards for this route
        route_length = self.board[city1].connections[city2][0][0]
        
        # Remove the specific cards from the player's train cards
        for _ in range(route_length):
            player.train_cards[color] -= 1
        
        player.claimed_connections.append((city1, city2, color))
        player.points += route_length
        print(f"{player.name} has claimed the route between {city1} and {city2} with {color}")
    
    def draw_destination_tickets(self, player: Player):
        # Pick up three destination tickets, player must keep at least one
        destinations = [self.destination_deck.pop() for _ in range(3)]

        print(f"{player.name} has been dealt the following destinations:  \
        {destinations[0].city1} to {destinations[0].city2} ({destinations[0].points}),  \
        {destinations[1].city1} to {destinations[1].city2} ({destinations[1].points}),  \
        {destinations[2].city1} to {destinations[2].city2} ({destinations[2].points})")
        
        numDestinations = 3
        # must keep atleast one
        while numDestinations > 1:
            choice = input("Would you like to remove any destinations? (y/n)")
            if choice == "y":
                print("Which destination would you like to remove?")
                for i, destination in enumerate(destinations):
                    print(f"{i+1}: {destination.city1} to {destination.city2} ({destination.points})")
                remove_idx = int(input("Enter the destination number to remove: ")) - 1
                removed_destination = destinations.pop(remove_idx)
                print(f"{player.name} has removed the destination between {removed_destination.city1} and {removed_destination.city2} ({removed_destination.points})")
                numDestinations -= 1
            elif choice == "n":
                break
            elif choice == "back":
                self.play_turn(player)
            else:
                print("Invalid choice, please try again.")
            
        player.destinations.extend(destinations)
        print(f"{player.name} current destinations: {', '.join(self.formatted_destinations(player))}")
        
    
    def calculate_final_scores(self):
        # TODO - calculate final scores using completed destination tickets, longest route, and remaining trains
        pass

def main():
    game = TicketToRide()
    
    # Add players
    game.players = [
        Player("Player 1"),
        Player("Player 2")
    ]
    print("\n" + "_" * 200 + "\n")
    # Set up and start the game
    game.setup_game()
    print("You can type back to go to the previous menu option")
    print("Enjoy Ticket to Ride!")
    
    # Main game loop
    game_end = False
    while not game_end:
        current_player = game.players[game.current_player_idx]
        
        game.play_turn(current_player)
        game.current_player_idx = (game.current_player_idx + 1) % len(game.players)
        
        # Check end game condition
        if current_player.remaining_trains <= 2:
            game_end = True
    
    # Calculate final scores
    game.calculate_final_scores()

if __name__ == "__main__":
    main()