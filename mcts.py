import math
import random

from console import LiveConsole, is_pypy
from heuristic_agents import DestinationHeuristic

# from graph import visualize_mcts_tree as viz_mcts


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

        const = 2  # Can modify exploration constant
        max_children = int(math.ceil(const * math.sqrt(self.visits)))
        return len(self.children) >= min(len(possible_actions), max_children)

    def expand(self):
        # Get all possible actions from the current state
        possible_actions = self.state.get_legal_actions()
        if len(possible_actions) == 0:
            return None
        # Filter out actions that have already been tried (i.e., have corresponding child nodes)
        untried_actions = [
            action
            for action in possible_actions
            if action not in [child.action for child in self.children]
        ]
        if len(untried_actions) == 0:
            return None

        # Split actions into their respective types to make random selection fair
        random_type = random.choice(
            ["draw_two_train_cards", "claim_route", "draw_destination_tickets"]
        )
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
                    opponent_action = random.choice(opponent_actions)
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
        if hasattr(self.state, "check_all_destinations"):
            results = self.state.check_all_destinations(self.state.current_player)
            num_incomplete = sum(1 for dest in results if dest[1] == False)

        for child in self.children:
            if child.visits == 0:
                choices_weights.append(float("inf"))
            else:
                # Base UCT score
                uct_score = (child.value / child.visits) + c_param * math.sqrt(
                    (2 * math.log(self.visits) / child.visits)
                )

                # Add bias for claim_route actions that might reduce destination distances
                if (
                    child.action
                    and child.action[0] == "claim_route"
                    and num_incomplete > 0
                ):
                    city1, city2 = child.action[1], child.action[2]
                    # Quick check if route directly connects destination endpoints
                    dest_bonus = 0
                    for dest in self.state.current_player.destinations:
                        if not self.state.current_player.uf.is_connected(
                            dest.city1, dest.city2
                        ):
                            best_path = self.state.fw.get_path(dest.city1, dest.city2)
                            if (
                                self.state.current_player.uf.is_connected(
                                    city1, dest.city1
                                )
                                and self.state.current_player.uf.is_connected(
                                    city1, dest.city2
                                )
                                or self.state.current_player.uf.is_connected(
                                    city2, dest.city1
                                )
                                and self.state.current_player.uf.is_connected(
                                    city2, dest.city2
                                )
                            ):
                                # Move connects destination endpoints
                                dest_bonus += 5
                            elif best_path and (
                                city1 in best_path and city2 in best_path
                            ):
                                # Move is in path
                                dest_bonus += 1
                    # Scale bonus perhaps
                    uct_score += dest_bonus

                # Penalize drawing more destination tickets when we already have many
                if child.action and child.action[0] == "draw_destination_tickets":
                    if num_incomplete >= 1:
                        # Progressive penalty: more incomplete tickets = bigger penalty
                        uct_score -= 2 * num_incomplete
                    elif self.state.current_player.remaining_trains > 15:
                        uct_score += 5

                if child.action and child.action[0] == "draw_two_train_cards":
                    # Punish drawing train cards if we have many already
                    num_cards = len(self.state.current_player.train_cards)
                    if num_cards > 15:
                        uct_score -= num_cards * 0.5

                choices_weights.append(uct_score)

        return self.children[choices_weights.index(max(choices_weights))]

    def rollout(self, max_depth):
        current_rollout_state = self.state.copy()
        depth = 0

        while not current_rollout_state.is_end() and depth < max_depth:
            action = self.rollout_policy(current_rollout_state)
            if action is None:
                break
            current_rollout_state.apply_action(action)
            current_player = current_rollout_state.current_player
            # Opponent plays immediately after
            for player in current_rollout_state.players:
                # Cycle all players
                current_rollout_state.switch_turn()
                if current_rollout_state.current_player.name != current_player.name:
                    # Opponents play immediately after
                    opponent_action = DestinationHeuristic(
                        current_rollout_state
                    ).choose_action()
                    # opponent_action = RandomHeuristic(current_rollout_state).choose_action()
                    if opponent_action:
                        current_rollout_state.apply_action(opponent_action)
                    else:
                        opponent_actions = current_rollout_state.get_legal_actions()
                        if opponent_actions:
                            opponent_action = random.choice(
                                opponent_actions
                            )  # TODO - Could make this more advanced
            if current_rollout_state.current_player.name != current_player.name:
                pass
            depth += 1
        return current_rollout_state

    def rollout_policy(self, current_rollout_state):
        # Just use the agent
        return DestinationHeuristic(current_rollout_state).choose_action()
        """ # Old rollout policy
        action_found = False
        while not action_found:
            random_choice = random.random()
            dest_mod = 0
            destinations = current_rollout_state.check_all_destinations(current_rollout_state.current_player)
            sum_dest = sum(1 for dest in destinations if dest[1] == False)
            if sum_dest >= 2:
                dest_mod = 0.01
            elif sum_dest == 1:
                dest_mod = 0.05
            elif sum_dest == 0:
                dest_mod = 0.15

            if random_choice < dest_mod:
                random_type = 'draw_destination_tickets'
            elif random_choice < 0.5:
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
        """

    def backpropagate(self, result):
        self.visits += 1
        self.value += result
        if self.action_type == "draw_destination_tickets":
            pass
        if self.action_type == "claim_route":
            pass
        if self.parent:
            self.parent.backpropagate(result)


class MCTS:
    def __init__(self, game_state):
        self.root = MCTSNode(game_state)
        self.console = None if is_pypy else LiveConsole()

    def best_action(self, simulations_number, max_depth):
        if self.console and not is_pypy:
            self.console.start_live(simulations_number)

        try:
            for sim_num in range(simulations_number):
                v = self.tree_policy()
                state = v.rollout(max_depth)
                player = state.players[state.current_player_idx]
                reward = state.game_result(sim_num)
                v.backpropagate(reward)

                # Update the console display every 10 simulations to avoid slowdown
                if self.console and sim_num % 10 == 0 and not is_pypy:
                    # Collect player information
                    player_info = {
                        "name": player.name,
                        "points": reward,  # Use the calculated reward as points
                    }
                    self.console.update_display(sim_num, player_info)

            # Show when its complete
            if self.console and not is_pypy:
                player = self.root.state.current_player
                self.console.update_display(
                    simulations_number, {"name": player.name, "points": player.points}
                )
                self.console.stop()

            # Visualize the tree
            """
            viz_mcts(self.root, max_depth=4, 
                        filename=f"mcts_tree_turn_{self.root.state.current_player.turn}.png")
            """
            # Print score and return best action
            return self.root.best_child().action

        except Exception as e:
            print(f"Error in MCTS simulation: {e}")
            # Stop if theres an error
            if self.console and not is_pypy:
                self.console.stop()
            # Return a valid action if possible
            if self.root.children:
                return self.root.best_child().action
            return None

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
