import random

from helper_classes import Colour


class DestinationHeuristic:
    """Take routes that help complete destination tickets, take cards from deck if no routes are affordable"""

    def __init__(self, game_state):
        self.game_state = game_state

    def choose_action(self):
        player = self.game_state.current_player
        actions = self.game_state.get_legal_actions()
        if actions:
            # Try to claim routes that help complete destinations
            claim_actions = [a for a in actions if a[0] == "claim_route"]
            if claim_actions:
                best_routes = self.game_state.select_best_route_action(claim_actions)
                if best_routes:
                    return best_routes[0]

            complete_all = True
            completed_destinations = self.game_state.check_all_destinations(player)
            for destination, complete in completed_destinations:
                if not complete:
                    complete_all = False

            if complete_all:
                destination_actions = [
                    a for a in actions if a[0] == "draw_destination_tickets"
                ]
                if destination_actions:
                    # Take minimum number of tickets
                    return min(destination_actions, key=lambda a: a[1] + a[2] + a[3])

            # Draw cards that help with destinations
            card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
            if card_actions:
                # Prefer wild cards
                for action in card_actions:
                    if action[1] != "deck" and action[2] == Colour.WILD:
                        return action

                # Default to drawing from deck
                for action in card_actions:
                    if action[1] == "deck":
                        return action

            return random.choice(actions)
        return None


class BestMoveHeuristic:
    """Only take best possible move or draw cards that help achieve the best possible move"""

    def __init__(self, game_state):
        self.game_state = game_state

    def choose_action(self):
        player = self.game_state.current_player
        player.train_cards[Colour.WILD] += 50
        best_actions = self.game_state.get_legal_actions()
        player.train_cards[Colour.WILD] -= 50
        self.game_state.routes_cache_valid[player.name] = False
        actions = self.game_state.get_legal_actions()

        if not actions:
            return None

        # Take destination tickets if they are all completed
        complete_all = True
        completed_destinations = self.game_state.check_all_destinations(player)
        for destination, complete in completed_destinations:
            if not complete:
                complete_all = False
        if complete_all:
            destination_actions = [
                a for a in actions if a[0] == "draw_destination_tickets"
            ]
            if destination_actions:
                # Take minimum number of tickets
                return min(destination_actions, key=lambda a: a[1] + a[2] + a[3])

        # Assume the player has unlimited cards to find the best possible route
        best_claim_actions = [a for a in best_actions if a[0] == "claim_route"]
        best_route = (
            self.game_state.select_best_route_action(best_claim_actions)
            if best_claim_actions
            else None
        )
        best_route = best_route[0] if best_route else None

        if best_route:
            # Attempt any action that uses the same route regardless of colour
            check_all_colours = [
                a
                for a in actions
                if a[0] == "claim_route"
                and a[5] == best_route[5]
                and a[1] == best_route[1]
                and a[2] == best_route[2]
            ]
            if check_all_colours:
                return check_all_colours[0]
            # Otherwise, attempt to draw cards that help make it affordable
            else:
                colour_needed = best_route[5].colour
                card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
                if card_actions:
                    # If it's a gray route, draw the colour that the player has most of
                    if colour_needed == Colour.GRAY:
                        top_colours = sorted(
                            player.train_cards, key=player.train_cards.get, reverse=True
                        )
                        max_colour = top_colours[0]
                        max_colour_2 = top_colours[1]
                        return self.best_card(card_actions, max_colour, max_colour_2)
                    else:
                        # Draw the specific colour needed for the route
                        return self.best_card(card_actions, colour_needed, Colour.GRAY)

        # We either have no possible claims or no possible draws
        return random.choice(actions)

    def best_card(player, card_actions, best_colour, best_colour_2):
        """Select the best card to draw based on the player's hand"""

        # Sort card actions by the number of occurrences of the best or second best colour
        card_actions = sorted(
            card_actions,
            key=lambda a: (
                (a[1] == best_colour)
                + (a[2] == best_colour)
                + 0.5 * (a[1] == best_colour_2 or a[2] == best_colour_2)
            ),
            reverse=True,
        )
        # Return best card action
        return card_actions[0]


