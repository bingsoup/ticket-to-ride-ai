from helper_classes import Destination, Route, Color
class MapData:
    def __init__(self, map_type):
        self.map_type = map_type
    
    def get_destinations(self):
        if self.map_type == "USA":
            return self.american_destinations()
        elif self.map_type == "Europe":
            return self.european_destinations()
    
    def get_routes(self):
        if self.map_type == "USA":
            return self.american_routes()
        elif self.map_type == "Europe":
            return self.european_routes()

    def american_destinations(self):
        destinations = [
            Destination("Denver", "El Paso", 4),
            Destination("Kansas City", "Houston", 5),
            Destination("New York", "Atlanta", 6),
            Destination("Calgary", "Salt Lake City", 7),
            Destination("Chicago", "New Orleans", 7),
            Destination("Duluth", "Houston", 8),
            Destination("Helena", "Los Angeles", 8),
            Destination("Sault St. Marie", "Nashville", 8),
            Destination("Sault St. Marie", "Oklahoma City", 9),
            Destination("Chicago", "Santa Fe", 9),
            Destination("Montreal", "Atlanta", 9),
            Destination("Seattle", "Los Angeles", 9),
            Destination("Duluth", "El Paso", 10),
            Destination("Toronto", "Miami", 10),
            Destination("Dallas", "New York", 11),
            Destination("Denver", "Pittsburgh", 11),
            Destination("Portland", "Phoenix", 11),
            Destination("Winnipeg", "Little Rock", 11),
            Destination("Boston", "Miami", 12),
            Destination("Winnipeg", "Houston", 12),
            Destination("Calgary", "Phoenix", 13),
            Destination("Montreal", "New Orleans", 13),
            Destination("Vancouver", "Santa Fe", 13),
            Destination("Los Angeles", "Chicago", 16),
            Destination("Portland", "Nashville", 17),
            Destination("San Francisco", "Atlanta", 17),
            Destination("Los Angeles", "Miami", 20),
            Destination("Vancouver", "Montreal", 20),
            Destination("Los Angeles", "New York", 21),
            Destination("Seattle", "New York", 22)
        ]
        return destinations
    
    def american_routes(self):
        routes = {
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
                    Route(length=1, color=Color.GRAY),
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
        return routes
    
    def european_destinations(self):
        destinations = [
            Destination("Athina", "Angora", 5),
            Destination("Budapest", "Sofia", 5),
            Destination("Frankfurt", "Kobenhavn", 5),
            Destination("Rostov", "Erzurum", 5),
            Destination("Sofia", "Smyrna", 5),
            Destination("Kyiv", "Petrograd", 6),
            Destination("Zurich", "Brindisi", 6),
            Destination("Zurich", "Budapest", 6),
            Destination("Warszawa", "Smolensk", 6),
            Destination("Zagrab", "Brindisi", 6),
            Destination("Paris", "Zagrab", 7),
            Destination("Brest", "Marseille", 7),
            Destination("London", "Berlin", 7),
            Destination("Edinburgh", "Paris", 7),
            Destination("Amsterdam", "Pamplona", 7),
            Destination("Roma", "Smyrna", 8),
            Destination("Palermo", "Constantinople", 8),
            Destination("Sarajevo", "Sevastopol", 8),
            Destination("Madrid", "Dieppe", 8),
            Destination("Barcelona", "Bruxelles", 8),
            Destination("Paris", "Wien", 8),
            Destination("Barcelona", "Munchen", 8),
            Destination("Brest", "Venezia", 8),
            Destination("Smolensk", "Rostov", 8),
            Destination("Marseille", "Essen", 8),
            Destination("Kyiv", "Sochi", 8),
            Destination("Madrid", "Zurich", 8),
            Destination("Berlin", "Bucuresti", 8),
            Destination("Bruxelles", "Danzic", 9),
            Destination("Berlin", "Roma", 9),
            Destination("Angora", "Kharkov", 10),
            Destination("Riga", "Bucuresti", 10),
            Destination("Essen", "Kyiv", 10),
            Destination("Venezia", "Constantinople", 10),
            Destination("London", "Wien", 10),
            Destination("Athina", "Wilno", 11),
            Destination("Stockholm", "Wien", 11),
            Destination("Berlin", "Moskva", 12),
            Destination("Amsterdam", "Wilno", 12),
            Destination("Frankfurt", "Smolensk", 13),
            Destination("Lisboa", "Danzic", 20),
            Destination("Brest", "Petrograd", 20),
            Destination("Palermo", "Moskva", 20),
            Destination("Kobenhavn", "Erzurum", 21),
            Destination("Edinburgh", "Athina", 21),
            Destination("Cadiz", "Stockholm", 21)
        ]
        return destinations
    
    def european_routes(self):
        routes = {
            "London": {
                "Edinburgh": [
                    Route(length=4, color=Color.ORANGE),
                    Route(length=4, color=Color.BLACK)
                ],
                "Dieppe": [
                    Route(length=2, color=Color.GRAY, num_locomotives=1),
                    Route(length=2, color=Color.GRAY, num_locomotives=1)
                ],
                "Amsterdam": [
                    Route(length=2, color=Color.GRAY, num_locomotives=2)
                ]
            },
            "Edinburgh": {
                "London": [
                    Route(length=4, color=Color.ORANGE),
                    Route(length=4, color=Color.BLACK)
                ]
            },
            "Dieppe": {
                "Paris": [
                    Route(length=1, color=Color.PINK)
                ],
                "London": [
                    Route(length=2, color=Color.GRAY, num_locomotives=1),
                    Route(length=2, color=Color.GRAY, num_locomotives=1)
                ],
                "Brest": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Bruxelles": [
                    Route(length=2, color=Color.GREEN)
                ]
            },
            "Brest": {
                "Paris": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Pamplona": [
                    Route(length=4, color=Color.PINK)
                ],
                "Dieppe": [
                    Route(length=2, color=Color.ORANGE)
                ]
            },
            "Pamplona": {
                "Barcelona": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Marseille": [
                    Route(length=4, color=Color.RED)
                ],
                "Madrid": [
                    Route(length=3, color=Color.BLACK, tunnel=True),
                    Route(length=3, color=Color.WHITE, tunnel=True)
                ],
                "Brest": [
                    Route(length=4, color=Color.PINK)
                ],
                "Paris": [
                    Route(length=4, color=Color.BLUE),
                    Route(length=4, color=Color.GREEN)
                ]
            },
            "Madrid": {
                "Pamplona": [
                    Route(length=3, color=Color.BLACK, tunnel=True),
                    Route(length=3, color=Color.WHITE, tunnel=True)
                ],
                "Cadiz": [
                    Route(length=3, color=Color.ORANGE)
                ],
                "Lisboa": [
                    Route(length=3, color=Color.PINK)
                ],
                "Barcelona": [
                    Route(length=2, color=Color.YELLOW)
                ]
            },
            "Cadiz": {
                "Madrid": [
                    Route(length=3, color=Color.ORANGE)
                ],
                "Lisboa": [
                    Route(length=2, color=Color.BLUE)
                ]
            },
            "Lisboa": {
                "Cadiz": [
                    Route(length=2, color=Color.BLUE)
                ],
                "Madrid": [
                    Route(length=3, color=Color.PINK)
                ]
            },
            "Barcelona": {
                "Pamplona": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Madrid": [
                    Route(length=2, color=Color.YELLOW)
                ],
                "Marseille": [
                    Route(length=4, color=Color.GRAY)
                ]
            },
            "Marseille": {
                "Pamplona": [
                    Route(length=4, color=Color.RED)
                ],
                "Barcelona": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Paris": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Zurich": [
                    Route(length=2, color=Color.PINK, tunnel=True)
                ],
                "Roma": [
                    Route(length=4, color=Color.GRAY, tunnel=True)
                ]
            },
            "Paris": {
                "Dieppe": [
                    Route(length=1, color=Color.PINK)
                ],
                "Brest": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Pamplona": [
                    Route(length=4, color=Color.BLUE),
                    Route(length=4, color=Color.GREEN)
                ],
                "Marseille": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Bruxelles": [
                    Route(length=2, color=Color.YELLOW),
                    Route(length=2, color=Color.RED)
                ],
                "Frankfurt": [
                    Route(length=3, color=Color.WHITE),
                    Route(length=3, color=Color.ORANGE)
                ],
                "Zurich": [
                    Route(length=3, color=Color.GRAY, tunnel=True)
                ]
            },
            "Bruxelles": {
                "Paris": [
                    Route(length=2, color=Color.YELLOW),
                    Route(length=2, color=Color.RED)
                ],
                "Frankfurt": [
                    Route(length=2, color=Color.PINK)
                ],
                "Dieppe": [
                    Route(length=2, color=Color.GREEN)
                ],
                "Amsterdam": [
                    Route(length=1, color=Color.BLACK)
                ]
            },
            "Amsterdam": {
                "Bruxelles": [
                    Route(length=1, color=Color.BLACK)
                ],
                "Essen": [
                    Route(length=3, color=Color.YELLOW)
                ],
                "London": [
                    Route(length=2, color=Color.GRAY, num_locomotives=2)
                ],
                "Frankfurt": [
                    Route(length=2, color=Color.WHITE)
                ]
            },
            "Frankfurt": {
                "Bruxelles": [
                    Route(length=2, color=Color.PINK)
                ],
                "Paris": [
                    Route(length=3, color=Color.WHITE),
                    Route(length=3, color=Color.ORANGE)
                ],
                "Munchen": [
                    Route(length=2, color=Color.PINK)
                ],
                "Berlin": [
                    Route(length=3, color=Color.BLACK),
                    Route(length=3, color=Color.RED)
                ],
                "Essen": [
                    Route(length=2, color=Color.GREEN)
                ],
                "Amsterdam": [
                    Route(length=2, color=Color.WHITE)
                ]
            },
            "Zurich": {
                "Paris": [
                    Route(length=3, color=Color.GRAY, tunnel=True)
                ],
                "Munchen": [
                    Route(length=2, color=Color.YELLOW, tunnel=True)
                ],
                "Venezia": [
                    Route(length=2, color=Color.GREEN, tunnel=True)
                ],
                "Marseille": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ]
            },
            "Essen": {
                "Amsterdam": [
                    Route(length=3, color=Color.YELLOW)
                ],
                "Frankfurt": [
                    Route(length=2, color=Color.GREEN)
                ],
                "Berlin": [
                    Route(length=2, color=Color.BLUE)
                ],
                "Kobenhavn": [
                    Route(length=3, color=Color.GRAY, num_locomotives=1)
                ]
            },
            "Kobenhavn": {
                "Essen": [
                    Route(length=3, color=Color.GRAY, num_locomotives=1)
                ],
                "Stockholm": [
                    Route(length=3, color=Color.YELLOW),
                    Route(length=3, color=Color.WHITE)
                ]
            },
            "Stockholm": {
                "Kobenhavn": [
                    Route(length=3, color=Color.YELLOW),
                    Route(length=3, color=Color.WHITE)
                ],
                "Petrograd": [
                    Route(length=8, color=Color.GRAY, tunnel=True)
                ]
            },
            "Berlin": {
                "Essen": [
                    Route(length=2, color=Color.BLUE)
                ],
                "Frankfurt": [
                    Route(length=3, color=Color.BLACK),
                    Route(length=3, color=Color.RED)
                ],
                "Wien": [
                    Route(length=3, color=Color.GREEN)
                ],
                "Warszawa": [
                    Route(length=4, color=Color.PINK),
                    Route(length=4, color=Color.YELLOW)
                ],
                "Danzic": [
                    Route(length=4, color=Color.GRAY)
                ]
            },
            "Wien": {
                "Berlin": [
                    Route(length=3, color=Color.GREEN)
                ],
                "Munchen": [
                    Route(length=3, color=Color.ORANGE)
                ],
                "Zagrab": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Budapest": [
                    Route(length=1, color=Color.WHITE),
                    Route(length=1, color=Color.RED)
                ],
                "Warszawa": [
                    Route(length=4, color=Color.BLUE)
                ]
            },
            "Munchen": {
                "Frankfurt": [
                    Route(length=2, color=Color.PINK)
                ],
                "Zurich": [
                    Route(length=2, color=Color.YELLOW, tunnel=True)
                ],
                "Wien": [
                    Route(length=3, color=Color.ORANGE)
                ],
                "Venezia": [
                    Route(length=2, color=Color.BLUE, tunnel=True)
                ]
            },
            "Venezia": {
                "Zurich": [
                    Route(length=2, color=Color.GREEN, tunnel=True)
                ],
                "Munchen": [
                    Route(length=2, color=Color.BLUE, tunnel=True)
                ],
                "Roma": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Zagrab": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Roma": {
                "Venezia": [
                    Route(length=2, color=Color.BLACK)
                ],
                "Marseille": [
                    Route(length=4, color=Color.GRAY, tunnel=True)
                ],
                "Palermo": [
                    Route(length=4, color=Color.GRAY, num_locomotives=1)
                ],
                "Brindisi": [
                    Route(length=2, color=Color.WHITE)
                ]
            },
            "Palermo": {
                "Roma": [
                    Route(length=4, color=Color.GRAY, num_locomotives=1)
                ],
                "Brindisi": [
                    Route(length=3, color=Color.GRAY, num_locomotives=1)
                ],
                "Smyrna": [
                    Route(length=6, color=Color.GRAY, num_locomotives=2)
                ]
            },
            "Brindisi": {
                "Palermo": [
                    Route(length=3, color=Color.GRAY, num_locomotives=1)
                ],
                "Roma": [
                    Route(length=2, color=Color.WHITE)
                ],
                "Athina": [
                    Route(length=4, color=Color.GRAY, num_locomotives=1)
                ]
            },
            "Zagrab": {
                "Venezia": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Wien": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Sarajevo": [
                    Route(length=3, color=Color.RED)
                ],
                "Budapest": [
                    Route(length=2, color=Color.ORANGE)
                ]
            },
            "Budapest": {
                "Zagrab": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Wien": [
                    Route(length=1, color=Color.WHITE),
                    Route(length=1, color=Color.RED)
                ],
                "Sarajevo": [
                    Route(length=3, color=Color.PINK)
                ],
                "Bucuresti": [
                    Route(length=4, color=Color.GRAY, tunnel=True)
                ],
                "Kyiv": [
                    Route(length=6, color=Color.GRAY, tunnel=True)
                ]
            },
            "Sarajevo": {
                "Zagrab": [
                    Route(length=3, color=Color.RED)
                ],
                "Budapest": [
                    Route(length=3, color=Color.PINK)
                ],
                "Athina": [
                    Route(length=4, color=Color.GREEN)
                ],
                "Sofia": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ]
            },
            "Athina": {
                "Sarajevo": [
                    Route(length=4, color=Color.GREEN)
                ],
                "Sofia": [
                    Route(length=3, color=Color.PINK)
                ],
                "Brindisi": [
                    Route(length=4, color=Color.GRAY, num_locomotives=1)
                ],
                "Smyrna": [
                    Route(length=2, color=Color.GRAY, num_locomotives=1)
                ]
            },
            "Sofia": {
                "Athina": [
                    Route(length=3, color=Color.PINK)
                ],
                "Sarajevo": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Bucuresti": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=3, color=Color.BLUE)
                ]
            },
            "Smyrna": {
                "Athina": [
                    Route(length=2, color=Color.GRAY, num_locomotives=1)
                ],
                "Palermo": [
                    Route(length=6, color=Color.GRAY, num_locomotives=2)
                ],
                "Angora": [
                    Route(length=3, color=Color.ORANGE, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ]
            },
            "Angora": {
                "Smyrna": [
                    Route(length=3, color=Color.ORANGE, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Erzurum": [
                    Route(length=3, color=Color.BLACK)
                ]
            },
            "Constantinople": {
                "Smyrna": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Angora": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Sofia": [
                    Route(length=3, color=Color.BLUE)
                ],
                "Bucuresti": [
                    Route(length=3, color=Color.YELLOW)
                ],
                "Sevastopol": [
                    Route(length=4, color=Color.GRAY, num_locomotives=2)
                ]
            },
            "Erzurum": {
                "Angora": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Sevastopol": [
                    Route(length=4, color=Color.GRAY, num_locomotives=2)
                ],
                "Sochi": [
                    Route(length=3, color=Color.RED, tunnel=True)
                ]
            },
            "Sevastopol": {
                "Erzurum": [
                    Route(length=4, color=Color.GRAY, num_locomotives=2)
                ],
                "Constantinople": [
                    Route(length=4, color=Color.GRAY, num_locomotives=2)
                ],
                "Bucuresti": [
                    Route(length=4, color=Color.WHITE)
                ],
                "Sochi": [
                    Route(length=2, color=Color.GRAY, num_locomotives=1)
                ],
                "Rostov": [
                    Route(length=4, color=Color.GRAY)
                ]
            },
            "Sochi": {
                "Sevastopol": [
                    Route(length=2, color=Color.GRAY, num_locomotives=1)
                ],
                "Erzurum": [
                    Route(length=3, color=Color.RED, tunnel=True)
                ],
                "Rostov": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Rostov": {
                "Sevastopol": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Sochi": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Kharkov": [
                    Route(length=2, color=Color.GREEN)
                ]
            },
            "Bucuresti": {
                "Sofia": [
                    Route(length=2, color=Color.GRAY, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=3, color=Color.YELLOW)
                ],
                "Budapest": [
                    Route(length=4, color=Color.GRAY, tunnel=True)
                ],
                "Kyiv": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Sevastopol": [
                    Route(length=4, color=Color.WHITE)
                ]
            },
            "Kyiv": {
                "Budapest": [
                    Route(length=6, color=Color.GRAY, tunnel=True)
                ],
                "Bucuresti": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Kharkov": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Smolensk": [
                    Route(length=3, color=Color.RED)
                ],
                "Warszawa": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Wilno": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Warszawa": {
                "Kyiv": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Berlin": [
                    Route(length=4, color=Color.PINK),
                    Route(length=4, color=Color.YELLOW)
                ],
                "Wien": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Wilno": [
                    Route(length=3, color=Color.RED)
                ],
                "Danzic": [
                    Route(length=2, color=Color.GRAY)
                ]
            },
            "Kharkov": {
                "Kyiv": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Rostov": [
                    Route(length=2, color=Color.GREEN)
                ],
                "Moskva": [
                    Route(length=4, color=Color.GRAY)
                ]
            },
            "Moskva": {
                "Kharkov": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Smolensk": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Petrograd": [
                    Route(length=4, color=Color.WHITE)
                ]
            },
            "Smolensk": {
                "Moskva": [
                    Route(length=2, color=Color.ORANGE)
                ],
                "Kyiv": [
                    Route(length=3, color=Color.RED)
                ],
                "Wilno": [
                    Route(length=3, color=Color.YELLOW)
                ]
            },
            "Wilno": {
                "Warszawa": [
                    Route(length=3, color=Color.RED)
                ],
                "Kyiv": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Riga": [
                    Route(length=4, color=Color.GREEN)
                ],
                "Petrograd": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Smolensk": [
                    Route(length=3, color=Color.YELLOW)
                ]
            },
            "Danzic":{
                "Warszawa": [
                    Route(length=2, color=Color.GRAY)
                ],
                "Berlin": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Riga": [
                    Route(length=3, color=Color.BLACK)
                ]
            },
            "Riga": {
                "Danzic": [
                    Route(length=3, color=Color.BLACK)
                ],
                "Wilno": [
                    Route(length=4, color=Color.GREEN)
                ],
                "Petrograd": [
                    Route(length=4, color=Color.GRAY)
                ]
            },
            "Petrograd": {
                "Riga": [
                    Route(length=4, color=Color.GRAY)
                ],
                "Wilno": [
                    Route(length=4, color=Color.BLUE)
                ],
                "Moskva": [
                    Route(length=4, color=Color.WHITE)
                ],
                "Stockholm": [
                    Route(length=8, color=Color.GRAY, tunnel=True)
                ]
            }
        }
        return routes