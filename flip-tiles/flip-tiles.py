"""
Simple memory game.
"""

import random
import sys
import pygame as pg
import pygame.locals as pglocals

SQSIZE = 80
SEP = 2
WIDTH = 6
HEIGHT = 5

DARK_GRAY = (100, 100, 100)
GRAY = (200, 200, 200)
BLUE = (120, 160, 200)
GREEN = (80, 220, 50)
RED = (220, 50, 50)

class CellStatus:
    UNCLICKED = "UNCLICKED"
    CLICKED = "CLICKED"
    CORRECT = "CORRECT"
    WRONG_CLICKED = "WRONG_CLICKED"
    WRONG_UNCLICKED = "WRONG_UNCLICKED"

BOARD_PALETTE = {
    CellStatus.UNCLICKED: GRAY,
    CellStatus.CLICKED: BLUE,
    CellStatus.CORRECT: GREEN,
    CellStatus.WRONG_CLICKED: RED,
    CellStatus.WRONG_UNCLICKED: DARK_GRAY,
}

screen = pg.display.set_mode((SQSIZE*WIDTH, SQSIZE*HEIGHT))

def draw_cell(surf, board, x, y):
    """Draws the value of a single cell of the board in the given surface."""

    rect = pg.Rect(SEP//2 + x*SQSIZE, SEP//2 + y*SQSIZE, SQSIZE-SEP, SQSIZE-SEP)
    color = BOARD_PALETTE[getattr(CellStatus, board[y][x])]
    return pg.draw.rect(surf, color, rect)

def draw_board(surf, board):
    """Draws the board onto the screen."""

    for y, row in enumerate(board):
        for x in range(len(row)):
            draw_cell(surf, board, x, y)

board = [[CellStatus.UNCLICKED for _ in range(WIDTH)] for _ in range(HEIGHT)]
draw_board(screen, board)
pg.display.flip()

while True:
    for ev in pg.event.get():
        if ev.type == pglocals.QUIT:
            pg.quit()
            sys.exit()
        elif ev.type == pglocals.MOUSEBUTTONDOWN:
            x_, y_ = ev.pos
            x, y = x_//SQSIZE, y_//SQSIZE
            board[y][x] = CellStatus.UNCLICKED if (
                board[y][x] == CellStatus.CLICKED
            ) else CellStatus.CLICKED
            pg.display.update(draw_cell(screen, board, x, y))
