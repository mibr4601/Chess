import math
import copy
from const import *
from piece import *
import random
from move import Move
class Bot:
  def __init__(self, color, depth):
        """
        Contructor for a SmartBot object.

        Inputs:
            depth: int : recursion depth for minmax algorithm
            color: str : the color or player name the bot will be controlling
        """
        self.depth = depth
        self.color = color
        self.transposition_table = {}
        self.zobrist_keys = [[random.getrandbits(64) for _ in range(12)] for _ in range(64)]
        if color == 'white':
            self.opponent = 'black'
        else:
            self.opponent = 'white'
  
  def generate_position_key(self, board,color):
      key = 0
      for row in range(8):
          for col in range(8):
              if board.squares[row][col].piece:
                  piece = board.squares[row][col].piece
                  piece_index = self.get_piece_index(piece)
                  key ^= self.zobrist_keys[row * 8 + col][piece_index]

      if color == 'black':
          key ^= self.zobrist_keys[-1][1]  # XOR with a random key for black's turn

      return key
  def get_piece_index(self, piece):
        # Map chess pieces to indices (e.g., pawn = 0, knight = 1, ...).
        # You may need to adjust this based on your piece representation.
        piece_map = {
            'pawn': 0, 'knight': 1, 'bishop': 2, 'rook': 3, 'queen': 4, 'king': 5
        }
        if piece.color == 'black':
            return piece_map[piece.name] + 6
        return piece_map[piece.name]

  
  def generate_boards_move(self, board, moves):
        moves_boards = []
        for move in moves:
            #Performs a deep copy of the board, faster than copy.deepcopy()
            result_board = copy.deepcopy(board)
            result_board.move(move.initial.piece,move)
            moves_boards.append([move, result_board])
        return moves_boards

  
  def heuristic(self, board):
    # Define weights for the heuristic factors
    # Initialize scores for each side
    white_score = 0
    black_score = 0

    # Define the center squares
    center_square = (3.5,3.5)

    for row in range(8):
        for col in range(8):
            if not board.squares[row][col].piece:
                continue
            piece = board.squares[row][col].piece

            # Calculate piece value
            if piece.color == 'white':
                white_score += piece.value
            else:
                black_score += piece.value

            # Calculate center control bonus
            dist = math.dist((row, col), center_square)
            center_bonus = (1.0 / (1.0 + dist))
            dev = 0
            if col ==4 or col == 3 and piece.name =='pawn':
                center_bonus*=7
            if col ==5 or col == 2 and piece.name =='pawn':
                center_bonus*=2
            if piece.name!='knight' or piece.name=='bishop':
                #Incentivizing development
                dev += .5 * len(board.get_piece_moves(piece))
                center_bonus*=-.5
            elif piece.name=='queen' or piece.name== 'rook':
                center_bonus*= -10
                dev += .25 * len(board.get_piece_moves(piece))
            elif piece.name =='king':
                center_bonus*=-10
            
            if piece.color == 'white':
                white_score += center_bonus + dev
            else:
                black_score += center_bonus + dev

    # Calculate the total score
    if self.color == 'white':
        total_score = white_score - black_score
    else:
        total_score = black_score - white_score
    
    return total_score

  def move(self, board, moves):
    best_move = (None, math.inf * -1)
    # Generate all possible moves and choose best one
    board_moves = self.generate_boards_move(board,moves)
    for item in board_moves:
        move = item[0]
        new_board = item[1]
        priority = self.minimax(new_board, self.depth, math.inf * -1,
                                math.inf,False)
        if priority > best_move[1]:
            best_move = (move, priority)
        print(best_move[1],best_move[0].initial.piece)
    return best_move[0]


  def get_all_moves(self,board,color):
      moves = []
      for row in range(ROWS):
          for col in range(COLS):
              if not board.squares[row][col].has_team_piece(color):
                  continue
              piece = copy.deepcopy(board.squares[row][col].piece)
              piece.moves = []
              board.calc_moves(piece,row,col)
              moves = moves + piece.moves
      return moves
  
  def minimax(self, board, depth, alpha, beta,maximizingplayer):
    # Base case
    if maximizingplayer:
        color = self.color
    else:
        color = self.opponent
    position_key = self.generate_position_key(board,color)

    # Check if the current position is in the transposition table.
    if position_key in self.transposition_table:
        entry = self.transposition_table[position_key]
        if entry['depth'] >= depth:
            if entry['flag'] == 'exact':
                return entry['value']
            elif entry['flag'] == 'lower_bound':
                alpha = max(alpha, entry['value'])
            elif entry['flag'] == 'upper_bound':
                beta = min(beta, entry['value'])
            if alpha >= beta:
                return entry['value']
    if depth == 0:
      return self.heuristic(board)
    if maximizingplayer:
        moves = self.get_all_moves(board,self.color)
        if not moves:
            return self.heuristic(board)
        
        value = -math.inf
        for move in moves:
            new_board = copy.deepcopy(board)
            new_board.move(move.initial.piece,move,True)  # Make the move on a hypothetical board
            value = max(value, self.minimax(new_board, depth - 1, False, 
                            alpha, beta))
            if value > beta:
                flag = 'exact' if (value <= alpha) else ('upper_bound' if value >= beta else 'lower_bound')
                self.transposition_table[position_key] = {'value': value, 'depth': depth, 'flag': flag}
                break
            alpha = max(alpha, value)
        #undoing the move
        return value
    else:
        moves = self.get_all_moves(board,self.opponent)
        if not moves:
            return self.heuristic(board)

        value = math.inf
        for move in moves:
            initial_piece = move.initial.piece
            final_piece = move.final.piece
            board.move(move.initial.piece,move,True)   # Make the move on a hypothetical board
            value = min(value, self.minimax(board, depth - 1, True, alpha, beta))
            undo = Move(move.final,move.initial)
            board.move(initial_piece,undo,True)
            board.squares[undo.initial.row][undo.initial.col].piece = final_piece
            if value < alpha:
                flag = 'exact' if (value <= alpha) else ('upper_bound' if value >= beta else 'lower_bound')
                self.transposition_table[position_key] = {'value': value, 'depth': depth, 'flag': flag}
                break
            beta=min(beta,value)
        return value
