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
