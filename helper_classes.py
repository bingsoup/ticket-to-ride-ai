from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Tuple


class UnionFind:
    """Disjointed set for efficient connectivity checking, modified to use index matrix"""

    def __init__(self, cities):
        """
        Create all cities and set up the Union-Find structure.

        :param cities: List of city names
        :type cities: List[str]
        """
        # Create local index mapping
        self.city_to_idx = {city: i for i, city in enumerate(cities)}
        self.n = len(cities)

        # Initialize direct connectivity matrix (n*n boolean matrix)
        self.connected = [[False for _ in range(self.n)] for _ in range(self.n)]

        # Set diagonal to True (each city is connected to itself)
        for i in range(self.n):
            self.connected[i][i] = True

        # Standard Union-Find parent array for tracking components
        self.parent = list(range(self.n))

    def find_idx(self, idx):
        """
        Finds an id.

        :param idx: The index of the city to find
        :type idx: int
        """
        if self.parent[idx] != idx:
            self.parent[idx] = self.find_idx(self.parent[idx])
        return self.parent[idx]

    def union(self, city1, city2):
        """
        Union two cities and updates the connectivity matrix.

        :param city1: The first city to union
        :type city1: str
        :param city2: The second city to union
        :type city2: str
        """
        idx1 = self.city_to_idx[city1]
        idx2 = self.city_to_idx[city2]

        root1 = self.find_idx(idx1)
        root2 = self.find_idx(idx2)

        if root1 != root2:
            # Find all cities in each component
            comp1 = set()
            comp2 = set()
            for i in range(self.n):
                i_root = self.find_idx(i)
                if i_root == root1:
                    comp1.add(i)
                elif i_root == root2:
                    comp2.add(i)

            # Merge the smaller component into the larger one
            if len(comp1) < len(comp2):
                self.parent[root1] = root2
                # Update connectivity matrix for all city pairs
                for i in comp1:
                    for j in comp2:
                        self.connected[i][j] = True
                        self.connected[j][i] = True
            else:
                self.parent[root2] = root1
                # Update connectivity matrix for all city pairs
                for i in comp2:
                    for j in comp1:
                        self.connected[i][j] = True
                        self.connected[j][i] = True

    def is_connected(self, city1, city2):
        """
        O(1) connectivity check between two cities.

        :param city1: The first city to check
        :type city1: str
        :param city2: The second city to check
        :type city2: str
        :return: True if the cities are connected, False otherwise
        :rtype: bool
        """
        idx1 = self.city_to_idx[city1]
        idx2 = self.city_to_idx[city2]
        return self.connected[idx1][idx2]


@dataclass
class Destination:
    """Destination class to store destination cities and points"""

    city1: str
    city2: str
    points: int


class Colour(Enum):
    """
    Enum class to store the colours of the routes and train cards.

    :param Enum: Enum class
    :type Enum: Enum
    """

    RED = "Red"
    BLUE = "Blue"
    GREEN = "Green"
    YELLOW = "Yellow"
    BLACK = "Black"
    ORANGE = "Orange"
    WHITE = "White"
    PINK = "Pink"
    GRAY = "Gray"
    WILD = "Wild"


@dataclass
class Player:
    """Dataclass to store player information."""

    name: str
    remaining_trains: int = 45
    train_cards: Dict[Colour, int] = None
    destinations: List[Destination] = None
    claimed_connections: List[Tuple[str, str, Colour]] = None
    claimed_cities: Set[str] = None
    points: int = 0
    turn: int = 1
    winner: bool = False
    wins: int = 0
    uf: UnionFind = None


@dataclass
class Route:
    """Dataclass to store route information."""

    length: int
    colour: Colour
    claimed_by: str = None
    tunnel: bool = False
    num_locomotives: int = 0

    def claim(self, player: str):
        """
        Sets the route to claimed

        :param player: The name of the player who claimed the route
        :type player: str
        """
        self.claimed_by = player

    def is_claimed(self) -> bool:
        """
        Checks if the route is claimed

        :return: True if the route is claimed, False otherwise
        :rtype: bool
        """
        return self.claimed_by is not None