class LongestRouteHeuristic:
    """Prioritizes extending the player's longest continuous route"""

    def __init__(self, game_state):
        self.game_state = game_state

    def choose_action(self):
        player = self.game_state.current_player
        actions = self.game_state.get_legal_actions()

        if not actions:
            return None

        # Handle destination tickets
        if actions and actions[0][0] == "draw_destination_tickets":
            return min(actions, key=lambda a: a[1] + a[2] + a[3])

        # Find longest path in player's current network
        end_cities = self.find_longest_path(player)

        # Try to claim routes that extend the longest path
        claim_actions = [a for a in actions if a[0] == "claim_route"]
        if claim_actions:
            scored_actions = []

            for action in claim_actions:
                city1, city2 = action[1], action[2]
                route_length = self.game_state.get_route_length(city1, city2)
                score = 0

                # Check if route extends the longest path
                if city1 in end_cities or city2 in end_cities:
                    score += 100 + route_length

                # Check if route is on any destination's optimal path
                for dest in player.destinations:
                    if not player.uf.is_connected(dest.city1, dest.city2):
                        optimal_path = self.game_state.fw.get_path(
                            dest.city1, dest.city2
                        )

                        # Check if both cities are on the optimal path and adjacent
                        if city1 in optimal_path and city2 in optimal_path:
                            idx1 = optimal_path.index(city1)
                            idx2 = optimal_path.index(city2)
                            if abs(idx1 - idx2) == 1:
                                score += 50 + dest.points

                # Base score is route length
                score += route_length

                scored_actions.append((action, score))

            if scored_actions:
                # Take the highest scoring route
                return max(scored_actions, key=lambda x: x[1])[0]

        # Draw cards that help claim routes to extend longest path
        card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
        if card_actions:
            # Prefer wild cards
            for action in card_actions:
                if action[1] != "deck" and action[2] == Colour.WILD:
                    return action

            # Default to drawing from deck
            for action in card_actions:
                if action[1] == "deck":
                    return action

        return random.choice(actions)

    def find_longest_path(self, player):
        """Find the longest path in player's network and its end cities"""
        if not player.claimed_connections:
            return [], set()

        # Build adjacency list of player's network
        network = {}
        for city1, city2, _ in player.claimed_connections:
            if city1 not in network:
                network[city1] = []
            if city2 not in network:
                network[city2] = []
            network[city1].append(city2)
            network[city2].append(city1)

        # Find longest path using DFS from each city
        longest_path = []

        for start_city in network:
            for path in self.dfs_paths(network, start_city):
                if len(path) > len(longest_path):
                    longest_path = path

        # Get end cities (first and last city in the path)
        end_cities = set()
        if longest_path:
            end_cities.add(longest_path[0])
            end_cities.add(longest_path[-1])

        return end_cities

    def dfs_paths(self, network, start, path=None):
        """Find all paths from start using DFS"""
        if path is None:
            path = [start]

        # Yield the current path if it's a dead end
        if (
            len(path) > 1
            and len([city for city in network[path[-1]] if city not in path]) == 0
        ):
            yield path

        # Continue DFS
        for next_city in network[path[-1]]:
            if next_city not in path:
                yield from self.dfs_paths(network, start, path + [next_city])


class RandomHeuristic:
    def __init__(self, game_state):
        self.game_state = game_state

    def choose_action(self):
        possible_actions = self.game_state.get_legal_actions()
        if not possible_actions:
            return None
        return random.choice(possible_actions)


