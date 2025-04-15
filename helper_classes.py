from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple

# Disjointed set for efficient connectivity checking, modified to use index matrix   
class UnionFind:
    def __init__(self, cities):
        # Create city index mapping for array access (much faster than dictionary lookups)
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
        # Internal version that works with indices directly
        if self.parent[idx] != idx:
            self.parent[idx] = self.find_idx(self.parent[idx])
        return self.parent[idx]

    def union(self, city1, city2):
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
        # O(1) connectivity check
        idx1 = self.city_to_idx[city1]
        idx2 = self.city_to_idx[city2]
        return self.connected[idx1][idx2]
    
# Destination class to store destination cities and points
@dataclass
class Destination:
    city1: str
    city2: str
    points: int

# Colour enum for train cards
class Colour(Enum):
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
   
# Player class to store player information
@dataclass
class Player:
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
    
    def __post_init__(self):
        if self.train_cards is None:
            self.train_cards = {colour: 0 for colour in Colour}
        if self.destinations is None:
            self.destinations = []
        if self.claimed_connections is None:
            self.claimed_connections = []
        if self.claimed_cities is None:
            self.claimed_cities = set()
        
    def getTrainCards(self) -> List[Tuple[Colour, int]]:
        return [(colour, count) for colour, count in self.train_cards.items() if count > 0]
    
    def getClaimedCity(self,city: str) -> bool:
        return city in self.claimed_cities

@dataclass
class Route:
    length: int
    colour: Colour
    claimed_by: str = None
    tunnel: bool = False
    num_locomotives: int = 0
    
    def claim(self, player: str):
        self.claimed_by = player

    def is_claimed(self) -> bool:
        return self.claimed_by is not None