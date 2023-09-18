import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move
from bot import Bot

class Main:

  def __init__(self, bot = None, bot_depth = 0):
    pygame.init()
    self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess')
    self.game = Game()
    self.bot = bot
    self.bot_depth = bot_depth

  
  def mainloop(self):
    screen = self.screen
    game = self.game
    board = self.game.board
    dragger = self.game.dragger
    count = 0
    moves = True
    bots = len(self.bot)
    bot = {}
    for i in range(bots):
      bot[self.bot[i]] = Bot(self.bot[i],self.bot_depth[i])
    while(True):

      game.show_bg(screen)
      game.show_last_move(screen)
      game.show_moves(screen)
      game.show_pieces(screen)
      if moves:
        moves = board.get_all_moves(game.next_player)
      if board.checkmated(game.next_player,moves):
        game.show_win(screen)
      elif not moves or count == 50:
        game.show_draw(screen)
      elif dragger.dragging:
          dragger.update_blit(screen)
      pygame.display.update()
      if moves and game.next_player in bot:
        #Bot calculates the best move available
        best_move = bot[game.next_player].move(board,moves)
        p = board.squares[best_move.initial.row][best_move.initial.col].piece
        captured = board.squares[best_move.final.row][best_move.final.col].has_piece()
        #Reset the draw count if it is a pawn
        count += 0.5
        if p.name == 'pawn':
          count = 0
        #Make the move
        board.move(p, best_move)
        board.set_true_en_passant(p)
        game.play_sound(captured)
        #change the color and diplay
        game.next_turn()
      for event in pygame.event.get():
        #click
        if event.type == pygame.MOUSEBUTTONDOWN:
          dragger.update_mouse(event.pos)
          clicked_row = dragger.mouseY // SQSIZE
          clicked_col = dragger.mouseX//SQSIZE
          if board.squares[clicked_row][clicked_col].has_piece():
            piece = board.squares[clicked_row][clicked_col].piece

            #Check which color's turn
            if piece.color == game.next_player:
              board.calc_moves(piece,clicked_row,clicked_col)
              dragger.save_initial(event.pos)
              dragger.drag_piece(piece)

        #drag
        elif event.type==pygame.MOUSEMOTION:
          if dragger.dragging:
            dragger.update_mouse(event.pos)
            dragger.update_blit(screen)
        #click release
        elif event.type==pygame.MOUSEBUTTONUP:
          if dragger.dragging:
            dragger.update_mouse(event.pos)
            released_row = dragger.mouseY//SQSIZE
            released_col = dragger.mouseX//SQSIZE
            
            #create possible move
            initial = Square(dragger.initial_row,dragger.initial_col)
            final = Square(released_row,released_col)
            move = Move(initial,final)

            if board.valid_move(dragger.piece,move):
              captured = board.squares[released_row][released_col].has_piece()
              count += 0.5
              if dragger.piece.name == 'pawn':
                count = 0
              board.move(dragger.piece, move)
              board.set_true_en_passant(dragger.piece)
              game.play_sound(captured)
              #change the color and diplay
              game.next_turn()
            dragger.undrag_piece()
        elif event.type==pygame.KEYDOWN:
          if event.key==pygame.K_r:
            game.reset()
            game = self.game
            board = self.game.board
            dragger = self.game.dragger
          if event.key == pygame.K_q:
            pygame.quit()
            sys.exit()
      if event.type ==pygame.QUIT:
        pygame.quit()
        sys.exit()


main = Main(['black'],[3])
#main=Main([],[])
main.mainloop()