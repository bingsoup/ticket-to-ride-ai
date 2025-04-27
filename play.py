from typing import List

from helper_classes import Colour, Player


class PlayerController:
    def __init__(self, game_state):
        self.game_state = game_state

    def formatted_trains(self, player: Player) -> List[str]:
        return [
            f"{colour.name.capitalize()}: {count}"
            for colour, count in player.train_cards.items()
            if count > 0
        ]

    def formatted_destinations(self, player: Player) -> List[str]:
        return [
            f"{destination.city1} to {destination.city2} ({destination.points})"
            for destination in player.destinations
        ]

    def formatted_colours(self, colours: List[Colour]) -> List[str]:
        return [colour.name.capitalize() for colour in colours]

    def print_board(self):
        print("=== Ticket to Ride Board ===")
        for city1, connections in sorted(self.game_state.routes.items()):
            print(f"\n{city1}:")
            for city2, routes in sorted(connections.items()):
                for route in routes:
                    status = (
                        "Claimed by " + route.claimed_by
                        if route.claimed_by
                        else "Available"
                    )
                    print(f"  -> {city2} ({route.colour} * {route.length}): {status}")
        print("===========================")

    def print_available_routes(self, player: Player):
        unclaimed_routes = self.game_state.get_unclaimed_routes()
        available_routes = []

        for city1, city2, route in unclaimed_routes:
            # Check if player has enough cards to claim the route
            if route.colour == Colour.GRAY:
                for colour in Colour:
                    if (
                        colour != Colour.WILD
                        and colour != Colour.GRAY
                        and player.train_cards[colour] + player.train_cards[Colour.WILD]
                        >= route.length
                    ):
                        if not any(
                            r[0] == city1 and r[1] == city2 and r[3] == colour
                            for r in available_routes
                        ):
                            available_routes.append((city1, city2, route, colour))
            elif (
                player.train_cards[route.colour] + player.train_cards[Colour.WILD]
                >= route.length
            ):
                if not any(
                    r[0] == city1 and r[1] == city2 and r[3] == route.colour
                    for r in available_routes
                ):
                    available_routes.append((city1, city2, route, route.colour))

        if available_routes:
            print("\nRoutes you can complete:")
            for city1, city2, route, colour in available_routes:
                print(f"{city1} -> {city2} ({colour} * {route.length})")
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
        print(
            f"{player.name}'s train cards: {', '.join(self.formatted_trains(player))}"
        )
        print(
            f"{player.name}'s destination tickets: {', '.join(self.formatted_destinations(player))}"
        )
        print(
            f"Face-up cards: {', '.join([card.name for card in self.game_state.face_up_cards])}"
            + "\n"
        )

        choice = input(
            "<1: Draw Train cards, 2: Claim a route, 3: Draw destination tickets, 4: Print board, 5: Print routes you can complete, 6: Print score, 7: Show destination tickets, exit: Exit game>\n"
        )

        match choice:
            case "1":
                return self.draw_train_cards(player)
            case "2":
                return self.handle_claim_route(player)
            case "3":
                return self.draw_destination_tickets(player)
            case "4":
                self.print_board()
                return self.play_turn(player)
            case "5":
                self.print_available_routes(player)
                return self.play_turn(player)
            case "6":
                print(f"{player.name}'s score: {player.points}")
                return self.play_turn(player)
            case "7":
                self.destination_completion_check(player)
                return self.play_turn(player)
            case "exit":
                exit()
            case _:
                print("Invalid choice, please try again.")
                return self.play_turn(player)

    def handle_claim_route(self, player: Player):
        print("Choose a route to claim:")
        city1 = input("Enter the first city: ")
        if city1 == "back":
            return self.play_turn(player)

        city2 = input("Enter the second city: ")
        if city2 == "back":
            return self.play_turn(player)

        routes = self.game_state.get_routes_between_cities(city1, city2)
        if not routes:
            print("No route exists between these cities.")
            return self.play_turn(player)

        available_colours = []
        route = routes[0]  # Get the first route between these cities

        # Check if the route is already claimed
        if route.claimed_by is not None:
            print(f"This route is already claimed by {route.claimed_by}.")
            return self.play_turn(player)

        # Special handling for ferries and tunnels
        required_locomotives = getattr(route, "num_locomotives", 0)
        is_tunnel = getattr(route, "tunnel", False)

        # For GRAY routes, check all colours
        if route.colour == Colour.GRAY:
            for colour in Colour:
                if colour != Colour.WILD and colour != Colour.GRAY:
                    # For ferries, make sure player has enough wilds for the required locomotives
                    if player.train_cards[Colour.WILD] >= required_locomotives:
                        remaining_cards_needed = route.length - required_locomotives
                        if (
                            player.train_cards[colour]
                            + (player.train_cards[Colour.WILD] - required_locomotives)
                            >= remaining_cards_needed
                        ):
                            available_colours.append(colour)
        # For coloured routes, check that specific colour
        else:
            colour = route.colour
            # For ferries, make sure player has enough wilds for the required locomotives
            if player.train_cards[Colour.WILD] >= required_locomotives:
                remaining_cards_needed = route.length - required_locomotives
                if (
                    player.train_cards[colour]
                    + (player.train_cards[Colour.WILD] - required_locomotives)
                    >= remaining_cards_needed
                ):
                    available_colours.append(colour)

        if not available_colours:
            print("You don't have enough cards to claim this route.")
            return self.play_turn(player)

        colour = None
        if len(available_colours) > 1:
            colour_choice = input(
                f"Choose a colour to claim the route ({', '.join([colour.name for colour in available_colours])}): "
            )
            if colour_choice == "back":
                return self.play_turn(player)

            for avail_colour in available_colours:
                if colour_choice.upper() == avail_colour.name:
                    colour = avail_colour
                    break

            if colour is None:
                print("Invalid colour choice, please try again.")
                return self.handle_claim_route(player)
        else:
            colour = available_colours[0]

        # Calculate base cards needed
        base_wilds_needed = max(
            required_locomotives, max(0, route.length - player.train_cards[colour])
        )

        # Explain the costs to the player
        if is_tunnel:
            print(
                f"You are attempting to claim a tunnel route between {city1} and {city2}."
            )
            print(
                f"Base cost: {route.length} {colour.name} cards (using {base_wilds_needed} wild cards)"
            )
            print("The game will draw 3 cards to check for additional costs.")
            proceed = input("Do you want to proceed? (y/n): ")
            if proceed.lower() != "y":
                return self.play_turn(player)
        elif required_locomotives > 0:
            print(
                f"This ferry route requires {required_locomotives} locomotive cards and {route.length - required_locomotives} additional cards."
            )
            proceed = input("Do you want to proceed? (y/n): ")
            if proceed.lower() != "y":
                return self.play_turn(player)

        # Return the claim_route action with appropriate parameters
        if base_wilds_needed > 0:
            print(
                f"You are claiming {city1} to {city2} with {colour.name}, using at least {base_wilds_needed} wild cards."
            )
        else:
            print(f"You are claiming {city1} to {city2} with {colour.name}.")
        return [
            "claim_route",
            city1,
            city2,
            colour,
            base_wilds_needed,
            route,
            player.name,
        ]

    def draw_train_cards(self, player: Player):
        drawn_cards = []
        card_indices = []

        for draw_num in range(2):
            if draw_num == 1 and drawn_cards and drawn_cards[0] == Colour.WILD:
                # If first card was wild, can't draw another card
                print(
                    "You drew a wild card for your first pick, so you can't draw a second card."
                )
                break

            choice = input(
                f"Card {draw_num + 1}: Would you like to draw from the face-up cards? (y/n) "
            )
            if choice == "back":
                return self.play_turn(player)

            if choice.lower() == "y":
                print("Choose a card to draw:")
                for i, card in enumerate(self.game_state.face_up_cards):
                    print(f"{i + 1}: {card.name}")

                card_choice = int(input("Enter the card number: ")) - 1

                if card_choice < 0 or card_choice >= len(self.game_state.face_up_cards):
                    print("Invalid card choice. Try again.")
                    return self.draw_train_cards(player)

                if (
                    draw_num == 1
                    and self.game_state.face_up_cards[card_choice] == Colour.WILD
                ):
                    print("You cannot take a wild card as your second pick. Try again.")
                    return self.draw_train_cards(player)

                drawn_cards.append(self.game_state.face_up_cards[card_choice])
                card_indices.append(card_choice)

            elif choice.lower() == "n":
                drawn_cards.append("deck")
                card_indices.append("deck")
            else:
                print("Invalid choice. Please enter 'y' or 'n'.")
                return self.draw_train_cards(player)

        # Format the draw train cards action
        if len(drawn_cards) == 1:
            # If only one card was drawn (because first card was a wild)
            return [
                "draw_two_train_cards",
                card_indices[0],
                drawn_cards[0],
                "nodraw",
                "nodraw",
                player.name,
            ]
        else:
            return [
                "draw_two_train_cards",
                card_indices[0],
                drawn_cards[0],
                card_indices[1],
                drawn_cards[1],
                player.name,
            ]

    def draw_destination_tickets(self, player: Player):
        if len(self.game_state.destination_deck) < 3:
            print("Not enough destination tickets in the deck.")
            return self.play_turn(player)

        # Preview the top 3 destination cards
        destinations = self.game_state.destination_deck[
            :3
        ]  # Just look at them, don't remove
        print("You are drawing the following destination tickets:")
        for i, dest in enumerate(destinations, 1):
            print(f"{i}: {dest.city1} to {dest.city2} ({dest.points} points)")

        # Create a binary array [i, j, k] where 1 means keep and 0 means discard
        keep_choices = [0, 0, 0]

        # Player must keep at least one card
        while sum(keep_choices) < 1:
            for i in range(3):
                choice = input(f"Keep ticket {i + 1}? (y/n): ")
                if choice.lower() == "y":
                    keep_choices[i] = 1
                elif choice.lower() == "back":
                    return self.play_turn(player)

            if sum(keep_choices) < 1:
                print("You must keep at least one destination ticket.")

        # Return the draw_destination_tickets action with the keep choices
        return [
            "draw_destination_tickets",
            keep_choices[0],
            keep_choices[1],
            keep_choices[2],
            player.name,
        ]
