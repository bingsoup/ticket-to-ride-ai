import random
from helper_classes import Colour

class DestinationHeuristic():
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
                destination_actions = [a for a in actions if a[0] == "draw_destination_tickets"]
                if destination_actions:
                    # Take minimum number of tickets
                    return min(destination_actions, key=lambda a: a[1] + a[2] + a[3])
            
            # Draw cards that help with destinations
            card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
            if card_actions:
                # Prefer wild cards
                for action in card_actions:
                    if action[1] != "deck" and str(action[2]) == "WILD":
                        return action
                
                # Default to drawing from deck
                for action in card_actions:
                    if action[1] == "deck":
                        return action
            
            
            return random.choice(actions)
        return None
    
class BetterDestinationHeuristic():
    """Take routes that help complete destination tickets, take cards that help when no routes are affordable"""
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
                destination_actions = [a for a in actions if a[0] == "draw_destination_tickets"]
                if destination_actions:
                    # Take minimum number of tickets
                    return min(destination_actions, key=lambda a: a[1] + a[2] + a[3])
            
            # Draw cards that help with destinations
            card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
            if card_actions:
                # Prefer wild cards
                for action in card_actions:
                    if action[1] != "deck" and str(action[2]) == "WILD":
                        return action
                
                # Default to drawing from deck
                for action in card_actions:
                    if action[1] == "deck":
                        return action
            
            
            return random.choice(actions)
        return None
    
class BestMoveHeuristic():
    """Only take best possible move or draw cards that help achieve the best possible move"""
    def __init__(self, game_state):
        self.game_state = game_state
        
    def choose_action(self):
        player = self.game_state.current_player
        actions = self.game_state.get_legal_actions()
        cache_valid = self.game_state.best_routes_cache_valid.get(player.name, False)
                
        # Try to claim routes that help complete destinations
        claim_actions = [a for a in actions if a[0] == "claim_route"]
        if claim_actions:
            if cache_valid:
                best_routes = self.game_state.best_routes_cache[player.name]
                for route in best_routes:
                    if route in claim_actions:
                        return route
                    
        # Draw cards that help with destinations
        card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
        if card_actions:
            # Take best cards
            best_draw = self.game_state.select_best_draw_action(card_actions)
            if best_draw:
                return best_draw                
            
            # Draw wild if possible
            for action in card_actions:
                if action[1] != "deck" and action[3] == "nodraw":
                    return action
            
            # Default to drawing from deck
            for action in card_actions:
                if action[1] == "deck":
                    return action
        
        return random.choice(actions)

class LongestRouteHeuristic():
    """Prioritizes building the longest continuous route"""
    def __init__(self, game_state):
        self.game_state = game_state
        
    def choose_action(self):
        actions = self.game_state.get_legal_actions()
        if not actions:
            return None
        # Handle destination tickets
        if actions and actions[0][0] == "draw_destination_tickets":
            # Take minimum number of tickets
            return min(actions, key=lambda a: a[1] + a[2] + a[3])
        
        # Try to claim the longest available route
        claim_actions = [a for a in actions if a[0] == "claim_route"]
        if claim_actions:
            longest_route = max(claim_actions, 
                               key=lambda a: self.game_state.get_route_length(a[1], a[2]))
            return longest_route
        
        # Draw cards
        card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
        if card_actions:
            # Prefer wild cards
            for action in card_actions:
                if action[1] != "deck" and str(action[2]) == "WILD":
                    return action
            
            # Default to drawing from deck
            return [a for a in card_actions if a[1] == "deck"][0]
        
        return random.choice(actions)
    
class OpportunisticHeuristic():
    """Prioritizes high-value actions over long-term planning"""
    def __init__(self, game_state):
        self.game_state = game_state
        
    def choose_action(self):
        actions = self.game_state.get_legal_actions()
        if not actions:
            return None
        # Always draw destination tickets if available and we have few
        if actions and actions[0][0] == "draw_destination_tickets" and len(self.game_state.current_player.destinations) < 5:
            return actions[0]
        
        # Try to claim a route if possible
        claim_actions = [a for a in actions if a[0] == "claim_route"]
        if claim_actions:
            # Prefer shorter routes that give more points per train
            action_scores = []
            for action in claim_actions:
                city1, city2 = action[1], action[2]
                length = self.game_state.get_route_length(city1, city2)
                points = self.game_state.calc_route_points(length)
                efficiency = points / length if length > 0 else 0
                action_scores.append((action, efficiency))
            
            # Return the most efficient route
            return max(action_scores, key=lambda x: x[1])[0]
        
        # Draw cards with preference for wild cards
        card_actions = [a for a in actions if a[0] == "draw_two_train_cards"]
        if card_actions:
            for action in card_actions:
                if action[1] != "deck" and str(action[2]) == "WILD":
                    return action
            # Default to drawing from deck
            for action in card_actions:
                if action[1] == "deck":
                    return action

        return random.choice(actions)
    
class RandomHeuristic():
    def __init__(self, game_state):
        self.game_state = game_state

    def choose_action(self):
        possible_actions = self.game_state.get_legal_actions()
        if not possible_actions:
            return None
        return random.choice(possible_actions)
        
class ShaoHeuristic():
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
                    city1, city2 = optimal_path[i], optimal_path[i+1]
                    
                    # Look for actions that match this path segment
                    for action in claim_actions:
                        action_city1, action_city2 = action[1], action[2]
                        
                        if (action_city1 == city1 and action_city2 == city2) or \
                           (action_city1 == city2 and action_city2 == city1):
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
                        city1, city2 = optimal_path[i], optimal_path[i+1]
                        routes = self.game_state.get_routes_between_cities(city1, city2)
                        
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
        return sorted(claim_actions, 
                      key=lambda a: self.game_state.get_route_length(a[1], a[2]), 
                      reverse=True)
    
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