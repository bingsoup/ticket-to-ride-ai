from helper_classes import Color, Destination, Player, Route
# General game class for player interaction
class TicketToRideGame:
    def __init__(self):
        self.game_state = None
        self.god_mode = False
        
    def print_board(self):
        #self.visualizer = TicketToRideVisualizer(self.game_state)
        #self.visualizer.visualize_game_map()
        print("=== Ticket to Ride Board ===")
        for city1, connections in sorted(self.game_state.routes.items()):
            print(f"\n{city1}:")
            for city2, routes in sorted(connections.items()):
                for route in routes:
                    status = "Claimed by " + route.claimed_by if route.claimed_by else "Available"
                    print(f"  -> {city2} ({route.color} * {route.length}): {status}")
        print("===========================")

    def print_available_routes(self, player: Player):
        unclaimed_routes = self.game_state.get_unclaimed_routes()
        available_routes = []
        
        for city1, city2, route in unclaimed_routes:
            # Check if player has enough cards to claim the route
            if route.color == Color.GRAY:
                for color in Color:
                    if player.train_cards[color] >= route.length:
                        if available_routes.__contains__((city1, city2, route, color)): #if the route is already in the list, skip (avoids duplicates in case of multiple paths /wild cards)
                            continue
                        else:
                            available_routes.append((city1, city2, route, color))
            if player.train_cards[Color.WILD] >= route.length:
                if available_routes.__contains__((city1, city2, route, Color.WILD)):
                    continue
                else:
                    available_routes.append((city1, city2, route, Color.WILD))
            if player.train_cards[route.color] >= route.length:
                if available_routes.__contains__((city1, city2, route, route.color)):
                    continue
                else:
                    available_routes.append((city1, city2, route, route.color))
        if available_routes:
            print("\nRoutes you can complete:")
            for city1, city2, route, color in available_routes:
                print(f"{city1} -> {city2} ({color} * {route.length})")
        else:
            print("\nNo routes available to claim with your current cards.")

    def destination_completion_check(self, player: Player):
        results = self.game_state.check_all_destinations(player)
        
        completed_count = 0
        for destination, is_completed in results:
            status = "completed" if is_completed else "not completed"
            print(f"Destination {destination.city1} to {destination.city2} is {status}")
            if is_completed:
                completed_count += 1
                
        print(f"\nTotal completed destinations: {completed_count}/{len(results)}")
        
    def play_turn(self, player: Player):
        print("\n" + "_" * 200)
        print(f"Turn {player.turn}" + "\n")
        print(f"\n{player.name}'s turn")
        print(f"{player.name}'s train cards: {', '.join(self.formatted_trains(player))}")
        print(f"{player.name}'s destination tickets: {', '.join(self.formatted_destinations(player))}")
        print(f"Face-up cards: {', '.join([card.name for card in self.game_state.face_up_cards])}" + "\n")

        choice = input("<1: Draw Train cards, 2: Claim a route, 3: Draw destination tickets, 4: Print board, 5: Print routes you can complete, 6: Print score, exit: Exit game>\n")

        match choice:
            case "1":
                self.draw_train_cards(player)
            case "2":
                self.handle_claim_route(player)
                if self.god_mode:
                    self.play_turn(player)
            case "3":
                self.draw_destination_tickets(player)
            case "4":
                self.print_board()
                self.play_turn(player)
            case "5":
                self.print_available_routes(player)
                self.play_turn(player)
            case "6":
                print(f"{player.name}'s score: {player.points}")
                self.play_turn(player)
            case "7": 
                self.destination_completion_check(player)
                self.play_turn(player)
            case "godmode":
                self.god_mode = True
                self.game_state.players[0].train_cards[Color.WILD] += 100
                self.game_state.players[1].train_cards[Color.WILD] += 100
                self.play_turn(player)
            case "exit":
                exit()
            case _:
                print("Invalid choice, please try again.")
                self.play_turn(player)
        
    def handle_claim_route(self, player: Player):
        print("Choose a route to claim:")
        city1 = input("Enter the first city: ")
        if city1 == "back":
            self.play_turn(player)
            return
            
        city2 = input("Enter the second city: ")
        if city2 == "back":
            self.play_turn(player)
            return

        routes = self.game_state.get_routes_between_cities(city1, city2)
        if not routes:
            print("No route exists between these cities.")
            self.play_turn(player)
            return

        available_colors = []
        
        route = routes[0]
        if route.claimed_by is None:
            # TODO allow player to use a combination of wild and other colors
            if route.color == Color.GRAY:
                for color in Color:
                    if player.train_cards[color] >= route.length:
                        available_colors.append(color)
            if player.train_cards[route.color] >= route.length:
                available_colors.append(route.color)
            
            if player.train_cards[Color.WILD] >= route.length:
                available_colors.append(Color.WILD)

        if available_colors == []:
            print("You don't have enough cards to claim any routes between these cities.")
            self.play_turn(player)
            return 
        
        if len(available_colors) > 1:
            color = input(f"Choose a color to claim the route ({', '.join([colors.name for colors in available_colors])}): ")
            if color == "back":
                self.play_turn(player)
                return
            for colors in available_colors:
                if color == colors.name:
                    color = colors
            if color not in available_colors:
                print("Invalid color choice, please try again.")
                # TODO probably make a color choice function
                self.handle_claim_route(player)
                return
        else:
            color = available_colors[0]
        if self.game_state.claim_route(city1, city2, color, player.name):
            # Remove cards from player's hand
            route_length = self.game_state.get_route_length(city1, city2)
            if color == Color.WILD:
                player.train_cards[Color.WILD] -= route_length
            else:
                player.train_cards[color] -= route_length
            player.claimed_connections.append((city1, city2, color))
            player.claimed_cities.add(city1)
            player.claimed_cities.add(city2)
            player.points += self.game_state.calc_route_points(route_length)
            print(f"{player.name} has claimed the route between {city1} and {city2} with {color}")
            player.uf.union(city1, city2)
        else:
            print("Failed to claim route.")
            self.play_turn(player)

    def draw_train_cards(self, player: Player):
        drawn = 0
        while drawn < 2:
            # TODO only allow play to pick up 1 card if they take a wild card, disallow from taking a wild as second card
            choice = input("Would you like to draw from the face-up cards? (y/n)")
            match choice:
                case "y":
                    print("Choose a card to draw:")
                    for i, card in enumerate(self.game_state.face_up_cards):
                        print(f"{i+1}: {card.name}")
                    card_choice = int(input("Enter the card number: ")) - 1
                    card = self.game_state.face_up_cards.pop(card_choice)
                    player.train_cards[card] += 1
                    print(f"{player.name} has drawn {card.name}")
                    self.game_state.face_up_cards.append(self.game_state.train_deck.pop())
                    print(f"New face-up cards: {', '.join([card.name for card in self.game_state.face_up_cards])}")
                    drawn += 1
                case "n":
                    card = self.game_state.train_deck.pop()
                    player.train_cards[card] += 1
                    print(f"{player.name} has drawn {card.name}")
                    drawn += 1
                case "back":
                    self.play_turn(player)
                    return
                case _:
                    print("Invalid choice, please try again.")

        print(f"{player.name}'s train cards: {', '.join(self.formatted_trains(player))}")

    def draw_destination_tickets(self, player: Player):
        destinations = [self.game_state.destination_deck.pop() for _ in range(3)]
        print("You have drawn the following destinations:")
        for i, dest in enumerate(destinations, 1):
            print(f"{i}: {dest.city1} to {dest.city2} ({dest.points} points)")
        
        to_keep = destinations.copy()
        while len(to_keep) > 1:  # Must keep at least one
            choice = input("Would you like to remove any destinations? (y/n)")
            if choice == "y":
                print("Which destination would you like to remove?")
                for i, dest in enumerate(to_keep, 1):
                    print(f"{i}: {dest.city1} to {dest.city2} ({dest.points} points)")
                try:
                    remove_idx = int(input("Enter the destination number to remove: ")) - 1
                    removed = to_keep.pop(remove_idx)
                    print(f"Removed: {removed.city1} to {removed.city2}")
                except (ValueError, IndexError):
                    print("Invalid choice, please try again.")
            elif choice == "n":
                break
            elif choice == "back":
                self.play_turn(player)
                return

        player.destinations.extend(to_keep)
        print(f"{player.name}'s current destinations: {', '.join(self.formatted_destinations(player))}")