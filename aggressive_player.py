from host import GO
from read import readInput
from write import writeOutput
from copy import deepcopy

class CapturePlayer:
    def __init__(self, type='capture'):
        self.type = type  # Player type identifier

    def get_input(self, go, piece_type):
        """
        Get the best move that maximizes captured stones looking two moves ahead.
        
        :param go: GO game instance
        :param piece_type: 1('X') or 2('O')
        :return: tuple (action, i, j) where action is "MOVE" or "PASS"
        """
        # Get all possible moves
        possible_moves = self.get_possible_moves(go, piece_type)
        
        if not possible_moves:
            return ("PASS", None, None)

        # Evaluate each move based on maximum stones captured in two moves
        best_move = None
        max_captures = -1
        
        for move in possible_moves:
            i, j = move
            # Simulate first move
            test_go = deepcopy(go)
            if test_go.place_chess(i, j, piece_type):
                captured = len(test_go.remove_died_pieces(3 - piece_type))
                
                # Look ahead one more move
                opponent_moves = self.get_possible_moves(test_go, 3 - piece_type)
                for opp_move in opponent_moves:
                    opp_i, opp_j = opp_move
                    test_go2 = deepcopy(test_go)
                    test_go2.place_chess(opp_i, opp_j, 3 - piece_type)
                    test_go2.remove_died_pieces(piece_type)
                    
                    # Try our second move
                    our_moves = self.get_possible_moves(test_go2, piece_type)
                    for second_move in our_moves:
                        second_i, second_j = second_move
                        test_go3 = deepcopy(test_go2)
                        if test_go3.place_chess(second_i, second_j, piece_type):
                            second_captured = len(test_go3.remove_died_pieces(3 - piece_type))
                            total_captured = captured + second_captured
                            
                            if total_captured > max_captures:
                                max_captures = total_captured
                                best_move = (i, j)

        if best_move is None or max_captures == 0:
            return "PASS"
        
        return best_move

    def get_possible_moves(self, go, piece_type):
        """
        Get all valid moves for the given piece type.
        
        :param go: GO game instance
        :param piece_type: 1('X') or 2('O')
        :return: list of (i, j) coordinates
        """
        moves = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type):
                    moves.append((i, j))
        return moves

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = CapturePlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)