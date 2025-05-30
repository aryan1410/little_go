from read import readInput
from write import writeOutput
from host import GO

class MyPlayer():
    def __init__(self):
        self.type = 'my_player'

    def get_input(self, go, piece_type):
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))
        if piece_type == 1:
            attacking_moves = self.prioritize_attacking_opponent(go, possible_placements, piece_type)
            if attacking_moves:
                possible_placements = attacking_moves
        if not possible_placements:
            return "PASS"
        else:
            best_move = possible_placements[0]
            best_value = -float('inf')
            alpha = -float('inf')
            beta = float('inf')
            for move in possible_placements:
                test_go = go.copy_board()
                test_go.place_chess(move[0], move[1], piece_type)
                value = self.minimax(test_go, 2, False, alpha, beta, move, piece_type,25)
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, best_value)
            return best_move

    def prioritize_attacking_opponent(self, go, moves, piece_type):
        opponent_type = 3 - piece_type
        max_captures = -1
        best_attack_moves = []

        for move in moves:
            test_go = go.copy_board()
            test_go.place_chess(move[0], move[1], piece_type)
            captured_pieces = len(test_go.remove_died_pieces(opponent_type))
            if captured_pieces > max_captures:
                max_captures = captured_pieces
                best_attack_moves = [move]
            elif captured_pieces == max_captures:
                best_attack_moves.append(move)

        return best_attack_moves if max_captures > 0 else moves
    def select_best_moves(self, go, possible_moves, max_branching_factor, piece_type):
        move_scores = []
        for move in possible_moves:
            test_go = go.copy_board()
            test_go.place_chess(move[0], move[1], piece_type)
            score = self.calculate_reward(test_go, move, piece_type)
            move_scores.append((move, score))
        move_scores.sort(key=lambda x: x[1], reverse=True)
        selected_moves = [move for move, score in move_scores[:max_branching_factor]]
        return selected_moves

    def minimax(self, go, depth, maximizing_player, alpha, beta, action, piece_type, max_branching_factor):
        if depth == 0 or go.game_end(piece_type):
            return self.calculate_reward(go, action, piece_type)
        possible_moves = self.get_possible_moves(go, piece_type if maximizing_player else 3 - piece_type)
        if len(possible_moves) > max_branching_factor:
            possible_moves = self.select_best_moves(go, possible_moves, max_branching_factor, piece_type if maximizing_player else 3 - piece_type)

        if maximizing_player:
            max_value = -float('inf')
            for move in possible_moves:
                test_go = go.copy_board()
                test_go.place_chess(move[0], move[1], piece_type)
                value = self.minimax(test_go, depth - 1, False, alpha, beta, move, piece_type, max_branching_factor)
                max_value = max(max_value, value)
                alpha = max(alpha, max_value)
                if beta <= alpha:
                    break
            return max_value
        else:
            min_value = float('inf')
            for move in possible_moves:
                test_go = go.copy_board()
                test_go.place_chess(move[0], move[1], 3 - piece_type)
                value = self.minimax(test_go, depth - 1, True, alpha, beta, move, piece_type, max_branching_factor)
                min_value = min(min_value, value)
                beta = min(beta, min_value)
                if beta <= alpha:
                    break
            return min_value

    def get_possible_moves(self, go, piece_type):
        moves = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    moves.append((i, j))
        return moves

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

    def calculate_reward(self, go, action, piece_type):
        opponent_type = 3 - piece_type
        new_go = go.copy_board()
        captured_pieces=0
        lost_pieces=0
        territory = 0
        board_control=go.score(piece_type)-go.score(opponent_type)-1
        allies = []
        group_size=0
        corner_edge_control=0
        center_control=0
        ko=0
        if action != "PASS":
            new_go.place_chess(action[0], action[1], piece_type)
            captured_pieces = len(new_go.remove_died_pieces(opponent_type))
            lost_pieces = len(new_go.remove_died_pieces(piece_type))
            board_control = new_go.score(piece_type) - new_go.score(opponent_type)
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

        if new_go.game_end(piece_type, action):
            return 100 if new_go.judge_winner() == piece_type else -100

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
                if piece_type == 1:
                    opponent_atari += 25
                else:
                    opponent_atari += 5
            elif new_go.ally_dfs(i, j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) == 1:
                if piece_type == 1:
                    opponent_atari += 10
                else:
                    opponent_atari += 3
            elif new_go.ally_dfs(i,j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) > 1:
                if piece_type == 1:
                    opponent_atari -= sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.75
                else:
                    opponent_atari -= sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.1
        for i, j in allies:
            if not new_go.find_liberty(i, j):
                if piece_type == 1:
                    self_atari -= 5
                else:
                    self_atari -= 10
            elif new_go.ally_dfs(i, j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) == 1:
                if piece_type == 1:
                    self_atari -= 4
                else:
                    self_atari -= 6
            elif new_go.ally_dfs(i, j) and sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj)) > 1:
                if piece_type == 1:
                    self_atari += sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.3
                else:
                    self_atari += sum(1 for ai, aj in new_go.ally_dfs(i, j) if new_go.find_liberty(ai, aj))*0.75

        player_pieces = [(i, j) for i in range(go.size) for j in range(go.size) if go.board[i][j] == piece_type]
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
                if go.board[i][j] == 0 and self.is_eye(new_go, i, j, piece_type):
                    eyes += 1

        if piece_type == 1:
            white_potential_territory = 0
            early_game_aggression = 0
            late_game_stability = 0
            trap_bonus = 0
            sente_bonus = 0
            black_influence = self.calculate_influence(new_go, piece_type)
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

        if piece_type == 1:
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

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)