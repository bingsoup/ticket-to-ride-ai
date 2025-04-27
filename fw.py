class FloydWarshall:
    """
    This class computes and stores all-pairs shortest paths.
    Weighted edges are represented by the Route class.
    """

    def __init__(self, routes):
        """
        Initialize the Floyd-Warshall algorithm with route data.

        Constructs distance and next-hop matrices for path finding and
        distance calculations between all city pairs.

        :param routes: Dictionary mapping source cities to destination cities and their routes. Format: {city1: {city2: [Route objects]}}
        :type routes: Dict[str, Dict[str, List[Route]]]
        """
        self.cities = set()

        # Collect all unique cities
        for city1 in routes:
            self.cities.add(city1)
            for city2 in routes[city1]:
                self.cities.add(city2)

        self.cities = list(self.cities)  # Convert set to list for indexing
        self.n = len(self.cities)
        self.city_idx = {
            city: i for i, city in enumerate(self.cities)
        }  # Map city -> index

        INF = float("inf")
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
        self.compute_shortest_paths()

    def compute_shortest_paths(self):
        """
        Execute the Floyd-Warshall algorithm to compute shortest paths.
        """
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    if self.dist[i][j] > self.dist[i][k] + self.dist[k][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next[i][j] = self.next[i][k]  # Update next matrix

    def get_path(self, city1, city2):
        """
        Returns the list of cities on the shortest path from city1 to city2.

        Uses the next-hop matrix to reconstruct the optimal path between cities.

        :param city1: Starting city name
        :type city1: str
        :param city2: Destination city name
        :type city2: str
        :return: List of city names forming the shortest path (including start and end)
                or empty list if no path exists
        :rtype: List[str]
        """

        i, j = self.city_idx.get(city1), self.city_idx.get(city2)
        if i is None or j is None or self.dist[i][j] == float("inf"):
            return []

        path = [city1]
        while i != j:
            i = self.next[i][j]
            path.append(self.cities[i])  # type: ignore

        return path

    def get_distance(self, city1, city2):
        """
        Returns the length of the shortest path between two cities.

        :param city1: Starting city name
        :type city1: str
        :param city2: Destination city name
        :type city2: str
        :return: Total length of shortest path between cities, or infinity if no path exists
        :rtype: float
        """

        i, j = self.city_idx.get(city1), self.city_idx.get(city2)
        if i is None or j is None:
            return float("inf")
        return self.dist[i][j]
