import os
import sys
import random
import math
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

bomb_sound = pygame.mixer.Sound(file=r"bin\bomb.wav")
flag_sound = pygame.mixer.Sound(file=r"bin\flag.wav")
win_sound = pygame.mixer.Sound(file=r"bin\win.wav")
lose_sound = pygame.mixer.Sound(file=r"bin\gameover.wav")

IMAGE_REPO = "bin"
WIDTH_PER_CELL = 18
HEIGHT_PER_CELL = 18
SEPARATOR_WIDTH = 2
SEPARATOR_COLOUR = (255, 255, 255)

def load_image(name, transparent=False):
    """Function that handles image loading
    Returns the image and its Rect"""
    try:
        img = pygame.image.load(name)
    except pygame.error:
        raise SystemExit("Could not load image " + name)
    if not transparent:
        img = img.convert()
    img = img.convert_alpha()
    img_rect = img.get_rect()

    return img, img_rect

class Cell(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = 0
        self.state = "hidden"
        
    def set_bomb(self):
        self.value = 9
        
    def tick(self):
        self.value = self.value + 1 if self.value < 9 else 9
        
    def set_hidden(self):
        self.state = "hidden"
        self.set_image()
        
    def set_visible(self, override=False):
        if override or self.state == "hidden":
            self.state = "visible"
            self.set_image()
            if self.value == 9:
                if bomb_sound.get_num_channels() < 1:
                    bomb_sound.play()
            
        return self.value == 0
        
    def is_visible(self):
        return self.state == "visible"
        
    def is_flagged(self):
        return self.state == "flagged"
        
    def is_hidden(self):
        return self.state == "hidden"
        
    def get_number(self):
        return self.value
        
    def flip_flag(self, flags):
        if self.state == "flagged":
            flags += 1
            self.state = "hidden"
            flag_sound.play()
        elif self.state == "hidden" and flags:
            flags -= 1
            self.state = "flagged"
            flag_sound.play()
        self.set_image()
        return flags
    
    def is_bomb(self):
        return self.value == 9
        
    def set_image(self):
        if self.state in ["hidden", "flagged"]:
            self.image = image_dict[self.state]
        else:
            self.image = image_dict[self.value]
        
    def __str__(self):
        return "<Cell @{}>".format(self.value)
        
    def __repr__(self):
        return self.__str__()
        
class Board(object):
    def __init__(self, size, frame):
        self.frame = frame
        self.size = size
        self.board = [[None for i in range(size)] for j in range(size)]
        for r in range(size):
            for c in range(size):
                self.board[r][c] = Cell(c, r)
                self.board[r][c].set_hidden()
        self.is_populated = False
                
    def populate(self, click_pos):
        invalid_positions = [click_pos] + \
                            self.get_neighbour_coords(click_pos)
        placed = []
        side = self.size
        while len(placed) < self.bombs:
            pos = (random.randint(0, side-1), random.randint(0, side-1))
            # check for duplicates
            if pos in placed or pos in invalid_positions:
                continue
            else:
                placed.append(pos)
                
            self.board[pos[0]][pos[1]].set_bomb()
            neighbs = self.get_neighbour_coords(pos)
            for coords in neighbs:
                self.board[coords[0]][coords[1]].tick()
                
    def init_GUI(self):
        y = 0
        for i in range(self.size+1):
            x = i * (WIDTH_PER_CELL + SEPARATOR_WIDTH)
            pygame.draw.line(self.frame, SEPARATOR_COLOUR, (x, y),
                            (x, HEIGHT), SEPARATOR_WIDTH)
                    
        x = 0
        for j in range(self.size+1):
            y = j * (WIDTH_PER_CELL + SEPARATOR_WIDTH)
            pygame.draw.line(self.frame, SEPARATOR_COLOUR, (x, y),
                            (WIDTH, y), SEPARATOR_WIDTH)
                            
    def draw(self):
        x_spacing = WIDTH_PER_CELL + SEPARATOR_WIDTH
        y_spacing = HEIGHT_PER_CELL + SEPARATOR_WIDTH
        for i in range(self.size):
            for j in range(self.size):
                x = SEPARATOR_WIDTH + i*x_spacing
                y = SEPARATOR_WIDTH + j*y_spacing
                self.frame.blit(self.board[i][j].image, (x,y))
                
    def left_click(self, pos):
        x, y = self.get_indexes(pos)
        self.show(x, y)
                
    def show(self, x, y):
        if not self.is_populated:
            self.populate((x, y))
            self.is_populated = True
    
        # do nothing if we want to open a flag
        if self.board[x][y].is_flagged():
            return
            
        show_more = self.board[x][y].set_visible()
        if self.board[x][y].is_bomb():
            self.lose_game()
        
        shown = [(x,y)]
        if show_more:
            to_show = self.get_neighbour_coords((x,y))
            while to_show:
                pos = to_show[0]
                shown.append(pos)
                to_show = to_show[1:]
                show_more = self.board[pos[0]][pos[1]].set_visible()
                if show_more:
                    neighbs = self.get_neighbour_coords(pos)
                    for neighb in neighbs:
                        if neighb not in shown and neighb not in to_show:
                            to_show.append(neighb)
        
        self.check_if_win()
        
    def right_click(self, pos):
        x, y = self.get_indexes(pos)
        
        # should we clear surrounding cells or clear flags?
        if self.board[x][y].is_visible():
            self.clear(x, y)
        else:
            self.flag(x, y)
            
    def flag(self, x, y):
        self.flags = self.board[x][y].flip_flag(self.flags)
        
        self.check_if_win()
        
    def clear(self, x, y):
        num = self.board[x][y].get_number()
        if 1 <= num <= 8:
            neighbs = self.get_neighbour_coords((x,y))
            count = 0
            for (x, y) in neighbs:
                if self.board[x][y].is_flagged():
                    count += 1
            if count == num:
                for neighb in neighbs:
                    self.show(*neighb)
        
    def check_if_win(self):
        if self.flags == 0:
            count = 0
            for i in range(self.size):
                for j in range(self.size):
                    if self.board[i][j].state == "visible":
                        count += 1
            if count == self.size*self.size - self.bombs:
                self.win_game()
        
    def get_indexes(self, pos):
        x_, y_ = pos
        x = math.floor(x_ / (WIDTH_PER_CELL + SEPARATOR_WIDTH))
        y = math.floor(y_ / (HEIGHT_PER_CELL + SEPARATOR_WIDTH))
        
        return (x, y)
                
    def get_neighbour_coords(self, pos):
        side = self.size
        neighbours = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                neighbours.append((pos[0]+i, pos[1]+j))
        ## remove itself
        neighbours.pop(neighbours.index(pos))
        
        ## find all the pairs which are too far to the left/right
        ## or to far to the top/bottom i.e. out of board
        to_remove = [i for i in range(len(neighbours))
                if (-1 in neighbours[i] or side in neighbours[i])]
        while to_remove:
            neighbours.pop(to_remove.pop())
            
        return neighbours
        
    def lose_game(self):
        global to_play
        to_play = False
        print("You lost!!")
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j].is_bomb():
                    self.board[i][j].set_visible(override=True)
        pygame.display.set_caption("You lost!! :(")
        pygame.mixer.fadeout(1000)
        lose_sound.play()
                    
    def win_game(self):
        global to_play
        to_play = False
        print("You won!!")
        pygame.display.set_caption("You won!! :)")
        win_sound.play()
        
    def __str__(self):
        s = ""
        for line in self.board:
            s += str(line) + "\n"
        return s
            
