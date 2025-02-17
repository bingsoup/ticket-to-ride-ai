class FloydWarshall:
    def __init__(self, routes):
        self.cities = set()
        
        # Collect all unique cities
        for city1 in routes:
            self.cities.add(city1)
            for city2 in routes[city1]:
                self.cities.add(city2)
        
        self.cities = list(self.cities)  # Convert set to list for indexing
        self.n = len(self.cities)
        self.city_idx = {city: i for i, city in enumerate(self.cities)}  # Map city -> index
        
        INF = float('inf')
        self.dist = [[INF] * self.n for _ in range(self.n)]
        
        # Initialize direct routes (each route has a fixed length of 1, as it's a single route between two cities)
        for city1 in routes:
            for city2 in routes[city1]:
                i, j = self.city_idx[city1], self.city_idx[city2]
                self.dist[i][j] = 1  # All direct connections are treated as length 1
                self.dist[j][i] = 1  # Undirected graph
        
        # Self distances are 0
        for i in range(self.n):
            self.dist[i][i] = 0
        
        # Compute shortest paths
        self._compute_shortest_paths()

    def _compute_shortest_paths(self):
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    self.dist[i][j] = min(self.dist[i][j], self.dist[i][k] + self.dist[k][j])

    def get_one_off_cities(self, city):
        """Return all cities that are exactly one route away from `city`"""
        idx = self.city_idx.get(city)
        if idx is None:
            return set()
        return {self.cities[j] for j in range(self.n) if self.dist[idx][j] == 2}