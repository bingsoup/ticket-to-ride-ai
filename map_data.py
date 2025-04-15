from helper_classes import Destination, Route, Colour
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
                    Route(length=2, colour=Colour.YELLOW),
                    Route(length=2, colour=Colour.RED)
                ],
                "Pittsburgh": [
                    Route(length=2, colour=Colour.WHITE),
                    Route(length=2, colour=Colour.GREEN)
                ],
                "Washington": [
                    Route(length=2, colour=Colour.ORANGE),
                    Route(length=2, colour=Colour.BLACK)
                ],
                "Montreal": [
                    Route(length=3, colour=Colour.BLUE)
                ]
            },
            "Boston": {
                "New York": [
                    Route(length=2, colour=Colour.YELLOW),
                    Route(length=2, colour=Colour.RED)
                ],
                "Montreal": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Pittsburgh": {
                "New York": [
                    Route(length=2, colour=Colour.WHITE),
                    Route(length=2, colour=Colour.GREEN)
                ],
                "Washington": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Raleigh": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Nashville": [
                    Route(length=4, colour=Colour.YELLOW)
                ],
                "Saint Louis": [
                    Route(length=5, colour=Colour.GREEN)
                ],
                "Toronto": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Washington": {
                "New York": [
                    Route(length=2, colour=Colour.ORANGE),
                    Route(length=2, colour=Colour.BLACK)
                ],
                "Raleigh": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Pittsburgh": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Montreal": {
                "Boston": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Toronto": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "New York": [
                    Route(length=3, colour=Colour.BLUE)
                ],
                "Sault St. Marie": [
                    Route(length=5, colour=Colour.BLACK)
                ]
            },
            "Toronto": {
                "Montreal": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "Pittsburgh": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Chicago": [
                    Route(length=4, colour=Colour.WHITE)
                ],
                "Sault St. Marie": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Duluth": [
                    Route(length=6, colour=Colour.PINK)
                ]
            },
            "Raleigh": {
                "Washington": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Pittsburgh": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Charleston": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Atlanta": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Nashville": [
                    Route(length=3, colour=Colour.BLACK)
                ]
            },
            "Charleston": {
                "Raleigh": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Atlanta": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Miami": [
                    Route(length=4, colour=Colour.PINK)
                ]
            },
            "Atlanta": {
                "Raleigh": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Charleston": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Nashville": [
                    Route(length=1, colour=Colour.GRAY)
                ],
                "Miami": [
                    Route(length=5, colour=Colour.BLUE)
                ],
                "New Orleans": [
                    Route(length=4, colour=Colour.YELLOW),
                    Route(length=4, colour=Colour.ORANGE)
                ]
            },
            "Nashville": {
                "Pittsburgh": [
                    Route(length=4, colour=Colour.YELLOW)
                ],
                "Atlanta": [
                    Route(length=1, colour=Colour.GRAY)
                ],
                "Saint Louis": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Raleigh": [
                    Route(length=3, colour=Colour.BLACK)
                ],
                "Little Rock": [
                    Route(length=3, colour=Colour.WHITE)
                ]
            },
            "Saint Louis": {
                "Pittsburgh": [
                    Route(length=5, colour=Colour.GREEN)
                ],
                "Nashville": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Kansas City": [
                    Route(length=2, colour=Colour.BLUE),
                    Route(length=2, colour=Colour.PINK)
                ],
                "Chicago": [
                    Route(length=2, colour=Colour.GREEN),
                    Route(length=2, colour=Colour.WHITE)
                ],
                "Little Rock": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Chicago": {
                "Saint Louis": [
                    Route(length=2, colour=Colour.GREEN),
                    Route(length=2, colour=Colour.WHITE)
                ],
                "Pittsburgh": [
                    Route(length=3, colour=Colour.ORANGE),
                    Route(length=3, colour=Colour.BLACK)
                ],
                "Toronto": [
                    Route(length=4, colour=Colour.WHITE)
                ],
                "Omaha": [
                    Route(length=4, colour=Colour.BLUE)
                ],
                "Duluth": [
                    Route(length=3, colour=Colour.RED)
                ]
            },
            "Kansas City": {
                "Saint Louis": [
                    Route(length=2, colour=Colour.BLUE),
                    Route(length=2, colour=Colour.PINK)
                ],
                "Oklahoma City": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Denver": [
                    Route(length=4, colour=Colour.BLACK),
                    Route(length=4, colour=Colour.ORANGE)
                ],
                "Omaha": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ]
            },
            "Oklahoma City": {
                "Kansas City": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Dallas": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Little Rock": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Santa Fe": [
                    Route(length=3, colour=Colour.BLUE)
                ],
                "El Paso": [
                    Route(length=5, colour=Colour.YELLOW)
                ],
                "Denver": [
                    Route(length=4, colour=Colour.RED)
                ]
            },
            "Dallas": {
                "Oklahoma City": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Little Rock": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Houston": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ],
                "El Paso": [
                    Route(length=4, colour=Colour.RED)
                ]
            },
            "Little Rock": {
                "Oklahoma City": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Dallas": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Saint Louis": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "New Orleans": [
                    Route(length=3, colour=Colour.GREEN)
                ],
                "Nashville": [
                    Route(length=3, colour=Colour.WHITE)
                ]
            },
            "Houston": {
                "Dallas": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ],
                "New Orleans": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "El Paso": [
                    Route(length=6, colour=Colour.GREEN)
                ]
            },
            "New Orleans": {
                "Little Rock": [
                    Route(length=3, colour=Colour.GREEN)
                ],
                "Houston": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Miami": [
                    Route(length=6, colour=Colour.RED)
                ],
                "Atlanta": [
                    Route(length=4, colour=Colour.YELLOW),
                    Route(length=4, colour=Colour.ORANGE)
                ]
            },
            "Miami": {
                "Atlanta": [
                    Route(length=5, colour=Colour.BLUE)
                ],
                "New Orleans": [
                    Route(length=6, colour=Colour.RED)
                ],
                "Charleston": [
                    Route(length=4, colour=Colour.PINK)
                ]
            },
            "Denver": {
                "Kansas City": [
                    Route(length=4, colour=Colour.BLACK),
                    Route(length=4, colour=Colour.ORANGE)
                ],
                "Oklahoma City": [
                    Route(length=4, colour=Colour.RED)
                ],
                "Santa Fe": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Phoenix": [
                    Route(length=5, colour=Colour.WHITE)
                ],
                "Salt Lake City": [
                    Route(length=3, colour=Colour.RED),
                    Route(length=3, colour=Colour.YELLOW)
                ],
                "Helena": [
                    Route(length=4, colour=Colour.GREEN)
                ],
                "Omaha": [
                    Route(length=4, colour=Colour.PINK)
                ]
            },
            "Santa Fe": {
                "Denver": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Oklahoma City": [
                    Route(length=3, colour=Colour.BLUE)
                ],
                "Phoenix": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "El Paso": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Phoenix": {
                "Santa Fe": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "Denver": [
                    Route(length=5, colour=Colour.WHITE)
                ],
                "Los Angeles": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "El Paso": [
                    Route(length=3, colour=Colour.GRAY)
                ]
            },
            "El Paso": {
                "Phoenix": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "Santa Fe": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Houston": [
                    Route(length=6, colour=Colour.GREEN)
                ],
                "Dallas": [
                    Route(length=4, colour=Colour.RED)
                ],
                "Oklahoma City": [
                    Route(length=5, colour=Colour.YELLOW)
                ],
                "Los Angeles": [
                    Route(length=6, colour=Colour.BLACK)
                ]
            },
            "Salt Lake City": {
                "Denver": [
                    Route(length=3, colour=Colour.RED),
                    Route(length=3, colour=Colour.YELLOW)
                ],
                "Helena": [
                    Route(length=3, colour=Colour.PINK)
                ],
                "Las Vegas": [
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "San Francisco": [
                    Route(length=5, colour=Colour.ORANGE),
                    Route(length=5, colour=Colour.WHITE)
                ],
                "Portland": [
                    Route(length=6, colour=Colour.BLUE)
                ]
            },
            "Helena": {
                "Salt Lake City": [
                    Route(length=3, colour=Colour.PINK)
                ],
                "Denver": [
                    Route(length=4, colour=Colour.GREEN)
                ],
                "Omaha": [
                    Route(length=5, colour=Colour.RED)
                ],
                "Duluth": [
                    Route(length=6, colour=Colour.ORANGE)
                ],
                "Winnipeg": [
                    Route(length=4, colour=Colour.BLUE)
                ],
                "Calgary": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Seattle": [
                    Route(length=6, colour=Colour.YELLOW)
                ]
            },
            "Omaha": {
                "Chicago": [
                    Route(length=4, colour=Colour.BLUE)
                ],
                "Kansas City": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ],
                "Denver": [
                    Route(length=4, colour=Colour.PINK)
                ],
                "Helena": [
                    Route(length=5, colour=Colour.RED)
                ],
                "Duluth": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Duluth": {
                "Chicago": [
                    Route(length=3, colour=Colour.RED)
                ],
                "Omaha": [
                    Route(length=2, colour=Colour.GRAY),
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Helena": [
                    Route(length=6, colour=Colour.ORANGE)
                ],
                "Winnipeg": [
                    Route(length=4, colour=Colour.BLACK)
                ],
                "Sault St. Marie": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "Toronto": [
                    Route(length=6, colour=Colour.PINK)
                ]
            },
            "Winnipeg": {
                "Duluth": [
                    Route(length=4, colour=Colour.BLACK)
                ],
                "Helena": [
                    Route(length=4, colour=Colour.BLUE)
                ],
                "Sault St. Marie": [
                    Route(length=6, colour=Colour.GRAY)
                ],
                "Calgary": [
                    Route(length=6, colour=Colour.WHITE)
                ]
            },
            "Sault St. Marie": {
                "Duluth": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "Winnipeg": [
                    Route(length=6, colour=Colour.GRAY)
                ],
                "Toronto": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Montreal": [
                    Route(length=5, colour=Colour.BLACK)
                ]
            },
            "Las Vegas": {
                "Salt Lake City": [
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "Los Angeles": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Los Angeles": {
                "Las Vegas": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Phoenix": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "El Paso": [
                    Route(length=6, colour=Colour.BLACK)
                ],
                "San Francisco": [
                    Route(length=3, colour=Colour.PINK),
                    Route(length=3, colour=Colour.YELLOW)
                ]
            },
            "San Francisco": {
                "Salt Lake City": [
                    Route(length=5, colour=Colour.ORANGE),
                    Route(length=5, colour=Colour.WHITE)
                ],
                "Los Angeles": [
                    Route(length=3, colour=Colour.PINK),
                    Route(length=3, colour=Colour.YELLOW)
                ],
                "Portland": [
                    Route(length=5, colour=Colour.GREEN),
                    Route(length=5, colour=Colour.PINK)
                ]
            },
            "Portland": {
                "San Francisco": [
                    Route(length=5, colour=Colour.GREEN),
                    Route(length=5, colour=Colour.PINK)
                ],
                "Seattle": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ],
                "Salt Lake City": [
                    Route(length=6, colour=Colour.BLUE)
                ]
            },
            "Seattle": {
                "Portland": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ],
                "Helena": [
                    Route(length=6, colour=Colour.YELLOW)
                ],
                "Calgary": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Vancouver": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ]
            },
            "Vancouver": {
                "Seattle": [
                    Route(length=1, colour=Colour.GRAY),
                    Route(length=1, colour=Colour.GRAY)
                ],
                "Calgary": [
                    Route(length=3, colour=Colour.GRAY)
                ]
            },
            "Calgary": {
                "Vancouver": [
                    Route(length=3, colour=Colour.GRAY)
                ],
                "Seattle": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Helena": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Winnipeg": [
                    Route(length=6, colour=Colour.WHITE)
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
                    Route(length=4, colour=Colour.ORANGE),
                    Route(length=4, colour=Colour.BLACK)
                ],
                "Dieppe": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1),
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Amsterdam": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=2)
                ]
            },
            "Edinburgh": {
                "London": [
                    Route(length=4, colour=Colour.ORANGE),
                    Route(length=4, colour=Colour.BLACK)
                ]
            },
            "Dieppe": {
                "Paris": [
                    Route(length=1, colour=Colour.PINK)
                ],
                "London": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1),
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Brest": [
                    Route(length=2, colour=Colour.ORANGE)
                ],
                "Bruxelles": [
                    Route(length=2, colour=Colour.GREEN)
                ]
            },
            "Brest": {
                "Paris": [
                    Route(length=3, colour=Colour.BLACK)
                ],
                "Pamplona": [
                    Route(length=4, colour=Colour.PINK)
                ],
                "Dieppe": [
                    Route(length=2, colour=Colour.ORANGE)
                ]
            },
            "Pamplona": {
                "Barcelona": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Marseille": [
                    Route(length=4, colour=Colour.RED)
                ],
                "Madrid": [
                    Route(length=3, colour=Colour.BLACK, tunnel=True),
                    Route(length=3, colour=Colour.WHITE, tunnel=True)
                ],
                "Brest": [
                    Route(length=4, colour=Colour.PINK)
                ],
                "Paris": [
                    Route(length=4, colour=Colour.BLUE),
                    Route(length=4, colour=Colour.GREEN)
                ]
            },
            "Madrid": {
                "Pamplona": [
                    Route(length=3, colour=Colour.BLACK, tunnel=True),
                    Route(length=3, colour=Colour.WHITE, tunnel=True)
                ],
                "Cadiz": [
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "Lisboa": [
                    Route(length=3, colour=Colour.PINK)
                ],
                "Barcelona": [
                    Route(length=2, colour=Colour.YELLOW)
                ]
            },
            "Cadiz": {
                "Madrid": [
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "Lisboa": [
                    Route(length=2, colour=Colour.BLUE)
                ]
            },
            "Lisboa": {
                "Cadiz": [
                    Route(length=2, colour=Colour.BLUE)
                ],
                "Madrid": [
                    Route(length=3, colour=Colour.PINK)
                ]
            },
            "Barcelona": {
                "Pamplona": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Madrid": [
                    Route(length=2, colour=Colour.YELLOW)
                ],
                "Marseille": [
                    Route(length=4, colour=Colour.GRAY)
                ]
            },
            "Marseille": {
                "Pamplona": [
                    Route(length=4, colour=Colour.RED)
                ],
                "Barcelona": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Paris": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Zurich": [
                    Route(length=2, colour=Colour.PINK, tunnel=True)
                ],
                "Roma": [
                    Route(length=4, colour=Colour.GRAY, tunnel=True)
                ]
            },
            "Paris": {
                "Dieppe": [
                    Route(length=1, colour=Colour.PINK)
                ],
                "Brest": [
                    Route(length=3, colour=Colour.BLACK)
                ],
                "Pamplona": [
                    Route(length=4, colour=Colour.BLUE),
                    Route(length=4, colour=Colour.GREEN)
                ],
                "Marseille": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Bruxelles": [
                    Route(length=2, colour=Colour.YELLOW),
                    Route(length=2, colour=Colour.RED)
                ],
                "Frankfurt": [
                    Route(length=3, colour=Colour.WHITE),
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "Zurich": [
                    Route(length=3, colour=Colour.GRAY, tunnel=True)
                ]
            },
            "Bruxelles": {
                "Paris": [
                    Route(length=2, colour=Colour.YELLOW),
                    Route(length=2, colour=Colour.RED)
                ],
                "Frankfurt": [
                    Route(length=2, colour=Colour.PINK)
                ],
                "Dieppe": [
                    Route(length=2, colour=Colour.GREEN)
                ],
                "Amsterdam": [
                    Route(length=1, colour=Colour.BLACK)
                ]
            },
            "Amsterdam": {
                "Bruxelles": [
                    Route(length=1, colour=Colour.BLACK)
                ],
                "Essen": [
                    Route(length=3, colour=Colour.YELLOW)
                ],
                "London": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=2)
                ],
                "Frankfurt": [
                    Route(length=2, colour=Colour.WHITE)
                ]
            },
            "Frankfurt": {
                "Bruxelles": [
                    Route(length=2, colour=Colour.PINK)
                ],
                "Paris": [
                    Route(length=3, colour=Colour.WHITE),
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "Munchen": [
                    Route(length=2, colour=Colour.PINK)
                ],
                "Berlin": [
                    Route(length=3, colour=Colour.BLACK),
                    Route(length=3, colour=Colour.RED)
                ],
                "Essen": [
                    Route(length=2, colour=Colour.GREEN)
                ],
                "Amsterdam": [
                    Route(length=2, colour=Colour.WHITE)
                ]
            },
            "Zurich": {
                "Paris": [
                    Route(length=3, colour=Colour.GRAY, tunnel=True)
                ],
                "Munchen": [
                    Route(length=2, colour=Colour.YELLOW, tunnel=True)
                ],
                "Venezia": [
                    Route(length=2, colour=Colour.GREEN, tunnel=True)
                ],
                "Marseille": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ]
            },
            "Essen": {
                "Amsterdam": [
                    Route(length=3, colour=Colour.YELLOW)
                ],
                "Frankfurt": [
                    Route(length=2, colour=Colour.GREEN)
                ],
                "Berlin": [
                    Route(length=2, colour=Colour.BLUE)
                ],
                "Kobenhavn": [
                    Route(length=3, colour=Colour.GRAY, num_locomotives=1)
                ]
            },
            "Kobenhavn": {
                "Essen": [
                    Route(length=3, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Stockholm": [
                    Route(length=3, colour=Colour.YELLOW),
                    Route(length=3, colour=Colour.WHITE)
                ]
            },
            "Stockholm": {
                "Kobenhavn": [
                    Route(length=3, colour=Colour.YELLOW),
                    Route(length=3, colour=Colour.WHITE)
                ],
                "Petrograd": [
                    Route(length=8, colour=Colour.GRAY, tunnel=True)
                ]
            },
            "Berlin": {
                "Essen": [
                    Route(length=2, colour=Colour.BLUE)
                ],
                "Frankfurt": [
                    Route(length=3, colour=Colour.BLACK),
                    Route(length=3, colour=Colour.RED)
                ],
                "Wien": [
                    Route(length=3, colour=Colour.GREEN)
                ],
                "Warszawa": [
                    Route(length=4, colour=Colour.PINK),
                    Route(length=4, colour=Colour.YELLOW)
                ],
                "Danzic": [
                    Route(length=4, colour=Colour.GRAY)
                ]
            },
            "Wien": {
                "Berlin": [
                    Route(length=3, colour=Colour.GREEN)
                ],
                "Munchen": [
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "Zagrab": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Budapest": [
                    Route(length=1, colour=Colour.WHITE),
                    Route(length=1, colour=Colour.RED)
                ],
                "Warszawa": [
                    Route(length=4, colour=Colour.BLUE)
                ]
            },
            "Munchen": {
                "Frankfurt": [
                    Route(length=2, colour=Colour.PINK)
                ],
                "Zurich": [
                    Route(length=2, colour=Colour.YELLOW, tunnel=True)
                ],
                "Wien": [
                    Route(length=3, colour=Colour.ORANGE)
                ],
                "Venezia": [
                    Route(length=2, colour=Colour.BLUE, tunnel=True)
                ]
            },
            "Venezia": {
                "Zurich": [
                    Route(length=2, colour=Colour.GREEN, tunnel=True)
                ],
                "Munchen": [
                    Route(length=2, colour=Colour.BLUE, tunnel=True)
                ],
                "Roma": [
                    Route(length=2, colour=Colour.BLACK)
                ],
                "Zagrab": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Roma": {
                "Venezia": [
                    Route(length=2, colour=Colour.BLACK)
                ],
                "Marseille": [
                    Route(length=4, colour=Colour.GRAY, tunnel=True)
                ],
                "Palermo": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Brindisi": [
                    Route(length=2, colour=Colour.WHITE)
                ]
            },
            "Palermo": {
                "Roma": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Brindisi": [
                    Route(length=3, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Smyrna": [
                    Route(length=6, colour=Colour.GRAY, num_locomotives=2)
                ]
            },
            "Brindisi": {
                "Palermo": [
                    Route(length=3, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Roma": [
                    Route(length=2, colour=Colour.WHITE)
                ],
                "Athina": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=1)
                ]
            },
            "Zagrab": {
                "Venezia": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Wien": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Sarajevo": [
                    Route(length=3, colour=Colour.RED)
                ],
                "Budapest": [
                    Route(length=2, colour=Colour.ORANGE)
                ]
            },
            "Budapest": {
                "Zagrab": [
                    Route(length=2, colour=Colour.ORANGE)
                ],
                "Wien": [
                    Route(length=1, colour=Colour.WHITE),
                    Route(length=1, colour=Colour.RED)
                ],
                "Sarajevo": [
                    Route(length=3, colour=Colour.PINK)
                ],
                "Bucuresti": [
                    Route(length=4, colour=Colour.GRAY, tunnel=True)
                ],
                "Kyiv": [
                    Route(length=6, colour=Colour.GRAY, tunnel=True)
                ]
            },
            "Sarajevo": {
                "Zagrab": [
                    Route(length=3, colour=Colour.RED)
                ],
                "Budapest": [
                    Route(length=3, colour=Colour.PINK)
                ],
                "Athina": [
                    Route(length=4, colour=Colour.GREEN)
                ],
                "Sofia": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ]
            },
            "Athina": {
                "Sarajevo": [
                    Route(length=4, colour=Colour.GREEN)
                ],
                "Sofia": [
                    Route(length=3, colour=Colour.PINK)
                ],
                "Brindisi": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Smyrna": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1)
                ]
            },
            "Sofia": {
                "Athina": [
                    Route(length=3, colour=Colour.PINK)
                ],
                "Sarajevo": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Bucuresti": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=3, colour=Colour.BLUE)
                ]
            },
            "Smyrna": {
                "Athina": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Palermo": [
                    Route(length=6, colour=Colour.GRAY, num_locomotives=2)
                ],
                "Angora": [
                    Route(length=3, colour=Colour.ORANGE, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ]
            },
            "Angora": {
                "Smyrna": [
                    Route(length=3, colour=Colour.ORANGE, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Erzurum": [
                    Route(length=3, colour=Colour.BLACK)
                ]
            },
            "Constantinople": {
                "Smyrna": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Angora": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Sofia": [
                    Route(length=3, colour=Colour.BLUE)
                ],
                "Bucuresti": [
                    Route(length=3, colour=Colour.YELLOW)
                ],
                "Sevastopol": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=2)
                ]
            },
            "Erzurum": {
                "Angora": [
                    Route(length=3, colour=Colour.BLACK)
                ],
                "Sevastopol": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=2)
                ],
                "Sochi": [
                    Route(length=3, colour=Colour.RED, tunnel=True)
                ]
            },
            "Sevastopol": {
                "Erzurum": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=2)
                ],
                "Constantinople": [
                    Route(length=4, colour=Colour.GRAY, num_locomotives=2)
                ],
                "Bucuresti": [
                    Route(length=4, colour=Colour.WHITE)
                ],
                "Sochi": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Rostov": [
                    Route(length=4, colour=Colour.GRAY)
                ]
            },
            "Sochi": {
                "Sevastopol": [
                    Route(length=2, colour=Colour.GRAY, num_locomotives=1)
                ],
                "Erzurum": [
                    Route(length=3, colour=Colour.RED, tunnel=True)
                ],
                "Rostov": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Rostov": {
                "Sevastopol": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Sochi": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Kharkov": [
                    Route(length=2, colour=Colour.GREEN)
                ]
            },
            "Bucuresti": {
                "Sofia": [
                    Route(length=2, colour=Colour.GRAY, tunnel=True)
                ],
                "Constantinople": [
                    Route(length=3, colour=Colour.YELLOW)
                ],
                "Budapest": [
                    Route(length=4, colour=Colour.GRAY, tunnel=True)
                ],
                "Kyiv": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Sevastopol": [
                    Route(length=4, colour=Colour.WHITE)
                ]
            },
            "Kyiv": {
                "Budapest": [
                    Route(length=6, colour=Colour.GRAY, tunnel=True)
                ],
                "Bucuresti": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Kharkov": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Smolensk": [
                    Route(length=3, colour=Colour.RED)
                ],
                "Warszawa": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Wilno": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Warszawa": {
                "Kyiv": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Berlin": [
                    Route(length=4, colour=Colour.PINK),
                    Route(length=4, colour=Colour.YELLOW)
                ],
                "Wien": [
                    Route(length=4, colour=Colour.BLUE)
                ],
                "Wilno": [
                    Route(length=3, colour=Colour.RED)
                ],
                "Danzic": [
                    Route(length=2, colour=Colour.GRAY)
                ]
            },
            "Kharkov": {
                "Kyiv": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Rostov": [
                    Route(length=2, colour=Colour.GREEN)
                ],
                "Moskva": [
                    Route(length=4, colour=Colour.GRAY)
                ]
            },
            "Moskva": {
                "Kharkov": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Smolensk": [
                    Route(length=2, colour=Colour.ORANGE)
                ],
                "Petrograd": [
                    Route(length=4, colour=Colour.WHITE)
                ]
            },
            "Smolensk": {
                "Moskva": [
                    Route(length=2, colour=Colour.ORANGE)
                ],
                "Kyiv": [
                    Route(length=3, colour=Colour.RED)
                ],
                "Wilno": [
                    Route(length=3, colour=Colour.YELLOW)
                ]
            },
            "Wilno": {
                "Warszawa": [
                    Route(length=3, colour=Colour.RED)
                ],
                "Kyiv": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Riga": [
                    Route(length=4, colour=Colour.GREEN)
                ],
                "Petrograd": [
                    Route(length=4, colour=Colour.BLUE)
                ],
                "Smolensk": [
                    Route(length=3, colour=Colour.YELLOW)
                ]
            },
            "Danzic":{
                "Warszawa": [
                    Route(length=2, colour=Colour.GRAY)
                ],
                "Berlin": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Riga": [
                    Route(length=3, colour=Colour.BLACK)
                ]
            },
            "Riga": {
                "Danzic": [
                    Route(length=3, colour=Colour.BLACK)
                ],
                "Wilno": [
                    Route(length=4, colour=Colour.GREEN)
                ],
                "Petrograd": [
                    Route(length=4, colour=Colour.GRAY)
                ]
            },
            "Petrograd": {
                "Riga": [
                    Route(length=4, colour=Colour.GRAY)
                ],
                "Wilno": [
                    Route(length=4, colour=Colour.BLUE)
                ],
                "Moskva": [
                    Route(length=4, colour=Colour.WHITE)
                ],
                "Stockholm": [
                    Route(length=8, colour=Colour.GRAY, tunnel=True)
                ]
            }
        }
        return routes