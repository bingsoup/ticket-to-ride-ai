import random

class DestinationHeuristic():
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