n = 20
        
WIDTH = n * WIDTH_PER_CELL + (n+1) * SEPARATOR_WIDTH
HEIGHT = n * HEIGHT_PER_CELL + (n+1) * SEPARATOR_WIDTH
screen = pygame.display.set_mode((WIDTH, HEIGHT))

image_dict = {}
for i in range(1, 9):
    imagepath = os.path.join(IMAGE_REPO, str(i)+".png")
    image, rect = load_image(imagepath)
    image_dict[i] = image
image, rect = load_image(os.path.join(IMAGE_REPO, "bomb.png"))
image_dict[9] = image
image, rect = load_image(os.path.join(IMAGE_REPO, "background.png"))
image_dict[0] = image
image, rect = load_image(os.path.join(IMAGE_REPO, "flag.png"))
image_dict["flagged"] = image
image, rect = load_image(os.path.join(IMAGE_REPO, "hidden.png"))
image_dict["hidden"] = image

b = Board(n, screen)
b.bombs = int(n*n*0.2)
b.flags = b.bombs

b.init_GUI()

to_play = True

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        ## button == 1 is the left button and 3 is the right one
        elif to_play and ev.type == MOUSEBUTTONDOWN:
            if ev.button == 1:
                b.left_click(ev.pos)
            elif ev.button == 3:
                b.right_click(ev.pos)
        
    b.draw()
    pygame.display.update()