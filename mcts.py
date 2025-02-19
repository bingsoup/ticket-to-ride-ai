from concurrent.futures import ProcessPoolExecutor
import math
import random
import multiprocessing
from queue import Empty

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.next_state = state.copy()
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0

    def is_fully_expanded(self):
        possible_actions = self.state.get_legal_actions()
        max_children = int(math.ceil(math.sqrt(self.visits)))  # Progressive widening
        return len(self.children) >= min(len(possible_actions), max_children)

    def expand(self):
        # Get all possible actions from the current state
        possible_actions = self.next_state.get_legal_actions()
        if len(possible_actions) == 0:
            return None
        # Filter out actions that have already been tried (i.e., have corresponding child nodes)
        untried_actions = [action for action in possible_actions if action not in [child.action for child in self.children]]
        if len(untried_actions) == 0:
            return None
        
        # MCTS agent plays a move
        action = random.choice(untried_actions)
        self.next_state = self.state.copy()
        self.next_state.apply_action(action)

        # Opponent plays immediately after
        self.next_state.switch_turn()
        opponent_actions = self.next_state.get_legal_actions()
        if opponent_actions:
            opponent_action = random.choice(opponent_actions)  # TODO - Could make this more advanced
            self.next_state.apply_action(opponent_action)
        # Back to MCTS agent's turn
        self.next_state.switch_turn()        
        child_node = MCTSNode(self.next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def best_child(self, c_param=4):
        if not self.children:
            return None

        choices_weights = []
        for child in self.children:
            if child.visits == 0:
                choices_weights.append(float('inf'))
            else:
                one_off_bonus = 2 if child.state.one_off() else 0
                weight = (child.value / child.visits) + \
                         c_param * math.sqrt((2 * math.log(self.visits) / child.visits)) + \
                         one_off_bonus
                choices_weights.append(weight)

        return self.children[choices_weights.index(max(choices_weights))]

    def rollout(self, sim_num):
        current_rollout_state = self.state.copy()
        while not current_rollout_state.is_end():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state.apply_action(action)
            # Opponent plays immediately after
            current_rollout_state.switch_turn()
            opponent_actions = current_rollout_state.get_legal_actions()
            if opponent_actions:
                opponent_action = random.choice(opponent_actions)  # TODO - Could make this more advanced
                current_rollout_state.apply_action(opponent_action)
            # Back to MCTS agent's turn
            current_rollout_state.switch_turn()      
        return current_rollout_state.game_result(sim_num + 1)

    def rollout_policy(self, possible_moves):
        return random.choice(possible_moves)

    def backpropagate(self, result):
        self.visits += 1
        self.value += result
        if self.parent:
            self.parent.backpropagate(result)

class MCTS:
    def __init__(self, game_state):
        self.root = MCTSNode(game_state)

    def best_action(self, simulations_number):
        for sim_num in range(simulations_number):
            v = self.tree_policy()
            reward = v.rollout(sim_num)
            v.backpropagate(reward)
        self.root.best_child().state.print_scores()
        return self.root.best_child().action
    

    
    def best_action_multi(self, simulations_number, num_processes=8):
        if not self.root.state.get_legal_actions():
            return None

        simulations_per_process = simulations_number // num_processes

        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            results = list(executor.map(run_simulation, [self.root.state] * num_processes, [simulations_per_process] * num_processes))

        if not results:
            return None
        best = max(set(results), key=results.count)
        best.root.best_child().state.print_scores()
        return max(set(results), key=results.count)  # Most common best action

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


def run_simulation(game_state, simulations_number):
    """ Runs an independent MCTS simulation for multiprocessing """
    local_mcts = MCTS(game_state)
    
    for _ in range(simulations_number):
        v = local_mcts.tree_policy()
        if v:
            reward = v.rollout(simulations_number)
            v.backpropagate(reward)
    return local_mcts.root.best_child().action if local_mcts.root.best_child() else None