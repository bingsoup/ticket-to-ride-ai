from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple

# Disjointed set for efficient connectivity checking
class UnionFind:
    def __init__(self, cities):
        self.parent = {city: city for city in cities}
        self.rank = {city: 1 for city in cities}

    def find(self, city):
        if self.parent[city] != city:
            self.parent[city] = self.find(self.parent[city])  # Path compression
        return self.parent[city]

    def union(self, city1, city2):
        root1 = self.find(city1)
        root2 = self.find(city2)
        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1

    def is_connected(self, city1, city2):
        return self.find(city1) == self.find(city2)
        
# Destination class to store destination cities and points
@dataclass
class Destination:
    city1: str
    city2: str
    points: int

# Color enum for train cards
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

# Player class to store player information
@dataclass
class Player:
    name: str
    remaining_trains: int = 45
    train_cards: Dict[Color, int] = None
    destinations: List[Destination] = None
    claimed_connections: List[Tuple[str, str, Color]] = None
    claimed_cities: Set[str] = None
    points: int = 0
    turn: int = 1
    uf: UnionFind = None
    actions = None
    
    def __post_init__(self):
        if self.train_cards is None:
            self.train_cards = {color: 0 for color in Color}
        if self.destinations is None:
            self.destinations = []
        if self.claimed_connections is None:
            self.claimed_connections = []
        if self.claimed_cities is None:
            self.claimed_cities = set()
        
    def getTrainCards(self) -> List[Tuple[Color, int]]:
        return [(color, count) for color, count in self.train_cards.items() if count > 0]
    
    def getClaimedCity(self,city: str) -> bool:
        return city in self.claimed_cities

@dataclass
class Route:
    length: int
    color: Color
    claimed_by: str = None
    tunnel: bool = False
    num_locomotives: int = 0
    

    def claim(self, player: str):
        self.claimed_by = player

    def is_claimed(self) -> bool:
        return self.claimed_by is not None