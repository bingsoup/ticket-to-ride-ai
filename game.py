import copy
import platform
import random
import time
from typing import List, Optional, Tuple

# from graph import TicketToRideVisualizer
from fw import FloydWarshall
from helper_classes import Colour, Destination, Player, Route, UnionFind
from heuristic_agents import (
    BestMoveHeuristic,
    DestinationHeuristic,
    LongestRouteHeuristic,
    RandomHeuristic,
    ShaoHeuristic,
)
from map_data import MapData
from mcts import MCTS
from mcts_no_heuristics import MCTS as MCTS_no_heuristics
from mcts_rollouts import MCTS as MCTS_rollouts
from mcts_selection import MCTS as MCTS_selection
from play import PlayerController

is_pypy = False

# Only import GUI modules if not running under PyPy
is_pypy = platform.python_implementation() == "PyPy"

# Only import GUI modules if not running under PyPy or Nuitka standalone mode
if not is_pypy:
    try:
        from gui import initialise_gui, shutdown, update_game_state

        gui_available = True
    except ImportError:
        gui_available = False
        print("GUI modules couldn't be imported. Running in console-only mode.")
else:
    # Dummy functions for PyPy
    gui_available = False

    def initialise_gui():
        return False

    def update_game_state(game, action=None):
        pass

    def shutdown():
        pass

    print("Running under PyPy - GUI disabled for compatibility.")


