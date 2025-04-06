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
    
    def rollout(self, max_depth):
        current_rollout_state = self.state.copy()
        depth = 0
        
        while not current_rollout_state.is_end() and depth < max_depth:
            possible_moves = current_rollout_state.get_legal_actions()
            if not possible_moves:
                break
            action = self.rollout_policy(possible_moves)
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
        return current_rollout_state

    def rollout_policy(self, possible_moves):
        return random.choice(possible_moves)
    
    def best_child(self, c_param=1.4):
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
    
    def backpropagate(self, result):
        self.visits += 1
        self.value += result
        if self.action_type == 'draw_destination_tickets':
            pass
        if self.action_type == 'claim_route':
            pass
        if self.parent:
            self.parent.backpropagate(result)

class MCTS:
    def __init__(self, game_state, update_queue=None):
        self.root = MCTSNode(game_state)
        self.update_queue = update_queue
    
    def best_action(self, simulations_number, max_depth):
        for sim_num in range(simulations_number):
            v = self.tree_policy()
            state = v.rollout(max_depth)
            player = state.players[state.current_player_idx]
            reward = state.game_result(sim_num)
            v.backpropagate(reward)
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


