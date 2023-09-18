import os
class Piece:

  def __init__(self,name,color,value,texture=None,texture_rect=None):
    self.name = name
    self.color = color
    self.value = value
    self.moves=[]
    self.moved = False
    self.set_texture()
    self.texture_rect = texture_rect
  def set_texture(self,size=80):
    self.texture=os.path.join(
      f'assets/images/imgs-{size}px/{self.color}_{self.name}.png'
    )
  def add_move(self,move):
    self.moves.append(move)
  def clear_moves(self):
    self.moves = []
class Pawn(Piece):
  def __init__(self,color):
    self.dir = 1
    if color =='white':
      self.dir = -1
    self.en_passant = False
    super().__init__('pawn', color, 10.0)
class Knight(Piece):
  def __init__(self,color):
    super().__init__('knight', color, 32.0)
class Bishop(Piece):
  def __init__(self,color):
    super().__init__('bishop', color, 31.0)
class Rook(Piece):
  def __init__(self,color):
    super().__init__('rook', color, 50.0)
class Queen(Piece):
  def __init__(self,color):
    super().__init__('queen', color, 90.0)
class King(Piece):
  def __init__(self,color):
    self.left_rook = None
    self.right_rook = None
    super().__init__('king', color, 1000)