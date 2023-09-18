from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
def custom_sort_key(move):
    # Moves where move.final.piece is True get higher priority (lower sort key)
    return not move.final.piece
class Board:

  def __init__(self):
    self.squares=[[0,0,0,0,0,0,0,0] for col in range(COLS)]
    self.last_move=None
    self._create()
    self._add_pieces('white')
    self._add_pieces('black')

  def move(self,piece,move,testing=False):
    initial=move.initial
    final=move.final
    en_passant_empty = self.squares[final.row][final.col].isempty()
    #console update
    if self.squares[final.row][final.col].piece and self.squares[final.row][final.col].piece.name == 'king':
      return
    self.squares[initial.row][initial.col].piece = None
    self.squares[final.row][final.col].piece=piece

    #pawn promotion
    if isinstance(piece,Pawn):
      diff = final.col - initial.col
      if diff != 0 and en_passant_empty:
        self.squares[initial.row][initial.col + diff].piece = None
        self.squares[final.row][final.col].piece = piece
        if not testing:
            sound = Sound(
                os.path.join('assets/sounds/capture.wav'))
            sound.play()
      else:
        self.check_promotion(piece,final)
    if isinstance(piece,King):
      if self.castling(initial,final) and not testing:
        diff = final.col - initial.col
        rook = piece.left_rook if (diff < 0) else piece.right_rook
        if rook:
          self.move(rook, rook.moves[-1])

    piece.moved = True
    piece.clear_moves()
    self.last_move = move


  def get_all_moves(self,color):
    moves = []
    for row in range(ROWS):
      for col in range(COLS):
        if self.squares[row][col].has_team_piece(color):
          piece = self.squares[row][col].piece
          piece.moves = []
          self.calc_moves(piece,row,col)
          moves = moves + piece.moves
    return sorted(moves, key=custom_sort_key)

  def get_piece_moves(self,piece):
    return piece.moves
      
  def any_move(self,color):
    for row in range(ROWS):
      for col in range(COLS):
        if self.squares[row][col].has_team_piece(color):
          piece = self.squares[row][col].piece
          if piece.moves:
            return True
    return False

  def valid_move(self,piece,move): 
    return move in piece.moves
  def check_promotion(self,piece,final):
    if final.row==0 or final.row==7:
      self.squares[final.row][final.col].piece=Queen(piece.color)
  def checkmated(self, color,moves):
    if not moves:
      enemy_color = 'white' if color == 'black' else 'black'
      for row in range(ROWS):
        for col in range(COLS):
          if self.squares[row][col].has_team_piece(enemy_color):
            p = self.squares[row][col].piece
            self.calc_moves(p,row,col,False)
            for m in p.moves:
              if isinstance(m.final.piece,King) and m.final.piece.color ==color:
                return True
    return False
  def castling(self,initial,final):
    return abs(initial.col-final.col)==2
  def set_true_en_passant(self, piece):
        
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True
  def in_check(self,piece,move):
    temp_piece = copy.deepcopy(piece)
    temp_board = copy.deepcopy(self)
    temp_board.move(temp_piece,move,True)

    for row in range(ROWS):
      for col in range(COLS):
        if temp_board.squares[row][col].has_enemy_piece(piece.color):
          p = temp_board.squares[row][col].piece
          temp_board.calc_moves(p,row,col,False)
          for m in p.moves:
            if isinstance(m.final.piece,King):
              return True
    return False
  def calc_moves(self,piece,row,col,bool = True):
    #Calculate all valid moves of a specific piece in a position
    def pawn_moves():
      steps = 1 if piece.moved else 2

      #vertical moves
      start = row + piece.dir
      end = row + (piece.dir*(1+steps))
      for move_row in range(start,end,piece.dir):
        if Square.in_range(move_row):
          if self.squares[move_row][col].isempty():
            initial = Square(row,col,self.squares[row][col].piece)
            final = Square(move_row,col)
            move = Move(initial,final)
            if bool:
              if not self.in_check(piece, move):
                piece.add_move(move)
            else:piece.add_move(move)
          else:
            break
        else:
          break
      #diagonal moves
      move_row = row+piece.dir
      move_cols = [col-1,col+1]
      for move_col in move_cols:
        if Square.in_range(move_row,move_col):
          if self.squares[move_row][move_col].has_enemy_piece(piece.color):
            initial = Square(row,col,self.squares[row][col].piece)
            final_piece=self.squares[move_row][move_col].piece
            final = Square(move_row,move_col,final_piece)

            move = Move(initial,final)
            if bool:
              if not self.in_check(piece, move):
                piece.add_move(move)
            else:piece.add_move(move)
      #en passant
      r=3 if piece.color == 'white' else 4
      fr = 2 if piece.color == 'white' else 5
      # left en passant
      if Square.in_range(col-1) and row == r:
          if self.squares[row][col-1].has_enemy_piece(piece.color):
              p = self.squares[row][col-1].piece
              if isinstance(p, Pawn):
                  if p.en_passant:
                      # create initial and final move squares
                      initial = Square(row, col,self.squares[row][7].piece)
                      final = Square(fr, col-1, p)
                      # create a new move
                      move = Move(initial, final)
                      
                      # check potential checks
                      if bool:
                          if not self.in_check(piece, move):
                              # append new move
                              piece.add_move(move)
                      else:
                          # append new move
                          piece.add_move(move)
      
      # right en pessant
      if Square.in_range(col+1) and row == r:
          if self.squares[row][col+1].has_enemy_piece(piece.color):
              p = self.squares[row][col+1].piece
              if isinstance(p, Pawn):
                  if p.en_passant:
                      # create initial and final move squares
                      initial = Square(row, col,self.squares[row][7].piece)
                      final = Square(fr, col+1, p)
                      # create a new move
                      move = Move(initial, final)
                      
                      # check potencial checks
                      if bool:
                          if not self.in_check(piece, move):
                              # append new move
                              piece.add_move(move)
                      else:
                          # append new move
                          piece.add_move(move)

    def knight_moves():
      possible_moves=[(row-2,col+1),(row - 2,col-1),
                      (row+2,col-1),(row+2,col+1)
                      ,(row+1,col+2),(row-1,col+2)
                      ,(row+1,col-2),(row-1,col-2)]
      for possible in possible_moves:
        possible_row,possible_col = possible
        if Square.in_range(possible_row,possible_col):
          if self.squares[possible_row][possible_col].isempty_or_enemy(piece.color):
            #create new squares for move
            initial = Square(row,col,self.squares[row][col].piece)
            final_piece=self.squares[possible_row][possible_col].piece

            final = Square(possible_row,possible_col,final_piece)
            #perform new move
            move = Move(initial, final)
            if bool:
              if not self.in_check(piece, move):
                piece.add_move(move)
            else:piece.add_move(move)
    def straightline_moves(incrs):
      for incr in incrs:
        row_incr,col_incr = incr
        move_row = row + row_incr
        move_col = col + col_incr

        while True:
          if Square.in_range(move_row,move_col):
            initial = Square(row,col, self.squares[row][col].piece)
            final_piece=self.squares[move_row][move_col].piece
            final = Square(move_row,move_col,final_piece)
            move = Move(initial,final)
            if self.squares[move_row][move_col].isempty():
              if bool:
                if not self.in_check(piece, move):
                  piece.add_move(move)
              else:piece.add_move(move)
            elif self.squares[move_row][move_col].has_enemy_piece(piece.color):
              if bool:
                if not self.in_check(piece, move):
                  piece.add_move(move)
              else:piece.add_move(move)
              break
            else:
              break
            move_row,move_col = move_row + row_incr, move_col + col_incr
          else:
            break
    def king_moves():
      adjs=[(row-1,col-1),(row -1, col+1),(row-1,col),
            (row+1,col-1),(row +1, col+1),(row+1,col),
            (row,col-1),(row, col+1)]
      for adj in adjs:
        move_row, move_col = adj
        if Square.in_range(move_row,move_col):
          if self.squares[move_row][move_col].isempty_or_enemy(piece.color):
            #create new squares for move
            initial = Square(row,col,self.squares[row][col].piece)
            final = Square(move_row,move_col,self.squares[move_row][move_col].piece)
            #perform new move
            move = Move(initial, final)
            if bool:
              if not self.in_check(piece, move):
                piece.add_move(move)
            else:piece.add_move(move)
      if not piece.moved:
        #queen castle
        left_rook = self.squares[row][0].piece
        if left_rook and not left_rook.moved:
          for c in range(1,4):
            if self.squares[row][c].has_piece():
              break
            if c==3:
              #adds left rook to king to move both
              piece.left_rook = left_rook
              initial = Square(row,0,self.squares[row][0].piece)
              final=Square(row,3)
              movek = Move(initial,final)
              initial = Square(row,4,self.squares[row][4].piece)
              final=Square(row,2)
              mover = Move(initial,final)
              if bool:
                if not self.in_check(piece, movek) and not self.in_check(left_rook,mover):
                  piece.add_move(movek)
                  left_rook.add_move(mover)

              else:
                piece.add_move(movek)
                left_rook.add_move(mover)
        right_rook = self.squares[row][7].piece
        if right_rook and not right_rook.moved:
          for c in range(5,7):
            if self.squares[row][c].has_piece():
              break
            if c==6:
              #adds left rook to king to move both
              piece.right_rook = right_rook
              initial = Square(row,7,self.squares[row][7].piece)
              final=Square(row,5)
              mover = Move(initial,final)
              right_rook.add_move(move)
              initial = Square(row,4,self.squares[row][4].piece)
              final=Square(row,6)
              movek = Move(initial,final)
              if bool:
                if not self.in_check(piece, movek) and not self.in_check(right_rook,mover):
                  piece.add_move(movek)
                  right_rook.add_move(mover)

              else:
                piece.add_move(movek)
                right_rook.add_move(mover)
    if isinstance(piece,Pawn):
      pawn_moves()
    elif isinstance(piece,Knight):
      knight_moves()
    elif isinstance(piece,Bishop):
      straightline_moves([(-1,-1),(1,1),(1,-1),(-1,1)])
    elif isinstance(piece,Rook):
      straightline_moves([(1,0),(0,1),(0,-1),(-1,0)])
    elif isinstance(piece,Queen):
      straightline_moves([(-1,-1),(1,1),(1,-1),(-1,1),(1,0),(0,1),(0,-1),(-1,0)])
    elif isinstance(piece,King):
      king_moves()

  def _create(self):
    for row in range(ROWS):
      for col in range(COLS):
        self.squares[row][col] = Square(row, col)

  def _add_pieces(self,color):
    row_pawn,row_other = (6,7) if color == 'white' else (1,0)
    #pawns
    for col in range(COLS):
      self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
    #knights
    self.squares[row_other][1] = Square(row_pawn, col, Knight(color))
    self.squares[row_other][6] = Square(row_pawn, col, Knight(color))
    #bishops
    self.squares[row_other][2] = Square(row_pawn, col, Bishop(color))
    self.squares[row_other][5] = Square(row_pawn, col, Bishop(color))
    #Rooks
    self.squares[row_other][0] = Square(row_pawn, col, Rook(color))
    self.squares[row_other][7] = Square(row_pawn, col, Rook(color))
    #Queen
    self.squares[row_other][3] = Square(row_pawn, col, Queen(color))
    #King
    self.squares[row_other][4] = Square(row_pawn, col, King(color))
