import math
import random
from heuristic_agents import DestinationHeuristic, RandomHeuristic
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
        current_player = child_state.current_player

        for player in child_state.players:
            # Cycle all players
            child_state.switch_turn()
            if child_state.current_player.name != current_player.name:   
                # Opponents play immediately after
                opponent_actions = child_state.get_legal_actions()
                if opponent_actions:
                    opponent_action = random.choice(opponent_actions)  # TODO - Could make this more advanced
                    child_state.apply_action(opponent_action)
            
        child_node = MCTSNode(child_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def best_child(self, c_param=1.4):
        if not self.children:
            return None
        
        choices_weights = []
        
        # Get number of incomplete destination tickets for distance biasing
        num_incomplete = 0
        if hasattr(self.state, 'check_all_destinations'):
            results = self.state.check_all_destinations(self.state.current_player)
            num_incomplete = sum(1 for dest in results if dest[1] == False)
        
        for child in self.children:
            if child.visits == 0:
                choices_weights.append(float('inf'))
            else:
                 # Base UCT score
                uct_score = (child.value / child.visits) + \
                        c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
                
                # Add bias for claim_route actions that might reduce destination distances
                if child.action and child.action[0] == 'claim_route' and num_incomplete > 0:
                    city1, city2 = child.action[1], child.action[2]
                    
                    # Quick check if route directly connects destination endpoints
                    dest_bonus = 0
                    for dest in self.state.current_player.destinations:
                        if (city1 == dest.city1 and city2 == dest.city2) or \
                        (city1 == dest.city2 and city2 == dest.city1):
                            if not self.state.current_player.uf.is_connected(dest.city1, dest.city2):
                                # Direct connection gets high bonus
                                dest_bonus += 1.0
                    
                    # Add bonus for routes that connect to destination cities
                    for dest in self.state.current_player.destinations:
                        if city1 in (dest.city1, dest.city2) or city2 in (dest.city1, dest.city2):
                            dest_bonus += 0.2
                    
                    # Scale bonus based on number of incomplete tickets
                    uct_score += dest_bonus * (num_incomplete / 3)
                
                # Penalize drawing more destination tickets when we already have many
                if child.action and child.action[0] == 'draw_destination_tickets' and num_incomplete >= 1:
                    # Progressive penalty: more incomplete tickets = bigger penalty
                    uct_score -= 5 * num_incomplete
                if child.action and child.action[0] == 'draw_destination_tickets' and num_incomplete == 0 \
                and self.state.current_player.remaining_trains > 15:
                    # Reward for drawing destination tickets if its easily achievable
                    uct_score += 3
                """
                if child.action and child.action[0] == 'draw_two_train_cards':
                    # Punish drawing train cards if we have many already
                    num_cards = len(self.state.current_player.train_cards)
                    if num_cards > 10:
                        uct_score -= 10 * (num_cards / 10)
                """
                choices_weights.append(uct_score)
        
        return self.children[choices_weights.index(max(choices_weights))]
    
    def rollout(self, max_depth):
        current_rollout_state = self.state.copy()
        depth = 0
        destination_modifier = 0
        distance_modifier = 0
        wasted_trains = 0
        
        while not current_rollout_state.is_end() and depth < max_depth:
            #num_draw = 0
            #rem_dest = current_rollout_state.check_all_destinations(current_rollout_state.current_player)
            #num_dest = sum(1 for dest in rem_dest if dest[1] == False)
            #incr = 0
            possible_moves = current_rollout_state.get_legal_actions()
            if not possible_moves:
                break
            action = self.rollout_policy(possible_moves, current_rollout_state)
            """
            if action[0] == 'draw_destination_tickets':
                # Quadratic penalty for drawing destination tickets
                # num_dest is the number of uncompleted tickets
                # I can also penalise based on how much taking this ticket will reduce
                # the closeness of the destination tickets
                num_draw = sum(action[1:3])
                destination_modifier = max((((pow(num_dest,2)) + (15 * num_draw)) // 8),destination_modifier) if num_dest > 0 else 0
            """
            """
            if action[0] == 'claim_route':
                # Store the closeness of the destination tickets such that I can re-check after the route is claimed
                rem_trains = current_rollout_state.current_player.remaining_trains
                destinations = current_rollout_state.get_distance(current_rollout_state.current_player)
            """
            current_rollout_state.apply_action(action)
            """
            if action[0] == 'claim_route':
                # If the closeness of the destination tickets has reduced, reward
                rem_trains_after = current_rollout_state.current_player.remaining_trains
                
                destinations_after = current_rollout_state.get_distance(current_rollout_state.current_player)
                for i in range(len(destinations_after)):
                    if destinations_after[i][1] < destinations[i][1]:
                        incr = destinations[i][1] - destinations_after[i][1]
                        value = destinations[i][0].points
                        distance_modifier += (incr * ((value + 0.5) - destinations_after[i][1]))  
                        #distance_modifier += incr * 3 # (OLD)
                if incr == 0:
                    wasted_trains += rem_trains - rem_trains_after
                    pass
            """
            current_player = current_rollout_state.current_player  
            # Opponent plays immediately after
            for player in current_rollout_state.players:
                # Cycle all players
                current_rollout_state.switch_turn()
                if current_rollout_state.current_player.name != current_player.name:   
                    # Opponents play immediately after
                    #opponent_action = DestinationHeuristic(current_rollout_state).choose_action()
                    opponent_action = RandomHeuristic(current_rollout_state).choose_action()
                    if opponent_action:
                        current_rollout_state.apply_action(opponent_action)
                    else:
                        opponent_actions = current_rollout_state.get_legal_actions()
                        if opponent_actions:
                            opponent_action = random.choice(opponent_actions)  # TODO - Could make this more advanced
            if current_rollout_state.current_player.name != current_player.name:
                pass
            depth += 1  
        # TODO return the depth and work backwards to give rewards for the specific move?
        distance_modifier -= wasted_trains * 1.8
        return current_rollout_state, destination_modifier, distance_modifier

    def rollout_policy(self, possible_moves, current_rollout_state):
        # Bias choices
        action_found = False
        while not action_found:
            random_choice = random.random()
            dest_mod = 0
            destinations = current_rollout_state.check_all_destinations(current_rollout_state.current_player)
            sum_dest = sum(1 for dest in destinations if dest[1] == False)
            if sum_dest >= 2:
                dest_mod = 0
            elif sum_dest == 1:
                dest_mod = 0.05
            elif sum_dest == 0:
                dest_mod = 0.15

            if random_choice < dest_mod:
                random_type = 'draw_destination_tickets'
            elif random_choice < 0.50:
                random_type = 'claim_route'
            else:
                random_type = 'draw_two_train_cards'
            action_type = [action for action in possible_moves if action[0] == random_type]
            if action_type:
                action_found = True
        if random_type == 'draw_destination_tickets':
            # Prefer lower number of destination tickets. Sort by number of destiantions its gonna take. 
            # 80 percent of the time, split the list in half (Then 66 percent to get 1, 33 to get two)
            action_type = sorted(action_type, key=lambda x: sum(x[1:3]))
            if random.random() < 0.8:
                action_type = action_type[:len(action_type)//2]
        if random_type == 'claim_route':
            # 60% of the time, attempt to claim a helpful route
            if random.random() < 0.6: # TODO change the constant
                best_routes = current_rollout_state.select_best_route_action(action_type)
                if best_routes:
                    return best_routes[random.randint(0,len(best_routes)-1)]
        if random_type == 'draw_two_train_cards':
            # 50% of the time, draw the most helpful cards
            if random.random() < 0.5: # TODO change the constant
                best_cards = current_rollout_state.select_best_draw_action(action_type)
                if best_cards:
                    return best_cards
        
        return random.choice(action_type)
    
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

    def best_action(self, simulations_number, max_depth):
        for sim_num in range(simulations_number):
            v = self.tree_policy()
            state, dest_mod, dist_mod = v.rollout(max_depth)
            player = state.players[state.current_player_idx]
            reward = state.game_result(sim_num)
            v.backpropagate(reward,dest_mod,dist_mod)
         # Visualize the tree
        """
        viz_mcts(self.root, max_depth=4, 
                       filename=f"mcts_tree_turn_{self.root.state.current_player.turn}.png")
        """
        #self.root.state.apply_action(self.root.best_child().action)
        self.root.state.print_score()
        return self.root.best_child().action
 
    def tree_policy(self):
        current_node = self.root
        while not current_node.state.is_end():
            if not current_node.is_fully_expanded():
                new_node = current_node.expand()
                if new_node is not None:
                    return new_node
                elif current_node.children:
                    current_node = current_node.best_child()
                    if current_node is None:
                        return None
                else:
                    return None
            else:
                next_node = current_node.best_child()
                if next_node is None:
                    return current_node
                current_node = next_node
        return current_node