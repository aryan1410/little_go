import random
import json
from copy import deepcopy
import os
from host import GO
from read import readInput
from write import writeOutput
import math
class MinimaxQLearningPlayer:
    def __init__(self, size, piece_type, move_count = 0, epsilon=1.0, epsilon_decay=0.999992, epsilon_min=0.01, alpha=0.03, gamma=0.95, move_count_file="move.txt", epsilon_file="epsilon.txt", q_table_black_file="q_table_black.json", q_table_white_file="q_table_white.json"):
        self.size = size
        self.piece_type = piece_type
        self.epsilon = epsilon
        self.move_count = move_count
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon_file = epsilon_file
        self.move_count_file = move_count_file
        self.q_table_black_file = q_table_black_file
        self.q_table_white_file = q_table_white_file
        self.q_table_black = {}
        self.q_table_white = {}
        self.load_q_table()
        self.load_epsilon()
        self.load_move_count()
        self.all_positions = []
        for i in range(size):
            for j in range(size):
                self.all_positions.append((i, j))
        self.valid_moves_cache = {}
    
    def load_move_count(self):
        if os.path.exists(self.move_count_file):
            with open(self.move_count_file, "r") as f:
                self.move_count = float(f.read().strip())
    
    def load_epsilon(self):
        if os.path.exists(self.epsilon_file):
            with open(self.epsilon_file, "r") as f:
                self.epsilon = float(f.read().strip())

    def save_epsilon(self):
            with open(self.epsilon_file, "w") as f:
                f.write(str(self.epsilon))

    def save_move_count(self):
            with open(self.move_count_file, "w") as f:
                f.write(str(self.move_count))

    def load_q_table(self):
        if self.piece_type == 1:
            if os.path.exists(self.q_table_black_file):
                try:
                    with open(self.q_table_black_file, "r") as f:
                        q_table_str_keys = json.load(f)
                        self.q_table_black = self._convert_keys_to_tuples(q_table_str_keys)
                except (json.JSONDecodeError, SyntaxError, ValueError):
                    self.q_table_black= {}
            else:
                self.q_table_black = {}
        else:
            if os.path.exists(self.q_table_white_file):
                try:
                    with open(self.q_table_white_file, "r") as f:
                        q_table_str_keys = json.load(f)
                        self.q_table_white = self._convert_keys_to_tuples(q_table_str_keys)
                except (json.JSONDecodeError, SyntaxError, ValueError):
                    self.q_table_white= {}
            else:
                self.q_table_white = {}

    def save_q_table(self):
        if self.piece_type == 1:
            q_table_black_filtered = {state: {action: q for action, q in actions.items() if q != 0}
                            for state, actions in self.q_table_black.items() if actions}
            q_table_str_keys = self._convert_keys_to_strings(q_table_black_filtered)
            with open(self.q_table_black_file, "w") as f:
                json.dump(q_table_str_keys, f, indent=4)
        else:
            q_table_white_filtered = {state: {action: q for action, q in actions.items() if q != 0}
                            for state, actions in self.q_table_white.items() if actions}
            q_table_str_keys = self._convert_keys_to_strings(q_table_white_filtered)
            with open(self.q_table_white_file, "w") as f:
                json.dump(q_table_str_keys, f, indent=4)

    def _convert_keys_to_strings(self, obj):
        if isinstance(obj, dict):
            return {str(k): self._convert_keys_to_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_keys_to_strings(v) for v in obj]
        else:
            return obj

    def _convert_keys_to_tuples(self, obj):
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                try:
                    if k == "PASS":
                        key_tuple = "PASS"
                    else:
                        key_tuple = eval(k) if isinstance(k, str) else k
                        new_dict[key_tuple] = self._convert_keys_to_tuples(v)
                except (SyntaxError, ValueError):
                    new_dict[k] = self._convert_keys_to_tuples(v)
            return new_dict
        elif isinstance(obj, list):
            return [self._convert_keys_to_tuples(v) for v in obj]
        else:
            return obj
    
    def is_eye(self, go, i, j, piece_type):
        neighbors = go.detect_neighbor(i, j)
        for x, y in neighbors:
            if go.board[x][y] != piece_type:
                return False
        return True
    
    def calculate_influence(self, go, piece_type):
        influence = [[0 for _ in range(go.size)] for _ in range(go.size)]
        decay_rate = 0.5

        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == piece_type:
                    for x in range(go.size):
                        for y in range(go.size):
                            distance = abs(i - x) + abs(j - y)
                            influence[x][y] += (decay_rate ** distance)

        return influence

    def calculate_reward(self, go, action):
        opponent_type = 3 - self.piece_type
        new_go = go.copy_board()
        captured_pieces=0
        lost_pieces=0
        territory = 0
        board_control=go.score(self.piece_type)-go.score(opponent_type)-1
        allies = []
        group_size=0
        corner_edge_control=0
        center_control=0
        ko=0
        if action != "PASS":
            new_go.place_chess(action[0], action[1], self.piece_type)
            captured_pieces = len(new_go.remove_died_pieces(opponent_type))
            lost_pieces = len(new_go.remove_died_pieces(self.piece_type))
            board_control = new_go.score(self.piece_type) - new_go.score(opponent_type)
            allies = new_go.ally_dfs(action[0], action[1])
            group_size = len(new_go.ally_dfs(action[0], action[1]))
            i, j = action
            if len(new_go.remove_died_pieces(opponent_type)) > 0:
                ko = len(new_go.remove_died_pieces(opponent_type))*1.25
            if (i == 0 or i == go.size - 1) and (j == 0 or j == go.size - 1):
                corner_edge_control= 3
            elif i == 0 or i == go.size - 1 or j == 0 or j == go.size - 1:
                corner_edge_control= 2
            else:
                corner_edge_control= 1
            i, j = action
            distance_to_center = abs(i - new_go.size // 2) + abs(j - new_go.size // 2)
            center_control = max(0, 5 - distance_to_center)

        if new_go.game_end(self.piece_type, action):
            return 100 if new_go.judge_winner() == self.piece_type else -100

        new_liberty_count = sum(1 for i, j in allies if new_go.find_liberty(i, j))
        opponent_atari = 0
        self_atari = 0
        opponent_allies = []
        for i in range(new_go.size):
            for j in range(new_go.size):
                if new_go.board[i][j] == opponent_type:
                    opponent_allies.append((i, j))
        for i, j in opponent_allies:
            if not new_go.find_liberty(i, j):
                if self.piece_type == 1:
                    opponent_atari += 25
                else:
                    opponent_atari += 5
            elif new_go.ally_dfs(i, j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) == 1:
                if self.piece_type == 1:
                    opponent_atari += 10
                else:
                    opponent_atari += 3
            elif new_go.ally_dfs(i,j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) > 1:
                if self.piece_type == 1:
                    opponent_atari -= sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.75
                else:
                    opponent_atari -= sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.1
        for i, j in allies:
            if not new_go.find_liberty(i, j):
                if self.piece_type == 1:
                    self_atari -= 5
                else:
                    self_atari -= 10
            elif new_go.ally_dfs(i, j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) == 1:
                if self.piece_type == 1:
                    self_atari -= 4
                else:
                    self_atari -= 6
            elif new_go.ally_dfs(i, j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) > 1:
                if self.piece_type == 1:
                    self_atari += sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.3
                else:
                    self_atari += sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.75

        player_pieces = [(i, j) for i in range(go.size) for j in range(go.size) if go.board[i][j] == self.piece_type]
        opponent_pieces = [(i, j) for i in range(go.size) for j in range(go.size) if go.board[i][j] == opponent_type]
        for i in range(new_go.size):
            for j in range(new_go.size):
                if go.board[i][j] == 0:
                    min_player_distance = min(abs(i - x) + abs(j - y) for x, y in player_pieces) if player_pieces else float('inf')
                    min_opponent_distance = min(abs(i - x) + abs(j - y) for x, y in opponent_pieces) if opponent_pieces else float('inf')
                    if min_player_distance < min_opponent_distance:
                        territory += 1

        eyes = 0
        for i in range(new_go.size):
            for j in range(new_go.size):
                if go.board[i][j] == 0 and self.is_eye(new_go, i, j, self.piece_type):
                    eyes += 1

        if self.piece_type == 1:
            white_potential_territory = 0
            early_game_aggression = 0
            late_game_stability = 0
            trap_bonus = 0
            sente_bonus = 0
            black_influence = self.calculate_influence(new_go, self.piece_type)
            white_influence = self.calculate_influence(new_go, opponent_type)
            influence_diff = 0
            cutting_reward = 0
            early_tempo = 0
            for i in range(new_go.size):
                for j in range(new_go.size):
                    if new_go.board[i][j] == 0:
                        if any(new_go.board[x][y] == opponent_type for x, y in new_go.detect_neighbor(i, j)):
                            white_potential_territory += 1
            if new_go.n_move < 10:
                early_game_aggression = captured_pieces * 5
            if new_go.n_move >= new_go.max_move // 2:
                late_game_stability = territory * 2
            for i in range(go.size):
                for j in range(go.size):
                    influence_diff += (black_influence[i][j] - white_influence[i][j])
            if any(new_go.valid_place_check(x, y, opponent_type, test_check=True) for x, y in new_go.detect_neighbor(i, j)):
                sente_bonus = 15
            if lost_pieces == 1 and captured_pieces > 1:
                trap_bonus = 20
            if action != "PASS":
                for x, y in new_go.detect_neighbor(action[0], action[1]):
                    if new_go.board[x][y] == opponent_type:
                        group = new_go.ally_dfs(x, y)
                        if len(group) > 1 and sum(1 for i, j in group if new_go.find_liberty(i, j)) <= 2:
                            cutting_reward += 12
            if new_go.n_move < 5:
                early_tempo = center_control * 1.5 + corner_edge_control * 1.5

        if self.piece_type == 1:
            capture_reward = 20 * captured_pieces
            lost_penalty = -20 * lost_pieces
            influence_reward = 15 * influence_diff
            control_reward = 10 * board_control
            liberty_reward = 8 * new_liberty_count
            territory_control = 7 * territory
            eye_formation = 10 * eyes
            group_reward = 3 * group_size
            corner_edge_reward = 5 * corner_edge_control
            ko_threat = 10 * ko
            pass_penalty = -3 if action == "PASS" else 0
            total_reward = (capture_reward + lost_penalty + influence_reward+ control_reward +
                            liberty_reward + opponent_atari +
                            self_atari + territory_control + eye_formation +
                            group_reward + corner_edge_reward + pass_penalty + center_control -
                            (1.5*white_potential_territory) + early_game_aggression + late_game_stability + ko_threat + cutting_reward + early_tempo + trap_bonus  + sente_bonus)
        else:
            capture_reward = 8 * captured_pieces
            lost_penalty = -10 * lost_pieces
            control_reward = 15 * board_control
            liberty_reward = 6 * new_liberty_count
            territory_control = 15 * territory
            eye_formation = 10 * eyes
            group_reward = 5 * group_size
            corner_edge_reward = 3 * corner_edge_control
            pass_penalty = -3 if action == "PASS" else 0
            total_reward = (capture_reward + lost_penalty + control_reward +
                            liberty_reward + opponent_atari +
                            self_atari + territory_control + eye_formation +
                            group_reward + corner_edge_reward + pass_penalty)
        return total_reward



    def get_input(self, go, piece_type):
        if (random.random()*0.0) < self.epsilon:
            print("Exploring")
            return self.get_random_move(go, piece_type)
        else:
            print("Exploiting")
            return self.bestMove(go.board, piece_type, go)

    def get_random_move(self, go, piece_type):
        board_state = self.get_state(go.board)
        cache_key = (board_state, piece_type)
        if cache_key in self.valid_moves_cache:
            possible_placements = self.valid_moves_cache[cache_key]
        else:
            possible_placements = []
            for i, j in self.all_positions:
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))
            self.valid_moves_cache[cache_key] = possible_placements
            if len(self.valid_moves_cache) > 1000:
                self.valid_moves_cache.pop(next(iter(self.valid_moves_cache)))
        if not possible_placements:
            return "PASS"
        q_table = self.q_table_black if self.piece_type == 1 else self.q_table_white
        tried_moves = set()
        if board_state in q_table:
            tried_moves = set(q_table[board_state].keys())
        untried_moves = [move for move in possible_placements if move not in tried_moves]
        if untried_moves:
            return random.choice(untried_moves)
        else:
            return random.choice(possible_placements)

    def minimax(self, board, depth, piece_type, maxTurn, maxDepth, alpha=-float('inf'), beta=float('inf')):
        opponent_piece=3-piece_type
        if depth == maxDepth or go.game_end(piece_type, "MOVE"):
            return self.evaluation_function(board, piece_type)
        empty_cells = [(i, j) for i, j in self.all_positions if board[i][j] == 0]

        if maxTurn:
            best = -float('inf')
            for i,j in empty_cells:
                board[i][j] = piece_type
                best = max(best, self.minimax(board, depth + 1, piece_type, False, maxDepth, alpha, beta))
                board[i][j] = 0
                alpha = max(alpha, best)
                if best >= beta:
                    return best
            return best
        else:
            best = float('inf')
            for i,j in empty_cells:
                board[i][j] = opponent_piece
                best = min(best, self.minimax(board, depth + 1, piece_type, True, maxDepth, alpha, beta))
                board[i][j] = 0
                beta = min(beta,best)
                if best <= alpha:
                    return best
            return best

    def bestMove(self, board, piece_type, go):
        bestVal = -float('inf')
        best_move = "PASS"
        valid_moves = []
        for i, j in self.all_positions:
            if board[i][j] == 0 and go.valid_place_check(i, j, piece_type, test_check=True):
                valid_moves.append((i, j))
        if not valid_moves:
            return "PASS"
        state = self.get_state(board)
        
        if piece_type == 1:
            if state in self.q_table_black:
                q_values = {move: self.q_table_black[state].get(move, 0) for move in valid_moves}
                valid_moves.sort(key=lambda move: q_values.get(move, 0), reverse=True)

            for i, j in valid_moves:
                board[i][j] = piece_type
                moveVal = self.minimax(board, 0, piece_type, False, 4, -float('inf'), float('inf'))
                board[i][j] = 0

                if moveVal > bestVal:
                    best_move = (i, j)
                    bestVal = moveVal
            return best_move
        else:
            if state in self.q_table_white:
                q_values = {move: self.q_table_white[state].get(move, 0) for move in valid_moves}
                valid_moves.sort(key=lambda move: q_values.get(move, 0), reverse=True)

            for i, j in valid_moves:
                board[i][j] = piece_type
                moveVal = self.minimax(board, 0, piece_type, False, 3, -float('inf'), float('inf'))
                board[i][j] = 0

                if moveVal > bestVal:
                    best_move = (i, j)
                    bestVal = moveVal
            return best_move

    def evaluation_function(self, board, piece_type):
        state = self.get_state(board)
        return self.get_q_value(state, None)

    def get_state(self, board):
        return tuple(tuple(row) for row in board)

    def get_q_value(self, state, action):
        if self.piece_type == 1:
            if state not in self.q_table_black:
                self.q_table_black[state] = {}
            if action not in self.q_table_black[state]:
                self.q_table_black[state][action] = 0
            return self.q_table_black[state][action]
        else:
            if state not in self.q_table_white:
                self.q_table_white[state] = {}
            if action not in self.q_table_white[state]:
                self.q_table_white[state][action] = 0
            return self.q_table_white[state][action]

    def update_q_value(self, state, action, reward, next_state):
        if self.piece_type == 1:
            current_q = self.get_q_value(state, action)
            max_future_q = max([self.get_q_value(next_state, a) for a in self.get_valid_actions(next_state)], default=0)
            new_q = (current_q*(1-self.alpha))+(self.alpha*(reward + (self.gamma*max_future_q)))
            self.q_table_black[state][action]=new_q
        else:
            current_q = self.get_q_value(state, action)
            max_future_q = max([self.get_q_value(next_state, a) for a in self.get_valid_actions(next_state)], default=0)
            new_q = (current_q*(1-self.alpha))+(self.alpha*(reward + (self.gamma*max_future_q)))
            self.q_table_white[state][action]=new_q

    def get_valid_actions(self, state):
        board = [list(row) for row in state]
        return [(i, j) for i, j in self.all_positions if board[i][j] == 0]

    def train(self, go, state, action, next_state, iteration):
        for _ in range(15):
            reward = self.calculate_reward(go, action)
            self.update_q_value(state, action, reward, next_state)
        self.epsilon = max(self.epsilon_min, (self.epsilon*self.epsilon_decay))
        self.save_epsilon()
        self.save_q_table()


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MinimaxQLearningPlayer(size=N, piece_type=piece_type)
    state = player.get_state(go.board)
    action = player.get_input(go, piece_type)
    if action != "PASS":
        simulated_go = deepcopy(go)
        simulated_go.place_chess(action[0], action[1], piece_type)
        simulated_go.remove_died_pieces(3 - piece_type)
        next_state = player.get_state(simulated_go.board)
    else:
        next_state = state
    player.move_count += 1
    player.save_move_count()
    player.train(go, state, action, next_state, player.move_count)
    if action == "PASS":
        writeOutput("PASS")
    else:
        writeOutput(action)