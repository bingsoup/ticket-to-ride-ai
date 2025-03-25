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
        
        # Initialize next matrix for path reconstruction
        self.next = [[-1] * self.n for _ in range(self.n)]
        
        # Initialize direct routes
        for city1 in routes:
            for city2 in routes[city1]:
                for route in routes[city1][city2]:
                    i, j = self.city_idx[city1], self.city_idx[city2]
                    self.dist[i][j] = route.length
                    self.dist[j][i] = route.length  # Undirected graph
                    
                    # Initialize next matrix for direct connections
                    self.next[i][j] = j
                    self.next[j][i] = i
        
        # Self distances are 0
        for i in range(self.n):
            self.dist[i][i] = 0
            self.next[i][i] = i
        
        # Compute shortest paths
        self._compute_shortest_paths()

    def _compute_shortest_paths(self):
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    if self.dist[i][j] > self.dist[i][k] + self.dist[k][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next[i][j] = self.next[i][k]  # Update next matrix

    def get_path(self, city1, city2):
        """
        Returns the list of cities on the shortest path from city1 to city2.
        Returns empty list if no path exists.
        """
        i, j = self.city_idx.get(city1), self.city_idx.get(city2)
        if i is None or j is None or self.dist[i][j] == float('inf'):
            return []
            
        path = [city1]
        while i != j:
            i = self.next[i][j]
            path.append(self.cities[i])
        
        return path
    
    def get_one_off_cities(self, city):
        """Return all cities that are exactly one route away from `city`"""
        idx = self.city_idx.get(city)
        if idx is None:
            return set()
        return {self.cities[j] for j in range(self.n) if self.dist[idx][j] == 2}
    
    def get_distance(self, city1, city2):
        i, j = self.city_idx.get(city1), self.city_idx.get(city2)
        if i is None or j is None:
            return float('inf')
        return self.dist[i][j]