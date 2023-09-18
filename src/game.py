import pygame
from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
class Game:

  def __init__(self):
    self.board = Board()
    self.dragger = Dragger()
    self.next_player='white'
    self.config=Config()

  #Show methods
  
  def show_bg(self,surface):
    for row in range(ROWS):
      for col in range(COLS):
        if (row + col) % 2 == 0:
          color = (235,235,200)
        else:
          color = (119, 154, 88)
        rect = (col*SQSIZE, row*SQSIZE,SQSIZE,SQSIZE)
        pygame.draw.rect(surface, color, rect)
        if col == 0:
          # color
          color = (235,235,200) if row % 2 != 0 else (119, 154, 88)
          lbl = self.config.font.render(str(ROWS-row), 1, color)
          lbl_pos = (5, 5+row*SQSIZE)
          # blit
          surface.blit(lbl, lbl_pos)
        if row == 7:
            # color
            color = color = (235,235,200) if (row + col) % 2 != 0 else (119, 154, 88)
            # label
            lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
            lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
            # blit
            surface.blit(lbl, lbl_pos)
  
  def show_pieces(self,surface):
    for row in range(ROWS):
      for col in range(COLS):
        if self.board.squares[row][col].has_piece():
          piece = self.board.squares[row][col].piece
          #all pieces but the one being dragged
          if piece is not self.dragger.piece:
            img = pygame.image.load(piece.texture)
            img_center = col*SQSIZE + SQSIZE//2,row*SQSIZE+SQSIZE//2
            piece.texture_rect = img.get_rect(center = img_center)
            surface.blit(img,piece.texture_rect)
  
  def show_moves(self, surface):
    if self.dragger.dragging:
      piece = self.dragger.piece
      for move in piece.moves:
        color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646'
        rect = (move.final.col * SQSIZE,move.final.row*SQSIZE,SQSIZE,SQSIZE)
        pygame.draw.rect(surface,color,rect)

  def show_last_move(self,surface):
    if self.board.last_move:
      initial = self.board.last_move.initial
      final = self.board.last_move.final
      for pos in [initial,final]:
        color = (244,247,116) if (pos.row+pos.col)%2==0 else(172,195,51)
        rect = (pos.col*SQSIZE,pos.row*SQSIZE,SQSIZE,SQSIZE)
        pygame.draw.rect(surface,color,rect)
  
  def show_win(self,surface):
    color = (255,0,0)
    if self.next_player == 'white':
      lbl = self.config.font.render("Black won", 3, color)
    else:
      lbl = self.config.font.render("White won", 3, color)

    lbl_pos = (WIDTH//2, HEIGHT//2)
    #blit
    
    surface.blit(lbl, lbl_pos)
    lbl = self.config.font.render("Press r to play again and q to quit", 15, color)
    lbl_pos = (WIDTH//2, HEIGHT//2+15)
    #blit
    surface.blit(lbl, lbl_pos)
  def show_draw(self,surface):
    color = (255,0,0)
    lbl = self.config.font.render("Draw", 3, color)
    lbl_pos = (WIDTH//2, HEIGHT//2)
    #blit
    surface.blit(lbl, lbl_pos)
    lbl = self.config.font.render("Press r to play again and q to quit", 15, color)
    lbl_pos = (WIDTH//2, HEIGHT//2+15)
    #blit
    surface.blit(lbl, lbl_pos)

  def next_turn(self):
    self.next_player = 'white' if self.next_player == 'black' else 'black'
  
  def play_sound(self,captured=False):
    if captured:
      self.config.capture_sound.play()
    else:
      self.config.move_sound.play()
  def reset(self):
    self.__init__()

