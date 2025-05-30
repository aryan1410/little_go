import sys
from read import readInput
from write import writeOutput
from host import GO

class AlphaBetaPlayer():
    def __init__(self):
        self.type = 'alphabeta'

    def get_input(self, go, piece_type):
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))

        print(f"Possible placements: {possible_placements}")  # Debug print

        if not possible_placements:
            print("No possible placements. Returning PASS.")  # Debug print
            return "PASS"
        else:
            # Use Minimax with alpha-beta pruning to find the best move
            best_move = possible_placements[0]  # Default to the first valid move
            best_value = -float('inf')
            alpha = -float('inf')
            beta = float('inf')
            for move in possible_placements:
                test_go = go.copy_board()
                test_go.place_chess(move[0], move[1], piece_type)
                value = self.minimax(test_go, 2, False, alpha, beta, piece_type)
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, best_value)

            print(f"Best move: {best_move}")  # Debug print
            return best_move

    def minimax(self, go, depth, maximizing_player, alpha, beta, piece_type):
        '''
        Minimax algorithm with alpha-beta pruning.

        :param go: Go instance.
        :param depth: current depth of the search.
        :param maximizing_player: True if maximizing, False if minimizing.
        :param alpha: alpha value for pruning.
        :param beta: beta value for pruning.
        :param piece_type: 1('X') or 2('O').
        :return: heuristic value of the board.
        '''
        if depth == 0 or go.game_end(piece_type):
            return self.evaluate_board(go, piece_type)

        if maximizing_player:
            max_value = -float('inf')
            for move in self.get_possible_moves(go, piece_type):
                test_go = go.copy_board()
                test_go.place_chess(move[0], move[1], piece_type)
                value = self.minimax(test_go, depth - 1, False, alpha, beta, piece_type)
                max_value = max(max_value, value)
                alpha = max(alpha, max_value)
                if beta <= alpha:
                    break
            return max_value
        else:
            min_value = float('inf')
            for move in self.get_possible_moves(go, 3 - piece_type):
                test_go = go.copy_board()
                test_go.place_chess(move[0], move[1], 3 - piece_type)
                value = self.minimax(test_go, depth - 1, True, alpha, beta, piece_type)
                min_value = min(min_value, value)
                beta = min(beta, min_value)
                if beta <= alpha:
                    break
            return min_value

    def get_possible_moves(self, go, piece_type):
        '''
        Get all possible moves for a given piece type.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: list of possible moves.
        '''
        moves = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    moves.append((i, j))
        return moves

    def evaluate_board(self, go, piece_type):
        '''
        Evaluate the board for a given piece type.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: heuristic value of the board.
        '''
        # Heuristic: difference in the number of stones
        return go.score(piece_type) - go.score(3 - piece_type)

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = AlphaBetaPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)