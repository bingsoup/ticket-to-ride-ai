import math
import random
from typing import List, Dict, Tuple

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
        possible_actions = self.next_state.get_legal_actions()
        return len(self.children) >= len(possible_actions)

    def expand(self):
        # Get all possible actions from the current state
        possible_actions = self.next_state.get_legal_actions()
        # Filter out actions that have already been tried (i.e., have corresponding child nodes)
        untried_actions = [action for action in possible_actions if action not in [child.action for child in self.children]]
        if len(untried_actions) == 0:
            return None
        action = random.choice(untried_actions)
        self.next_state = self.state.copy()
        self.next_state.apply_action(action)
        child_node = MCTSNode(self.next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def best_child(self, c_param=4): # TODO Area of improvement - Experiment with c_param
        choices_weights = [
            (child.value / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    def rollout(self, sim_num):
        current_rollout_state = self.state.copy()
        while not current_rollout_state.is_end():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state.apply_action(action)
        return current_rollout_state.game_result(sim_num + 1)

    def rollout_policy(self, possible_moves): # TODO Area of improvement - Heuristics
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
        return self.root.best_child().action

    def tree_policy(self): # TODO Area of improvement - Pruning methods etc.
        current_node = self.root
        while not current_node.state.is_end():
            if not current_node.is_fully_expanded():
                new_node = current_node.expand()
                if new_node is not None:
                    return new_node
                else:
                    return current_node.best_child()
            else:
                current_node = current_node.best_child()
        return current_node