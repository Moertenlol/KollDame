import pygame
import pygame.freetype
from pygame.locals import *

pygame.init()

class Board:
    def __init__(self):
        self.__board = []

    def create_board(self):
        self.__board = [[0] * cols for _ in range(rows)]
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    self.__board[i][j] = 'orange'
                    pygame.draw.rect(screen, (255, 140, 0), (boardmiddlewidth + (i - 4) * tilesize, boardmiddleheight + (j - 4) * tilesize, tilesize, tilesize), 0)
                else:
                    self.__board[i][j] = 'brown'
                    pygame.draw.rect(screen, (139, 69, 19), (boardmiddlewidth + (i - 4) * tilesize, boardmiddleheight + (j - 4) * tilesize, tilesize, tilesize))
        pygame.display.flip()

class Pieces:
    def __init__(self, color, x, y, id):
        self.color = color
        self.position = [x, y]
        self.queen = False
        self.selected = False
        self.pieceid = id

    def draw_piece(self):
        if self.color == 'white':
            pygame.draw.circle(screen, (255, 255, 255), (boardmiddlewidth + (self.position[0] - 4) * tilesize + tilesize // 2, boardmiddleheight + (self.position[1] - 4) * tilesize + tilesize // 2), piecesize * 5)
        else:
            pygame.draw.circle(screen, (0, 0, 0), (boardmiddlewidth + (self.position[0] - 4) * tilesize + tilesize // 2, boardmiddleheight + (self.position[1] - 4) * tilesize + tilesize // 2), piecesize * 5)
        pygame.display.flip()

    def getpieceinfo(self):
        return self.color, self.position, self.queen, self.selected, self.pieceid

display = pygame.display.Info()
screen = pygame.display.set_mode((display.current_w, display.current_h - 60), 0, 0, 0)
pygame.display.set_caption('Checkers')
pygame.display.set_icon(pygame.image.load('icon.jpg'))
screen.fill((255, 255, 255))

tilesize = display.current_h // 11
boardmiddleheight = display.current_h // 2
boardmiddlewidth = display.current_w // 2

rows, cols = (8, 8)
positions = [[0 for i in range(8)] for j in range(8)]
pieceswhite = []
piecesblack = []

currentboard = Board()
currentboard.create_board()

piecesize = tilesize // 10

def makepieces(color, start_id, offset):
    pieces = []
    for i in range(12):
        j = i * 2 + 1
        k = j // 8
        j -= 8 * k
        pieces.append(Pieces(color, 7 - j if color == 'white' else j, 7 - k if color == 'white' else k, start_id + i))
    return pieces

pieceswhite = makepieces('white', 1, 0)
piecesblack = makepieces('black', 13, 0)

piecesonboard = pieceswhite + piecesblack
for i in piecesonboard:
    i.draw_piece()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    timer = pygame.time.get_ticks() // 10
    timer = str(timer // 60) + ':' + str(timer % 60)
    pygame.freetype.init()
    font = pygame.font.SysFont('Consolas', 30)
    text_surface = font.render(str(timer), False, (100, 100, 100))
    pygame.draw.rect(screen, (255, 255, 255), (boardmiddlewidth - 20, 50, 200, 50))
    screen.blit(text_surface, (boardmiddlewidth - 20, 50), (0, 0, 200, 50), 0)
    pygame.display.flip()