class ShaoHeuristic:
    """Implementation of Shao's strategy from the original Java SuperPlayer class"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.turn = 0

    def choose_action(self):
        """Main decision function that selects the best action using Shao's strategy"""
        player = self.game_state.current_player
        actions = self.game_state.get_legal_actions()
        self.turn = player.turn

        if not actions:
            return None

        # Track turns and calculate annealing factor (controls exploration vs. exploitation)
        self.turn += 1
        if self.turn < 40:
            # 68~100% emphasis on exploitation in early game
            annealing_factor = (1 - (self.turn / 100)) * 80 + 20
        else:
            # 0~15% emphasis on exploration in late game
            annealing_factor = (1 - (self.turn / 100)) * 100

        # Sort actions by type
        claim_actions = [a for a in actions if a[0] == "claim_route"]
        card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
        dest_actions = [a for a in actions if a[0] == "draw_destination_tickets"]

        # Check if all destinations are completed
        all_completed = True
        for dest in player.destinations:
            if not player.uf.is_connected(dest.city1, dest.city2):
                all_completed = False
                break

        # If no destinations or all completed, focus on high-value routes
        if all_completed or not player.destinations:
            # If early game, draw more destination tickets
            if self.turn <= 20 and dest_actions:
                return dest_actions[0]

            # Check if player has many cards of one color (≥ 5)
            max_color = self.get_max_color(player)
            max_count = player.train_cards[max_color]

            if max_count >= 5:
                # Find routes matching this color that can be claimed
                for action in claim_actions:
                    route_color = action[3]
                    if route_color == max_color or route_color == Colour.GRAY:
                        return action

            # Random decision based on annealing factor
            if random.random() * 100 < annealing_factor:
                # Draw cards if annealing suggests exploration
                if card_actions:
                    # Prefer wilds
                    for action in card_actions:
                        if action[1] != "deck" and action[2] == Colour.WILD:
                            return action
                    return card_actions[0]
            else:
                # Claim routes if annealing suggests exploitation
                sorted_routes = self.sort_descending(claim_actions)
                if sorted_routes:
                    # Get the route with highest cost
                    return sorted_routes[0]

            # Fallback to drawing cards
            if card_actions:
                return self.select_best_card(card_actions)

        # We have uncompleted destination tickets - focus on completing them
        else:
            # First check if we can claim a route that helps with destinations
            for dest in player.destinations:
                if player.uf.is_connected(dest.city1, dest.city2):
                    continue

                # Get shortest path between destination endpoints
                optimal_path = self.game_state.fw.get_path(dest.city1, dest.city2)

                # Check for affordable routes along optimal path
                for i in range(len(optimal_path) - 1):
                    city1, city2 = optimal_path[i], optimal_path[i + 1]

                    # Look for actions that match this path segment
                    for action in claim_actions:
                        action_city1, action_city2 = action[1], action[2]

                        if (action_city1 == city1 and action_city2 == city2) or (
                            action_city1 == city2 and action_city2 == city1
                        ):
                            return action

            # If no route can be claimed, draw cards that help
            if card_actions:
                # Try to find a wild card (rainbow in original code)
                for action in card_actions:
                    if action[1] != "deck" and action[2] == Colour.WILD:
                        return action

                # Try to find cards that match needed colors on optimal paths
                for dest in player.destinations:
                    if player.uf.is_connected(dest.city1, dest.city2):
                        continue

                    optimal_path = self.game_state.fw.get_path(dest.city1, dest.city2)

                    # Find colors needed for unclaimed routes in the path
                    for i in range(len(optimal_path) - 1):
                        city1, city2 = optimal_path[i], optimal_path[i + 1]
                        routes = self.game_state.route_lookup(city1, city2)

                        for route in routes:
                            if route.claimed_by is None:
                                route_color = route.colour

                                # Look for cards matching this color
                                for action in card_actions:
                                    if action[1] != "deck" and action[2] == route_color:
                                        return action

                # Default to drawing from deck
                for action in card_actions:
                    if action[1] == "deck":
                        return action

        # If no specific strategy applies, try drawing destination tickets
        if len(player.destinations) < 3 and dest_actions:
            return dest_actions[0]

        # Final fallback to any action
        return random.choice(actions)

    def get_max_color(self, player):
        """Get the color with the most cards (excluding wild)"""
        max_count = -1
        max_color = None

        for color in Colour:
            if color != Colour.WILD and color != Colour.GRAY:
                count = player.train_cards[color]
                if count > max_count:
                    max_count = count
                    max_color = color

        return max_color

    def sort_descending(self, claim_actions):
        """Sort routes by length in descending order (highest cost first)"""
        if not claim_actions:
            return []

        # Sort actions by route length in descending order
        return sorted(
            claim_actions,
            key=lambda a: self.game_state.get_route_length(a[1], a[2]),
            reverse=True,
        )

    def select_best_card(self, card_actions):
        """Find the best card to draw based on current strategy"""
        # First priority: draw a wild card
        for action in card_actions:
            if action[1] != "deck" and action[2] == Colour.WILD:
                return action

        # Second priority: draw a card of the most common color
        max_color = self.get_max_color(self.game_state.current_player)
        for action in card_actions:
            if action[1] != "deck" and action[2] == max_color:
                return action

        # Last priority: draw from the deck
        for action in card_actions:
            if action[1] == "deck":
                return action

        # Fallback to any card action
        return card_actions[0]
