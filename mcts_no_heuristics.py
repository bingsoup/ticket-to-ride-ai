import math
import random
#from graph import visualize_mcts_tree as viz_mcts

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.action_type = action[0] if action else None
        self.children = []
        self.visits = 0
        self.value = 0.0

    def is_fully_expanded(self):
        possible_actions = self.state.get_legal_actions()

        const = 2 # TODO modify exploration constant
        max_children = int(math.ceil(const * math.sqrt(self.visits)))
        return len(self.children) >= min(len(possible_actions), max_children)
        """ full expansion
        tried_actions = [child.action for child in self.children]
        expanded = len(tried_actions) >= len(possible_actions)
        if expanded:
            # Check if all possible actions have been tried
            for action in possible_actions:
                if action not in tried_actions:
                    expanded = False
                    break
        # A node is fully expanded only when ALL possible actions have been tried
        return expanded
        """

    def expand(self):
        # Get all possible actions from the current state
        possible_actions = self.state.get_legal_actions()
        if len(possible_actions) == 0:
            return None
        # Filter out actions that have already been tried (i.e., have corresponding child nodes)
        untried_actions = [action for action in possible_actions if action not in [child.action for child in self.children]]
        if len(untried_actions) == 0:
            return None
        
        # Split actions into their respective types to make random selection fair
        random_type = random.choice(['draw_two_train_cards', 'claim_route', 'draw_destination_tickets'])
        action_type = [action for action in untried_actions if action[0] == random_type]
        if not action_type:
            action_type = untried_actions
        # MCTS agent plays a move
        action = random.choice(action_type)
        child_state = self.state.copy()
        child_state.apply_action(action)

        # Opponent plays immediately after
        child_state.switch_turn()
        opponent_actions = child_state.get_legal_actions()
        if opponent_actions:
            opponent_action = random.choice(opponent_actions)  # TODO - Could make this more advanced
            child_state.apply_action(opponent_action)
            
        # Back to MCTS agent's turn
        child_state.switch_turn()        
        child_node = MCTSNode(child_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node
    
    def rollout_random(self, sim_num):
        current_rollout_state = self.state.copy()
        depth = 0
        destination_modifier = 0
        distance_modifier = 0
        wasted_trains = 0
        max_depth = 50
        
        while not current_rollout_state.is_end() and depth < max_depth:
            possible_moves = current_rollout_state.get_legal_actions()
            if not possible_moves:
                break
            action = self.rollout_policy_random(possible_moves)
            current_rollout_state.apply_action(action)
                
            # Opponent plays immediately after
            current_rollout_state.switch_turn()
            opponent_actions = current_rollout_state.get_legal_actions()
            if not opponent_actions:
                break
            opponent_action = random.choice(opponent_actions)
            current_rollout_state.apply_action(opponent_action)
            # Back to MCTS agent's turn
            current_rollout_state.switch_turn()    
            depth += 1  
        # TODO return the depth and work backwords to give rewards for the specific move
        distance_modifier -= wasted_trains * 1.8
        return current_rollout_state, destination_modifier, distance_modifier

    def rollout_policy_random(self, possible_moves):
        return random.choice(possible_moves)
    
    def best_child_random(self, c_param=1.4):
        if not self.children:
            return None
        
        choices_weights = []

        for child in self.children:
            if child.visits == 0:
                choices_weights.append(float('inf'))
            else:
                # Base UCT score
                uct_score = (child.value / child.visits) + \
                        c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
                choices_weights.append(uct_score)
        
        return self.children[choices_weights.index(max(choices_weights))]
    
    def backpropagate(self, result,dest_mod,dist_mod):
        self.visits += 1
        self.value += result
        if self.action_type == 'draw_destination_tickets':
            #self.value -= dest_mod
            pass
        if self.action_type == 'claim_route':
            #self.value += dist_mod
            pass
        if self.parent:
            self.parent.backpropagate(result,dest_mod*0.9,dist_mod*0.9)

class MCTS:
    def __init__(self, game_state, update_queue=None):
        self.root = MCTSNode(game_state)
        self.update_queue = update_queue
    
    def best_action_random(self, simulations_number):
        for sim_num in range(simulations_number):
            v = self.tree_policy_random()
            state, dest_mod, dist_mod = v.rollout_random(sim_num)
            player = state.players[state.current_player_idx]
            reward = state.game_result(sim_num)
            v.backpropagate(reward,dest_mod,dist_mod)
        return self.root.best_child_random().action
 
    def select_initial_destinations(self, current_player):
        """
        Pick the destinations which are most likely to be completed using a simple heuristic.
        
        Returns:
            List of binary values [1,1,0] indicating which tickets to keep
        """
        options = current_player.destinations
        if not options or len(options) == 0:
            return []
        
        # Get minimum number of tickets required to keep
        min_to_keep = 2
        num_options = len(options)
        
        # Calculate a score for each destination ticket
        ticket_scores = []
        for dest in options:
            # Get direct distance between cities
            distance = self.root.state.fw.get_distance(dest.city1, dest.city2)
            
            # Calculate points-per-train ratio (higher is better)
            points_per_distance = dest.points / max(distance, 1)
            
            # Get cities that are used by other tickets
            city1_reused = sum(1 for d in options if d != dest and (d.city1 == dest.city1 or d.city1 == dest.city2 or d.city2 == dest.city1 or d.city2 == dest.city2))
            
            # Calculate final score with bonus for shared cities
            final_score = points_per_distance + (city1_reused * 0.5)
            
            # Small penalty for very long tickets (higher risk)
            if distance > 12:
                final_score *= 0.9
                
            ticket_scores.append((dest, final_score))
        
        # Sort tickets by score (descending)
        ticket_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create result array (1 = keep, 0 = discard)
        result = [0] * num_options
        
        # Keep the highest scoring tickets (at least min_to_keep)
        tickets_to_keep = min(num_options, max(min_to_keep, num_options - 1))
        
        # Get the indices of the best tickets
        best_tickets = [options.index(t[0]) for t in ticket_scores[:tickets_to_keep]]
        
        # Set those indices to 1 (keep)
        for idx in best_tickets:
            result[idx] = 1
        
        # Print info about selection
        print("Destination ticket selection:")
        for i, dest in enumerate(options):
            status = "Keep" if result[i] == 1 else "Discard"
            print(f"{status}: {dest.city1} to {dest.city2} ({dest.points} points, score: {next((s for d, s in ticket_scores if d == dest), 0):.2f})")
        
        return result
    
    def tree_policy_random(self):
        current_node = self.root
        while not current_node.state.is_end():
            if not current_node.is_fully_expanded():
                new_node = current_node.expand()
                if new_node is not None:
                    return new_node
                elif current_node.children:
                    current_node = current_node.best_child_random()
                    if current_node is None:
                        return None
                else:
                    return None
            else:
                next_node = current_node.best_child_random()
                if next_node is None:
                    return current_node
                current_node = next_node
        return current_node


