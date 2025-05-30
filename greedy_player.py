from read import readInput
from write import writeOutput
from host import GO

class GreedyPlayer():
    def __init__(self):
        self.type = 'greedy'

    def get_input(self, go, piece_type):
        '''
        Get one input using a greedy strategy to maximize captured enemy stones.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))

        if not possible_placements:
            return "PASS"
        else:
            # Evaluate each possible move based on the number of enemy stones captured
            best_move = None
            max_captured = -1
            for move in possible_placements:
                captured = self.evaluate_captured_stones(go, move, piece_type)
                if captured > max_captured:
                    max_captured = captured
                    best_move = move
            return best_move

    def evaluate_captured_stones(self, go, move, piece_type):
        '''
        Evaluate the number of enemy stones captured by a move.

        :param go: Go instance.
        :param move: (row, column) coordinate of the move.
        :param piece_type: 1('X') or 2('O').
        :return: number of enemy stones captured.
        '''
        i, j = move
        # Create a copy of the board to simulate the move
        test_go = go.copy_board()
        test_go.place_chess(i, j, piece_type)
        # Remove dead pieces of the opponent
        died_pieces = test_go.remove_died_pieces(3 - piece_type)
        return len(died_pieces)

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = GreedyPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)