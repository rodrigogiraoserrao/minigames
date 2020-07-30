import random
import pygame
from pygame.locals import *
import sys

try:
    from HueHueConfig import *
except Exception:
    TILE_WIDTH = 40
    TILE_HEIGHT = 60
    WIDTH = 5
    HEIGHT = 5
CORNERS = [[0, 0], [0, WIDTH-1], [HEIGHT-1, 0], [HEIGHT-1, WIDTH-1]]
print(CORNERS)

def pix_to_coord(x,y):
    a = x//TILE_WIDTH
    b = y//TILE_HEIGHT
    return [a, b]

def create_grid(w,h):
    global table
    table = [[[-1,-1,-1] for j in range(w)] for i in range(h)]
  
    table[0][0] = [random.randint(0,255) for k in range(3)]
    table[0][w-1] = [random.randint(0,255) for k in range(3)]
    table[h-1][0] = [random.randint(0,255) for k in range(3)]
    table[h-1][w-1] = [random.randint(0,255) for k in range(3)]
    
    y1 = [(table[h-1][0][k]-table[0][0][k])/(h-1) for k in range(3)]
    y2 = [(table[h-1][w-1][k]-table[0][w-1][k])/(h-1) for k in range(3)]
    
    for i in range(h):
        table[i][0] = [table[0][0][k] + i*y1[k] for k in range(3)]
        table[i][w-1] = [table[0][w-1][k] + i*y2[k] for k in range(3)]
        x = [(table[i][w-1][k]-table[i][0][k])/(w-1) for k in range(3)]
        for j in range(w):
            table[i][j] = [round(table[i][0][k] + j*x[k]) for k in range(3)]
  
def swap_tiles(n,m):
    s = table[n[0]][n[1]]
    table[n[0]][n[1]] = table[m[0]][m[1]]
    table[m[0]][m[1]] = s

pygame.init()
screen = pygame.display.set_mode((WIDTH*TILE_WIDTH, HEIGHT*TILE_HEIGHT))

def draw_tile(i,j):
    r = pygame.Rect(j*TILE_WIDTH, i*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
    c = table[i][j]
    pygame.draw.rect(screen, c, r)
    pygame.display.update([r])

create_grid(WIDTH,HEIGHT)
correct_table = [[color[::] for color in line] for line in table]
for i in range(WIDTH*HEIGHT):
    l = [random.randint(0,HEIGHT-1), random.randint(0,WIDTH-1)]
    r = [random.randint(0,HEIGHT-1), random.randint(0,WIDTH-1)]
    if l in CORNERS or r in CORNERS:
        continue
    swap_tiles(l, r)
    
correct_tiles = 0
for i in range(HEIGHT):
    for j in range(WIDTH):
        if table[i][j] == correct_table[i][j]:
            correct_tiles += 1
        draw_tile(i, j)

print("HUEHUE INSTRUCTIONS:")
print("The 4 corners of the board are fixed,")
print("\tyour job is to rearrange all other tiles to complete a degradee")
print("\tleft-clicking a tile makes it a source tile")
print("\tright-clicking a tile swaps it with the last source you clicked")
print("\tyou can also drag&drop a tile to move it")

pygame.image.save(screen, "start.png")

left_clicked = [0, 0]
while correct_tiles != WIDTH*HEIGHT:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif ev.type == MOUSEBUTTONDOWN or ev.type == MOUSEBUTTONUP:
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                left_clicked = pix_to_coord(*ev.pos)[::-1]
            elif ev.type == MOUSEBUTTONDOWN and ev.button == 3 or ev.type == MOUSEBUTTONUP and ev.button == 1:
                right_clicked = pix_to_coord(*ev.pos)[::-1]
                if left_clicked in CORNERS or right_clicked in CORNERS:
                    continue

                # moves are about to be done
                # chech how many will decrease score
                if table[left_clicked[0]][left_clicked[1]] == correct_table[left_clicked[0]][left_clicked[1]]:
                    correct_tiles -= 1
                if table[right_clicked[0]][right_clicked[1]] == correct_table[right_clicked[0]][right_clicked[1]]:
                    correct_tiles -= 1

                swap_tiles(left_clicked, right_clicked)
                draw_tile(left_clicked[0], left_clicked[1])
                draw_tile(right_clicked[0], right_clicked[1])

                # moves have been done; count how many were correct moves
                if table[left_clicked[0]][left_clicked[1]] == correct_table[left_clicked[0]][left_clicked[1]]:
                    correct_tiles += 1
                if table[right_clicked[0]][right_clicked[1]] == correct_table[right_clicked[0]][right_clicked[1]]:
                    correct_tiles += 1

                left_clicked = right_clicked

pygame.display.set_caption("You WON!")
pygame.image.save(screen, "end.png")

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