class GameEngine:
    """
    The game engine for Ticket to Ride.
    This class is responsible for managing the game state and action logic.
    """

    def __init__(self):
        self.routes: dict = {}  # Maps city1 -> city2 -> List[Route]
        self.players: List[Player] = []  # List of players
        self.current_player_idx: int = 0  # Index of the current player
        self.current_player: Player = None  # Reference to the current player
        self.train_deck: List[Colour] = []  # Train deck
        self.discard_deck: List[Colour] = []  # Discard deck
        self.destination_deck: List[Destination] = []  # Destination ticket deck
        self.destination_discard_deck: List[
            Destination
        ] = []  # Discard deck for destination tickets
        self.face_up_cards: List[Colour] = []  # Face-up cards
        # self.visualizer = TicketToRideVisualizer(self) # Displays the board state in image form
        self.fw: FloydWarshall = (
            None  # Floyd-Warshall object for shortest path calculations
        )
        self.routes_cache: dict = {}  # Player dependent cache for unclaimed routes
        self.routes_cache_valid: dict = {}  # Flag to indicate if cache needs update
        self.best_routes_cache: dict = {}  # Player dependent cache for best routes
        self.best_routes_cache_valid: dict = {}  # Flag to indicate if cache needs update
        self.map_data: MapData = None  # Map data object
        self.map_type: str = "USA"  # Default map type
        self.most_recent_hits: int = 0  # Most recent hits for tunnel routes

    def init(self, players: List[Player]):
        """
        Ordered initialisation of the engine.

        :param players: List of players to be added to the game
        :type players: List[Player]
        """
        self.players = players
        self.map_data = MapData(self.map_type)
        self.initialise_destination_deck()
        self.initialise_routes()

        self.fw = FloydWarshall(self.routes)
        # Add 12 of each colour (excluding wild) and 14 wild cards
        self.setup_train_deck()
        self.deal_initial_cards()
        # Draw initial face-up cards
        self.face_up_cards = [self.train_deck.pop() for _ in range(5)]
        self.current_player = self.players[self.current_player_idx]
        # Initialise union-find
        self.init_uf()

    def formatted_trains(self, player: Player) -> List[str]:
        """
        Formats all of a player's train cards for strings.

        :param player: The player whose train cards to format
        :type player: Player
        :return: List of formatted strings for train cards
        :rtype: List[str]
        """
        return [
            f"{colour.value}: {count}"
            for colour, count in player.train_cards.items()
            if count > 0
        ]

    def formatted_destinations(self, player: Player) -> List[str]:
        """
        Formats all of a player's destinations for strings.

        :param player: _description_
        :type player: Player
        :return: _description_
        :rtype: List[str]
        """
        return [
            f"{destination.city1} to {destination.city2} ({destination.points})"
            for destination in player.destinations
        ]

    def deal_initial_cards(self):
        """Deals initial cards to players."""
        for player in self.players:
            # Deal 4 train cards to each player
            for _ in range(4):
                card = self.train_deck.pop()
                player.train_cards[card] += 1
            # Deal 3 destination cards
            destinations = [self.destination_deck.pop() for _ in range(3)]
            player.destinations.extend(destinations[:3])

            print(
                f"{player.name} has been dealt the following destinations: {', '.join(self.formatted_destinations(player))}"
            )
            print(
                f"{player.name} has been dealt the following train cards: {', '.join(self.formatted_trains(player))}"
            )

    def init_uf(self):
        """Initialises the union-find data structure for each player."""
        for player in self.players:
            player.uf = UnionFind(self.routes.keys())

    def initialise_destination_deck(self):
        """Add destinations to the destination deck and shuffle it."""
        if self.map_data:
            dest_deck = self.map_data.get_destinations()
            self.destination_deck = dest_deck if dest_deck else []
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
        self.city_to_routes = {}  # Maps cities to their routes
        self.route_pairs = {}  # Maps (city1,city2) to route objects

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
                self.city_to_routes[city1].extend(
                    [(city2, route) for route in routes_list]
                )

        self.city_names = sorted(
            list(
                set(
                    [city for routes in self.routes.values() for city in routes.keys()]
                    + [city for city in self.routes.keys()]
                )
            )
        )
        self.city_to_idx = {city: i for i, city in enumerate(self.city_names)}
        self.idx_to_city = {i: city for i, city in enumerate(self.city_names)}

        # Create adjacency matrix for faster lookups
        n = len(self.city_names)
        self.adjacency = [[[] for _ in range(n)] for _ in range(n)]
        # Populate AM
        for city1, connections in self.routes.items():
            i = self.city_to_idx[city1]
            for city2, routes_list in connections.items():
                j = self.city_to_idx[city2]
                self.adjacency[i][j] = routes_list

    def route_lookup(self, city1: str, city2: str) -> List[Route]:
        """
        AM route lookup for adjacency between two cities.

        :param city1: First city
        :type city1: str
        :param city2: Second city
        :type city2: str
        :return: List of routes between the two cities
        :rtype: List[Route]
        """
        if (
            hasattr(self, "city_to_idx")
            and city1 in self.city_to_idx
            and city2 in self.city_to_idx
        ):
            i = self.city_to_idx[city1]
            j = self.city_to_idx[city2]
            return self.adjacency[i][j]
        # Shouldn't ever happen
        print(f"Error: {city1} or {city2} not in city_to_idx")
        return []

    def update_player_turn(self):
        """Update the current player to the next in the list."""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.current_player = self.players[self.current_player_idx]

    def set_player_routes(self):
        """
        Get all claim actions legal for the player using adjacency matrix, with player-specific caching.

        :return: List of actions where each action is a tuple
        :rtype: List[tuple("claim_route", city1, city2, colour, player)]
        """
        current_player = self.current_player
        cache_key = current_player.name

        # Return cached result if available
        if cache_key in self.routes_cache and self.routes_cache_valid.get(
            cache_key, False
        ):
            return self.routes_cache[cache_key].copy()

        route_actions = []
        n = len(self.city_names)

        # Iterate through adjacency matrix
        for i in range(n):
            city1 = self.idx_to_city[i]
            for j in range(i + 1, n):
                city2 = self.idx_to_city[j]
                routes_list = self.adjacency[i][j]

                # Skip if this is a double route and the player already owns one of the routes
                is_double_route = len(routes_list) > 1
                if is_double_route:
                    player_owns_route = False
                    # If it's only two players, do not allow double route claiming
                    for player in self.players:
                        for conn in player.claimed_connections:
                            conn_city1, conn_city2 = conn[0], conn[1]
                            if (conn_city1 == city1 and conn_city2 == city2) or (
                                conn_city1 == city2 and conn_city2 == city1
                            ):
                                if len(self.players) == 2:
                                    player_owns_route = True
                                    break
                                elif player.name == current_player.name:
                                    player_owns_route = True
                                    break
                    if player_owns_route:
                        continue  # Skip all routes between these cities if player already owns one

                for route in routes_list:
                    if route.claimed_by is None:
                        if current_player.remaining_trains > route.length:
                            # For gray routes, check each colour
                            if route.colour == Colour.GRAY:
                                for colour in Colour:
                                    if colour != Colour.WILD and colour != Colour.GRAY:
                                        cards_needed = route.length
                                        cards_available = current_player.train_cards[
                                            colour
                                        ]
                                        wilds_available = current_player.train_cards[
                                            Colour.WILD
                                        ]
                                        wilds_required = route.num_locomotives
                                        wilds_needed = max(
                                            wilds_required,
                                            (
                                                route.length
                                                - current_player.train_cards[colour]
                                            ),
                                        )

                                        if (
                                            cards_available + wilds_available
                                            >= cards_needed + wilds_required
                                        ):
                                            for wilds_used in range(
                                                wilds_needed, wilds_available + 1
                                            ):
                                                route_actions.append(
                                                    (
                                                        "claim_route",
                                                        city1,
                                                        city2,
                                                        colour,
                                                        wilds_used,
                                                        route,
                                                        current_player.name,
                                                    )
                                                )
                            else:
                                # For coloured routes
                                colour = route.colour
                                cards_needed = route.length
                                cards_available = current_player.train_cards[colour]
                                wilds_available = current_player.train_cards[
                                    Colour.WILD
                                ]
                                wilds_needed = max(
                                    0,
                                    (route.length - current_player.train_cards[colour]),
                                )
                                if cards_available + wilds_available >= cards_needed:
                                    for wilds_used in range(
                                        wilds_needed, wilds_available + 1
                                    ):
                                        route_actions.append(
                                            (
                                                "claim_route",
                                                city1,
                                                city2,
                                                colour,
                                                wilds_used,
                                                route,
                                                current_player.name,
                                            )
                                        )

        # Store in cache
        self.routes_cache[cache_key] = route_actions.copy()
        self.routes_cache_valid[cache_key] = True

        return route_actions

    def cache_update_helper(self, city1, city2):
        """
        Update the unclaimed routes cache when a route is claimed.

        :param city1: First city
        :type city1: str
        :param city2: Second city
        :type city2: str
        """
        if hasattr(self, "_unclaimed_routes_cache"):
            i = self.city_to_idx[city1]
            j = self.city_to_idx[city2]
            # If the route is claimed, remove it from the cache
            self.unclaimed_routes_cache = [
                (a, b, r)
                for a, b, r in self.unclaimed_routes_cache
                if not ((a == i and b == j) or (a == j and b == i))
            ]

    def claim_route_helper(
        self, colour: Colour, player: str, num_hits: int, routes
    ) -> bool:
        """
        Claims the route if possible, otherwise returns False.

        :param colour: Colour of the route
        :type colour: Colour
        :param player: Name of player claiming the route
        :type player: str
        :param num_hits: Number of hits for tunnel routes
        :type num_hits: int
        :param routes: List of routes to claim
        :type routes: List[Route]
        :return: True if the route was claimed, False otherwise
        :rtype: bool
        """
        claimed = [False] * len(routes)
        for i, route in enumerate(routes):
            claimed[i] = route.is_claimed()
            if (
                colour == Colour.WILD
                or route.colour == colour
                or route.colour == Colour.GRAY
            ) and not claimed[i]:
                if (
                    self.current_player.train_cards[colour]
                    + self.current_player.train_cards[Colour.WILD]
                    >= route.length + num_hits
                ):
                    # Update route state
                    route.claim(player)
                    # Invalidate cache when route is claimed
                    for player in self.players:
                        self.routes_cache_valid[player.name] = False
                else:
                    claimed[i] = True
                    if num_hits == 0:
                        print(
                            f"Player {player} does not have enough cards to claim route"
                        )

        if all(claimed):
            return False
        return True

    def claim_route(
        self, city1: str, city2: str, colour: Colour, player: str, num_hits: int
    ) -> bool:
        """
        Checks whether any of the routes between cities with a given can be claimed
        I have to to do it like this because you can have multiple gray routes between two cities
        And all of them must be claimable...
        :param city1: First city
        :type city1: str
        :param city2: Second city
        :type city2: str
        :param colour: Colour of the route
        :type colour: Colour
        :param player: Name of player claiming the route
        :type player: str
        :param num_hits: Precomputed number of hits for tunnel routes
        :type num_hits: int
        :return: True if the route was claimed, False otherwise
        :rtype: bool
        """

        routes = self.route_lookup(city1, city2)
        if len(routes) == 4:
            path1 = [routes[0], routes[2]]
            p1 = self.claim_route_helper(colour, player, num_hits, path1)
            if p1:
                return True
            path2 = [routes[1], routes[3]]
            p2 = self.claim_route_helper(colour, player, num_hits, path2)
            if p2:
                return True
            return False
        else:  # Only one direction so can claim both
            if self.claim_route_helper(colour, player, num_hits, routes):
                return True
        return False

    def check_hits(self, route: Route, colour) -> int:
        """
        Checks how many additional cards are needed for a tunnel route.
        Draws up to 3 cards and counts matches to the route color or wild cards.

        :param route: The tunnel route being claimed
        :type route: Route
        :param colour: The color being used to claim the route
        :type colour: Colour
        :return: Number of additional cards needed (hits)
        :rtype: int
        """
        num_hits = 0

        # Only check tunnel routes
        if not route.tunnel:
            return num_hits

        # Ensure we have enough cards to check
        if len(self.train_deck) < 3 and self.discard_deck:
            self.train_deck.extend(self.discard_deck)
            self.discard_deck.clear()
            random.shuffle(self.train_deck)

        # Draw up to 3 cards and check for matches
        for _ in range(min(3, len(self.train_deck))):
            card = self.train_deck.pop()
            self.discard_deck.insert(0, card)  # Move drawn cards to discard pile
            if card == Colour.WILD or card == colour:
                num_hits += 1

        # Keep track of the most recent hits for final actions
        self.most_recent_hits = num_hits

        return num_hits

    def get_route_length(self, city1: str, city2: str) -> Optional[int]:
        """Get the length of a specific route."""
        routes = self.route_lookup(city1, city2)
        return routes[0].length

    def setup_train_deck(self):
        for colour in Colour:
            if colour != Colour.WILD and colour != Colour.GRAY:
                self.train_deck.extend([colour] * 12)
        self.train_deck.extend([Colour.WILD] * 14)
        random.shuffle(self.train_deck)

    def draw_train_face(self, i: int, card: Colour):
        """Draw a face-up card."""
        if len(self.train_deck) == 0:
            if len(self.discard_deck) == 0:
                # print("Broken")
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
                # print("Broken")
                return
            self.train_deck.extend(self.discard_deck)
            self.discard_deck.clear()
        card = self.train_deck.pop()
        self.players[self.current_player_idx].train_cards[card] += 1

    def check_all_destinations(self, player) -> List[Tuple[Destination, bool]]:
        """
        Checks completion status of all destination tickets for a player.
        Uses the player's UnionFind data structure for efficient connectivity checking.

        :param player: The player whose destinations to check
        :type player: Player
        :return: List of tuples containing (destination, completion status)
        :rtype: List[Tuple[Destination, bool]]
        """
        destination_results = []
        for destination in player.destinations:
            city1, city2 = destination.city1, destination.city2
            if player.uf.is_connected(city1, city2):
                destination_results.append((destination, True))
            else:
                destination_results.append((destination, False))
        return destination_results

    def calc_route_points(self, route_length: int) -> int:
        """
        Calculates points earned for claiming a route based on its length.

        :param route_length: Length of the claimed route
        :type route_length: int
        :return: Points earned for the route
        :rtype: int
        """
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
        """
        Displays all routes claimed by each player for debugging.
        """
        for player in self.players:
            used_trains = 0
            print(f"{player.name} has claimed the following routes:")
            for city1, city2, colour in player.claimed_connections:
                used_trains += self.get_route_length(city1, city2)
                print(
                    f"{city1} to {city2} with {colour.value} and length {self.get_route_length(city1, city2)}"
                )

    # MCTS methods
    def copy(self):
        """
        Creates a copy of the current game state for simulation purposes.
        Efficiently copies all game elements including players, decks, and game state.

        :return: A new GameEngine instance with copied state
        :rtype: GameEngine
        """
        # Create a new instance
        new_state = GameEngine()

        # Copy id values
        new_state.current_player_idx = self.current_player_idx

        # Copy simple collections directly
        new_state.train_deck = self.train_deck.copy() if self.train_deck else []
        new_state.destination_deck = (
            self.destination_deck.copy() if self.destination_deck else []
        )
        new_state.face_up_cards = (
            self.face_up_cards.copy() if self.face_up_cards else []
        )

        # Copy indexing structures (these are mostly immutable after creation)
        if hasattr(self, "city_names"):
            new_state.city_names = self.city_names.copy()
        if hasattr(self, "city_to_idx"):
            new_state.city_to_idx = self.city_to_idx.copy()
        if hasattr(self, "idx_to_city"):
            new_state.idx_to_city = self.idx_to_city.copy()

        # More efficient copying of lookup structures
        if hasattr(self, "city_to_routes"):
            new_state.city_to_routes = {}
            for city, routes in self.city_to_routes.items():
                new_state.city_to_routes[city] = routes.copy()

        if hasattr(self, "route_pairs"):
            new_state.route_pairs = {}
            for key, routes in self.route_pairs.items():
                new_state.route_pairs[key] = [
                    Route(r.length, r.colour, r.claimed_by) for r in routes
                ]

        # Efficiently copy adjacency matrix if it exists
        if hasattr(self, "adjacency") and self.adjacency:
            n = len(self.adjacency)
            new_state.adjacency = [[[] for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    if self.adjacency[i][j]:  # Only copy non-empty lists
                        new_state.adjacency[i][j] = [
                            Route(r.length, r.colour, r.claimed_by)
                            for r in self.adjacency[i][j]
                        ]

        # Copy caches over
        new_state.routes_cache = self.routes_cache.copy() if self.routes_cache else {}
        new_state.routes_cache_valid = (
            self.routes_cache_valid.copy() if self.routes_cache_valid else {}
        )
        new_state.best_routes_cache = (
            self.best_routes_cache.copy() if self.best_routes_cache else {}
        )
        new_state.best_routes_cache_valid = (
            self.best_routes_cache_valid.copy() if self.best_routes_cache_valid else {}
        )

        # Handle FloydWarshall - lazy instantiation
        new_state.fw = self.fw

        # Copy players
        new_state.players = []
        for player in self.players:
            # Create new player with basic attributes
            new_player = Player(
                name=player.name, remaining_trains=player.remaining_trains
            )

            # Copy collections
            new_player.train_cards = {
                colour: count for colour, count in player.train_cards.items()
            }
            new_player.destinations = (
                player.destinations.copy() if player.destinations else []
            )
            new_player.claimed_connections = (
                player.claimed_connections.copy() if player.claimed_connections else []
            )
            new_player.claimed_cities = (
                set(player.claimed_cities) if player.claimed_cities else set()
            )
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
        new_state.current_player = (
            new_state.players[new_state.current_player_idx]
            if new_state.players
            else None
        )
        return new_state

    def apply_action(self, action):
        """
        Applies an action to the game state.
        Used because some actions (e.g. MCTS sims) do not need to be printed out.

        :param action: A formatted action
        :type action: tuple(str, ...)
        :return: True if legal, False otherwise
        :rtype: bool
        """
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
            case ["claim_route", city1, city2, colour, wilds_used, route, player_name]:
                num_hits = self.check_hits(route, colour)
                if self.claim_route(city1, city2, colour, player_name, num_hits):
                    route_length = self.get_route_length(city1, city2) or 0
                    total_length = route_length + num_hits

                    # Calculate the minimum number of wilds the player now has to use to complete the route
                    # Or return False if not possible because of too many tunnel hits.
                    if num_hits > 0:
                        if total_length > player.train_cards[colour]:
                            wilds_used += total_length - player.train_cards[colour]
                            if wilds_used > player.train_cards[Colour.WILD]:
                                if wilds_used > player.train_cards[Colour.WILD]:
                                    return False

                    # If the route is in the best routes cache, invalidate it
                    if self.best_routes_cache.get(player_name, False):
                        for i in range(len(self.best_routes_cache[player.name])):
                            if self.best_routes_cache[player.name][i][1] == (
                                city1 or city2
                            ) and self.best_routes_cache[player.name][i][2] == (
                                city1 or city2
                            ):
                                self.best_routes_cache_valid[player.name] = False

                    player.train_cards[Colour.WILD] -= wilds_used
                    player.train_cards[colour] -= max(0, total_length - wilds_used)
                    self.discard_deck.extend([Colour.WILD] * wilds_used)
                    self.discard_deck.extend([colour] * (total_length - wilds_used))
                    player.claimed_connections.append((city1, city2, colour))
                    player.claimed_cities.add(city1)
                    player.claimed_cities.add(city2)
                    points = self.calc_route_points(route_length)
                    if points is not None:
                        player.points += points
                    else:
                        print(f"Error: route length is {route_length}")
                    player.uf.union(city1, city2)

                    self.cache_update_helper(city1, city2)
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
                    destinations.append(choices[random.randint(0, 2)])
                self.destination_discard_deck.extend(
                    [dest for dest in choices if dest not in destinations]
                )
                self.current_player.destinations.extend(destinations)

    def apply_action_final(self, action):
        """
        Formats an print statement for the action taken by the player.
        Uses apply action to commit the action itself.

        :param action: A formatted action
        :type action: Tuple (str, ...)
        """
        success = self.apply_action(action)

        print(f"{self.current_player.name}'s hand:")
        for colour, count in self.current_player.train_cards.items():
            if count > 0:
                print(f"{colour.value}: {count}")
        match action:
            case [
                "draw_two_train_cards",
                idx1,
                card1,
                idx2,
                card2,
                player_name,
            ]:
                # Convert to strings and format
                if card1 != "deck" and card1 != "nodraw":
                    card1 = card1.value
                if card2 != "deck" and card2 != "nodraw":
                    card2 = card2.value
                if card2 == "nodraw":
                    print(f"{player_name} has drawn a Wild card")
                else:
                    print(f"{player_name} has drawn two train cards: {card1}, {card2}")

            case ["claim_route", city1, city2, colour, wilds_used, route, player_name]:
                route_length = self.get_route_length(city1, city2)
                num_hits = self.most_recent_hits
                if route.tunnel and self.most_recent_hits > 0:
                    self.most_recent_hits = 0
                if success:
                    if num_hits > 0:
                        print(
                            f"{player_name} has claimed a route of length {route_length} between {city1} and {city2} with {colour.value} using {wilds_used} wild cards and {num_hits} hits"
                        )
                    elif wilds_used > 0:
                        print(
                            f"{player_name} has claimed a route of length {route_length} between {city1} and {city2} with {colour.value} using {wilds_used} wild cards"
                        )
                    else:
                        print(
                            f"{player_name} has claimed a route of length {route_length} between {city1} and {city2} with {colour.value}"
                        )
                else:
                    print(
                        f"{player_name} got {num_hits} hits on a {route_length} route between {city1} and {city2} with {colour.value}"
                    )

            case ["draw_destination_tickets", i, j, k, player_name]:
                ijk = sum([i, j, k])
                print(f"{player_name} has drawn destination tickets and kept {ijk}")

        print(
            f"Remaining trains {self.current_player.name}: {self.current_player.remaining_trains}"
        )
        dest_completion = self.get_distance(self.current_player)
        for destination in dest_completion:
            distance = destination[1]
            dest = destination[0]
            if distance == 0:
                print(
                    f"{self.current_player.name} has completed destination ticket {dest.city1} to {dest.city2} ({dest.points} points)"
                )
            else:
                print(
                    f"{self.current_player.name} is {distance} trains away from completing destination ticket {dest.city1} to {dest.city2} ({dest.points} points)"
                )
        print("")

    def is_end(self):
        """
        Determines if the game has reached its end condition.
        Game ends when any player has 2 or fewer trains remaining.

        :return: True if either player has 2 of fewer trains, False otherwise
        :rtype: bool
        """
        # Check if the game state is terminal
        return any([True for player in self.players if player.remaining_trains <= 2])

    def get_legal_actions(self):
        """
        Generates all legal actions for the current player.
        Includes route claiming, card drawing, and destination ticket actions.
        Uses caching for efficient route action generation.

        :return: List of all legal actions in the current game state
        :rtype: List[Tuple]
        """
        legal_actions = []
        current_player = self.current_player

        legal_actions = self.set_player_routes()

        # Draw two train cards. Enumerate all possible combinations of face-up cards and deck cards
        if len(self.train_deck) + len(self.discard_deck) > 10:  # Dont hog cards
            for i, card1 in enumerate(self.face_up_cards):
                if card1 != Colour.WILD:
                    for j, card2 in enumerate(self.face_up_cards):
                        if j == i:
                            if len(self.train_deck) > 0:
                                card2 = self.train_deck[0]
                        if card2 != Colour.WILD:
                            legal_actions.append(
                                (
                                    "draw_two_train_cards",
                                    i,
                                    card1,
                                    j,
                                    card2,
                                    current_player.name,
                                )
                            )
                    legal_actions.append(
                        (
                            "draw_two_train_cards",
                            i,
                            card1,
                            "deck",
                            "deck",
                            current_player.name,
                        )
                    )
                else:
                    legal_actions.append(
                        (
                            "draw_two_train_cards",
                            i,
                            card1,
                            "nodraw",
                            "nodraw",
                            current_player.name,
                        )
                    )
            legal_actions.append(
                (
                    "draw_two_train_cards",
                    "deck",
                    "deck",
                    "deck",
                    "deck",
                    current_player.name,
                )
            )
        num_destinations = len(current_player.destinations)
        if num_destinations < 10:
            if len(self.destination_deck) >= 5:
                # Draw destination tickets: scry three, keep minimum one
                for i in range(2):
                    for j in range(2):
                        for k in range(2):
                            if i + j + k >= 1:
                                legal_actions.append(
                                    (
                                        "draw_destination_tickets",
                                        i,
                                        j,
                                        k,
                                        current_player.name,
                                    )
                                )
        return legal_actions

    def get_longest_route_length(self, player):
        """
        Calculates the longest continuous route length for a player.
        Uses DFS to find the longest path in the player's network.

        :param player: The player to calculate for
        :type player: Player
        :return: Length of the longest continuous route
        :rtype: int
        """
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
                    longest = max(
                        longest, dfs(next_city, visited, path_length + route_length)
                    )

            visited.remove(city)  # Backtrack
            return longest

        # Try each city as a starting point
        for city in player.claimed_cities:
            if city in connections:
                length = dfs(city, set(), 0)
                max_length = max(max_length, length)

        return max_length

    def remove_destination_tickets(self, player, destinations_remove):
        """
        Removes destination tickets from a player based on a selection array.

        :param player: The player whose tickets will be modified
        :type player: Player
        :param destinations_remove: Binary array where 1s indicate tickets to keep
        :type destinations_remove: List[int]
        """
        player.destinations = [
            dest
            for i, dest in enumerate(player.destinations)
            if destinations_remove[i] == 1
        ]

    def get_distance(self, player):
        """
        Calculates how close a player is to completing each destination ticket.
        For each destination, determines the minimum number of additional trains needed.

        :param player: The player to analyze
        :type player: Player
        :return: List of tuples (destination, distance) where distance is train count needed
        :rtype: List[Tuple[Destination, int]]
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
                dist_to_city1 = float("inf")
                dist_to_city2 = float("inf")

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
        Selects optimal route claiming actions that help complete destination tickets.
        Prioritizes routes that directly complete tickets or are on optimal paths.
        Applies penalties based on how many cards are required for the action.

        :param route_actions: List of possible route claiming actions
        :type route_actions: List[Tuple]
        :return: Selected route action or None if none are beneficial
        :rtype: Tuple or None
        """
        if not route_actions:
            return None

        player = self.current_player
        beneficial_actions = []

        for action in route_actions:
            city1, city2 = action[1], action[2]
            colour = action[3]
            route = action[5]

            # Calculate card penalty (100 points per card needed)
            route_length = route.length
            cards_available = player.train_cards[colour]
            cards_needed = max(
                0, route_length - cards_available - player.train_cards[Colour.WILD]
            )
            card_penalty = cards_needed * 100
            completion = False

            # Step 1: Check if claiming a route directly completes a destination ticket
            for dest in player.destinations:
                if not player.uf.is_connected(dest.city1, dest.city2):
                    if (
                        player.uf.is_connected(city1, dest.city1)
                        and player.uf.is_connected(city2, dest.city2)
                    ) or (
                        player.uf.is_connected(city1, dest.city2)
                        and player.uf.is_connected(city2, dest.city1)
                    ):
                        # Direct completion - highest priority, but with card penalty
                        beneficial_actions.append(
                            (action, 1000 + dest.points - card_penalty)
                        )
                        completion = True
                        break

            # If we already found a high-value action, continue to next route
            if completion:
                continue

            # Step 2: Check if route is on the optimal path between destination endpoints
            for dest in player.destinations:
                # Skip completed destinations
                if player.uf.is_connected(dest.city1, dest.city2):
                    continue

                # Get the optimal path between destination endpoints
                optimal_path = self.fw.get_path(dest.city1, dest.city2)
                if city1 in optimal_path or city2 in optimal_path:
                    # If both cities are adjacent on the optimal path, it's even more valuable
                    if city1 in optimal_path and city2 in optimal_path:
                        idx1 = optimal_path.index(city1)
                        idx2 = optimal_path.index(city2)
                        if abs(idx1 - idx2) == 1:  # Cities are adjacent in the path
                            beneficial_actions.append(
                                (action, 400 + dest.points - card_penalty)
                            )
                            break

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
            if hasattr(fw, "get_path"):
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
                for i in range(len(path) - 1):
                    city1, city2 = path[i], path[i + 1]
                    # Check if this edge (city1->city2) exists in the other path
                    for j in range(len(other_path) - 1):
                        if (other_path[j] == city1 and other_path[j + 1] == city2) or (
                            other_path[j] == city2 and other_path[j + 1] == city1
                        ):
                            shared_edges += 1
                            break

                # Add value for shared edges (major bonus - saves actual trains)
                if shared_edges > 0:
                    path_overlap_score += shared_edges * other_dest.points / 15

                # Add intersection bonus (minor bonus - potential hub cities)
                # Check for city intersections that aren't already counted in shared edges
                path_set = set(path)
                other_set = set(other_path)
                intersections = path_set.intersection(other_set)

                # Don't double-count: subtract cities that are part of shared edges
                edge_cities = set()
                for i in range(len(path) - 1):
                    city1, city2 = path[i], path[i + 1]
                    for j in range(len(other_path) - 1):
                        if (other_path[j] == city1 and other_path[j + 1] == city2) or (
                            other_path[j] == city2 and other_path[j + 1] == city1
                        ):
                            edge_cities.add(city1)
                            edge_cities.add(city2)

                # Only count intersections that aren't part of shared edges
                unique_intersections = intersections - edge_cities
                if unique_intersections:
                    # Small bonus for intersecting cities (much less than shared edges)
                    intersection_score += (
                        len(unique_intersections) * other_dest.points / 40
                    )

            # Calculate final score with bonuses for shared edges, intersections, and endpoints
            final_score = (
                points_per_distance
                + (path_overlap_score * 0.8)
                + (intersection_score * 0.2)
            )

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
            print(
                f"{status}: {dest.city1} to {dest.city2} ({dest.points} points, score: {score:.2f})"
            )

        return result

    def switch_turn(self):
        """
        Advances the game to the next player's turn.
        Updates both the current_player_idx and the current_player reference.
        """
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.current_player = self.players[self.current_player_idx]

    def game_result(self, game_num):
        """
        Calculates final scores for all players and returns current player's score.
        Doesn't print, used during MCTS simulations to evaluate game outcomes.

        :param game_num: The game number (used for tracking in simulations)
        :type game_num: int
        :return: Current player's final score
        :rtype: int
        """
        longest_score = 5
        longest_player = None
        current_player = self.current_player
        for player in self.players:
            destination_results = self.check_all_destinations(player)
            longest = self.get_longest_route_length(player)

            if longest >= longest_score:
                longest_score = longest
                longest_player = player

            for destination, is_complete in destination_results:
                if is_complete:
                    player.points += destination.points
                else:
                    player.points -= destination.points

        if longest_player:
            longest_player.points += 10

        return current_player.points

    def print_score(self):
        """
        Calculates and displays each player's current score including:
        - Base points from claimed routes
        - Projected points from completed/uncompleted destinations
        - Potential longest route bonus

        This shows the current game state without modifying player points.
        """
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
        """
        Calculates and displays final scores for all players at game end.
        Updates player points with destination bonuses/penalties and longest route bonus.
        Sets the winner flag for the player(s) with highest score.

        :param game_num: The game number
        :type game_num: int
        :return: List of players with updated scores and winner status
        :rtype: List[Player]
        """
        print(f"Game {game_num}:")

        # First calculate longest routes
        longest_routes = [
            (player, self.get_longest_route_length(player)) for player in self.players
        ]
        longest_routes.sort(key=lambda x: x[1], reverse=True)  # Sort by length

        # Award bonus to player with longest route
        if longest_routes[0][1] >= 5:
            if longest_routes[0][1] > longest_routes[1][1]:
                longest_player = longest_routes[0][0]
                longest_player.points += 10
                print(
                    f"{longest_player.name} gets 10 bonus points for the longest continuous route of length {longest_routes[0][1]}!"
                )
            else:
                longest_player1, longest_player2 = (
                    longest_routes[0][0],
                    longest_routes[1][0],
                )
                longest_player1.points += 10
                longest_player2.points += 10
                print(
                    f"{longest_player1.name} and {longest_player2.name} both get 10 bonus points for the longest continuous route of length {longest_routes[0][1]}!"
                )
        else:
            print("No player gets longest route.")

        # Calculate and display final scores for each player
        for player in self.players:
            print(f"Score {player.name}: {player.points}")
            destination_results = self.check_all_destinations(player)
            for destination, is_complete in destination_results:
                if is_complete:
                    player.points += destination.points
                    print(
                        f"Destination between {destination.city1} and {destination.city2} has been completed. Total score: {player.points}"
                    )
                else:
                    player.points -= destination.points
                    print(
                        f"Destination between {destination.city1} and {destination.city2} has not been completed. Total score: {player.points}"
                    )

            # Show longest route length for each player
            print(f"Longest continuous route: {self.get_longest_route_length(player)}")
            print("Final score: ", player.points)

        for player in self.players:
            if player.points == max([p.points for p in self.players]):
                player.winner = True
                player.wins += 1
                print(f"{player.name} wins!")

        return self.players


def main():
    timestart = time.time()

    # Ask user for number of players and agent types
    print("\nWelcome to Ticket to Ride!")

    if gui_available:
        use_gui = input("Do you want to use the GUI? (y/n): ").lower() == "y"

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
            map_type = input(
                "Which map would you like to play on? (USA or Europe): "
            ).lower()
            if map_type == "usa":
                chosen_map_type = "USA"
                break
            elif map_type == "europe":
                chosen_map_type = "Europe"
                break
            else:
                print("Please enter USA or Europe.")
        except ValueError:
            print("Please enter text.")

    # Define agent options
    agent_options = {
        1: "Human Player",
        2: "MCTS Tuned AI",
        3: "MCTS Rollouts AI",
        4: "MCTS Selection AI",
        5: "MCTS Untuned AI",
        6: "Destination Heuristic AI",
        7: "Longest Route Heuristic AI",
        8: "Best Move Heuristic AI",
        9: "ShaoPlayer AI",
        10: "Random AI",
    }

    # Create players array and agent mapping
    players = []
    player_agents = {}  # Maps player name to agent type
    mcts_params = {}  # Store custom MCTS parameters for each player

    # Default MCTS parameters (used if not customized)
    default_num_sims = 3000
    default_max_depth = 10

    for i in range(num_players):
        print(f"\nPlayer {i + 1} options:")
        for key, value in agent_options.items():
            print(f"{key}: {value}")

        while True:
            try:
                agent_type = int(input(f"Select agent type for Player {i + 1}: "))
                if 1 <= agent_type <= len(agent_options):
                    break
                else:
                    print(f"Please enter a number between 1 and {len(agent_options)}.")
            except ValueError:
                print("Please enter a valid number.")

        # If MCTS AI is selected, prompt for parameters
        if agent_type == 2 or agent_type == 3 or agent_type == 4 or agent_type == 5:
            while True:
                try:
                    customize = input(
                        "Do you want to customize MCTS parameters? (y/n): "
                    ).lower()
                    if customize in ["y", "n"]:
                        if customize == "y":
                            # Get number of simulations
                            while True:
                                try:
                                    num_sims = int(
                                        input(
                                            "Enter number of simulations for MCTS (500-20000, default: 3000)"
                                        )
                                    )
                                    if 500 <= num_sims <= 20000:
                                        break
                                    else:
                                        print(
                                            "Please enter a number between 500 and 20000."
                                        )
                                except ValueError:
                                    print("Please enter a valid number.")

                            # Get max depth
                            while True:
                                try:
                                    max_depth = int(
                                        input(
                                            "Enter maximum search depth for MCTS (5-50, default: 10)"
                                        )
                                    )
                                    if 5 <= max_depth <= 50:
                                        break
                                    else:
                                        print("Please enter a number between 5 and 50.")
                                except ValueError:
                                    print("Please enter a valid number.")
                        else:
                            # Use default parameters
                            num_sims = default_num_sims
                            max_depth = default_max_depth
                            print(
                                "Using default MCTS parameters (3000 sims, 10 depth)."
                            )
                        break
                    else:
                        print("Please enter 'y' or 'n'.")
                except ValueError:
                    print("Please enter 'y' or 'n'.")

            # Store MCTS parameters for this player
            player_name = f"Player {i + 1}"
            mcts_params[player_name] = {"num_sims": num_sims, "max_depth": max_depth}

        # Create player
        player_name = f"Player {i + 1}"
        player = Player(
            name=player_name,
            remaining_trains=45,
            train_cards={colour: 0 for colour in Colour},
            destinations=[],
            claimed_connections=[],
            points=0,
            turn=1,
            winner=False,
            wins=0,
        )
        players.append(player)
        player_agents[player_name] = agent_type  # Store the agent type

    while True:
        try:
            num_games = int(
                input(
                    "How many games do you want to play with these settings? (1-100): "
                )
            )
            if 1 <= num_games <= 100:
                break
            else:
                print("Please enter a number between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")

    print("\n" + "_" * 200 + "\n")

    player_stats = {}  # Store results for player
    for player in players:
        player_stats[player.name] = []

    for i in range(num_games):
        print(f"\nStarting Game {i + 1}...")

        # Reset players
        for player in players:
            player.remaining_trains = 45
            player.train_cards = {colour: 0 for colour in Colour}
            player.destinations = []
            player.claimed_connections = []
            player.claimed_cities = set()
            player.uf = None
            player.points = 0
            player.turn = 1
            player.winner = False

        # Set up and start the game
        game = GameEngine()
        if gui_available and use_gui:
            initialise_gui()
        game.map_type = chosen_map_type
        game.init(players)
        game.player_agents = player_agents
        game.agent_options = agent_options

        if gui_available and use_gui:
            update_game_state(game)  # Populate board
            time.sleep(0.5)
        # Main game loop
        while not game.is_end():
            game.routes_cache_valid = {player.name: False for player in game.players}

            current_player = game.players[game.current_player_idx]
            agent_type = player_agents[current_player.name]

            print(
                f"\n{current_player.name} ({agent_options[agent_type]}) Turn: {current_player.turn}"
            )
            tst = time.time()

            # Handle first turn destination selection
            if current_player.turn == 1:
                destinations = game.select_initial_destinations(current_player)
                game.remove_destination_tickets(current_player, destinations)

            # Execute agent-specific logic using match-case
            match agent_type:
                case 1:  # Human Player
                    print("You can type back to go to the previous menu option")
                    player = PlayerController(game)
                    best_action = player.play_turn(current_player)
                case 2:  # MCTS AI
                    # Get player-specific MCTS parameters or use defaults
                    if current_player.name in mcts_params:
                        params = mcts_params[current_player.name]
                        num_sims = params["num_sims"]
                        max_depth = params["max_depth"]
                        print(
                            f"Using MCTS parameters: {num_sims} simulations, max depth {max_depth}"
                        )
                    else:
                        num_sims = default_num_sims
                        max_depth = default_max_depth

                    mcts_player = MCTS(game)
                    best_action = mcts_player.best_action(num_sims, max_depth)
                case 3:  # MCTS Rollouts AI
                    # Get player-specific MCTS parameters or use defaults
                    if current_player.name in mcts_params:
                        params = mcts_params[current_player.name]
                        num_sims = params["num_sims"]
                        max_depth = params["max_depth"]
                        print(
                            f"Using MCTS parameters: {num_sims} simulations, max depth {max_depth}"
                        )
                    else:
                        num_sims = default_num_sims
                        max_depth = default_max_depth

                    mcts_player = MCTS_rollouts(game)
                    best_action = mcts_player.best_action(num_sims, max_depth)
                case 4:  # MCTS Selection AI
                    # Get player-specific MCTS parameters or use defaults
                    if current_player.name in mcts_params:
                        params = mcts_params[current_player.name]
                        num_sims = params["num_sims"]
                        max_depth = params["max_depth"]
                        print(
                            f"Using MCTS parameters: {num_sims} simulations, max depth {max_depth}"
                        )
                    else:
                        num_sims = default_num_sims
                        max_depth = default_max_depth

                    mcts_player = MCTS_selection(game)
                    best_action = mcts_player.best_action(num_sims, max_depth)
                case 5:  # MCTS Untuned AI
                    # Get player-specific MCTS parameters or use defaults
                    if current_player.name in mcts_params:
                        params = mcts_params[current_player.name]
                        num_sims = params["num_sims"]
                        max_depth = params["max_depth"]
                        print(
                            f"Using MCTS parameters: {num_sims} simulations, max depth {max_depth}"
                        )
                    else:
                        num_sims = default_num_sims
                        max_depth = default_max_depth

                    mcts_player = MCTS_no_heuristics(game)
                    best_action = mcts_player.best_action(num_sims, max_depth)
                case 6:  # Destination Heuristic AI
                    heuristic_player = DestinationHeuristic(game)
                    best_action = heuristic_player.choose_action()
                case 7:  # Longest Route Heuristic AI
                    heuristic_player = LongestRouteHeuristic(game)
                    best_action = heuristic_player.choose_action()
                case 8:  # Best Move Heuristic AI
                    heuristic_player = BestMoveHeuristic(game)
                    best_action = heuristic_player.choose_action()
                case 9:  # ShaoPlayer AI
                    heuristic_player = ShaoHeuristic(game)
                    best_action = heuristic_player.choose_action()
                case 10:  # Random AI
                    heuristic_player = RandomHeuristic(game)
                    best_action = heuristic_player.choose_action()

            if best_action is None:
                if current_player.remaining_trains == 3:
                    print(
                        f"{current_player.name} has no valid actions and 3 trains left. Ending game."
                    )
                    current_player.remaining_trains -= 1
                else:
                    print(f"{current_player.name} has no valid actions. Ending turn.")
                pass
            # Apply the action and update game state
            game.apply_action_final(best_action)
            game.update_player_turn()
            if gui_available and use_gui:
                update_game_state(game, best_action)
            current_player.turn += 1
            tet = time.time()
            print(f"Time taken for turn: {(tet - tst):.4f} seconds")

        # Calculate final scores
        players_final = game.game_result_final(i + 1)
        # Store results for this game
        for player in players_final:
            player_stats[player.name].append(copy.deepcopy(player))

        timeend = time.time()
        elapsed_time = timeend - timestart
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        print(f"Time taken: {minutes} minutes and {seconds} seconds")

    # Enhanced statistics tracking
    if gui_available and use_gui:
        shutdown()

    # Initialise stats
    player_statistics = {}
    for player in players:
        player_statistics[player.name] = {
            "games_played": num_games,
            "wins": 0,
            "total_score": 0,
            "total_completed_destinations": 0,
            "total_incomplete_destinations": 0,
            "total_leftover_trains": 0,
            "total_turns": 0,
            "agent_type": agent_options[
                player_agents[player.name]
            ],  # Store agent type description
        }

    # Process game results
    for i in range(num_games):
        print(f"\nGame {i + 1} Results:")

        # Track game-wide total turns for average calculation later
        game_total_turns = 0

        for player_name, player_results in player_stats.items():
            if i < len(player_results):  # Make sure we have data for this game
                player = player_results[i]
                stats = player_statistics[player_name]
                agent_type = agent_options[player_agents[player_name]]

                # Update statistics
                if player.winner:
                    stats["wins"] += 1
                stats["total_score"] += player.points

                # Calculate destinations completed/incomplete
                completed = 0
                incomplete = 0
                for destination in player.destinations:
                    if player.uf.is_connected(destination.city1, destination.city2):
                        completed += 1
                    else:
                        incomplete += 1

                stats["total_completed_destinations"] += completed
                stats["total_incomplete_destinations"] += incomplete

                # Track leftover trains
                stats["total_leftover_trains"] += player.remaining_trains

                # Track turns
                stats["total_turns"] += player.turn
                game_total_turns += player.turn

                # Display individual game results - now with agent type
                print(f"{player_name} ({agent_type}): {player.points} points")
                print(
                    f"  Destinations completed: {completed}, incomplete: {incomplete}"
                )
                print(f"  Trains left: {player.remaining_trains}")
                print(f"  Turns taken: {player.turn}")

                if player.winner:
                    print(f"  {player_name} wins!")

    # Display comprehensive statistics
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)

    # Calculate average turns per game
    average_turns_per_game = sum(
        [stats["total_turns"] for stats in player_statistics.values()]
    ) / (num_games * len(players))

    for player_name, stats in player_statistics.items():
        win_ratio = stats["wins"] / num_games
        avg_score = stats["total_score"] / num_games
        avg_complete = stats["total_completed_destinations"] / num_games
        avg_incomplete = stats["total_incomplete_destinations"] / num_games
        avg_leftover = stats["total_leftover_trains"] / num_games
        agent_type = stats["agent_type"]

        print(f"\n{player_name} ({agent_type}) Statistics:")
        print(f"  Win Ratio: {win_ratio:.2f} ({stats['wins']}/{num_games})")
        print(f"  Average Score: {avg_score:.2f}")
        print(f"  Average Destinations Completed: {avg_complete:.2f}")
        print(f"  Average Destinations Uncompleted: {avg_incomplete:.2f}")
        print(f"  Average Leftover Trains: {avg_leftover:.2f}")

    print(f"\nAverage Turns Per Game: {average_turns_per_game:.2f}")
    print("=" * 70)

    # Keep the existing best player display, but add agent type
    best_player = max(players, key=lambda p: p.wins)
    best_agent_type = agent_options[player_agents[best_player.name]]
    print(
        f"\nBest player: {best_player.name} ({best_agent_type}) with {best_player.wins} wins!"
    )


if __name__ == "__main__":
    main()
