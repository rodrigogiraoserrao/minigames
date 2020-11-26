import itertools
import os
import random
import sys
import numpy as np
import pygame
from pygame.locals import *

try:
    from HueHueConfig import *
except Exception:
    TILE_WIDTH = 40
    TILE_HEIGHT = 60
    WIDTH = 5
    HEIGHT = 5

CORNERS = [[0, 0], [WIDTH-1, 0], [0, HEIGHT-1], [WIDTH-1, HEIGHT-1]]
BLACK = np.zeros(3, dtype=np.uint8)
FRAMES = "huehue_frames"

def at(arr, pair):
    """Utility method to use pairs to index a numpy array."""
    return arr[pair[0], pair[1]]

def pix_to_coord(px, py):
    """Transform pixel coordinates into integer tile coordinates."""
    return [px // TILE_WIDTH, py //TILE_HEIGHT]

def rand_colour():
    """Generates a random RGB colour, returns a numpy vector.
    Prevents generation of colours that are too light or too dark.
    """

    while not 50 < np.sum(c := np.random.randint(0, 256, 3)) < 3*240:
        pass
    return c

def create_grid(w, h):
    """Creates an initial grid with random colours, returns a 3D numpy tensor."""

    # Define the left and right edges and interpolate them.
    left  = np.linspace(rand_colour(), rand_colour(), num=h)
    right = np.linspace(rand_colour(), rand_colour(), num=h)
    return np.round(np.linspace(left, right, num=w))
  
def swap_tiles(colours, t1, t2):
    """Swap two tiles in the given array (side-effect)."""
    colours[t1[0], t1[1]], colours[t2[0], t2[1]] = (
        np.copy(colours[t2[0], t2[1]]), np.copy(colours[t1[0], t1[1]])
    )

def draw_tile(screen, colours, x, y):
    """Draw the given tile to the surface given."""

    if not (0 <= x < WIDTH) or not (0 <= y < HEIGHT):
        return None

    r = pygame.Rect(x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
    c = colours[x, y]
    pygame.draw.rect(screen, c, r)
    return r

def black_out_tile(screen, colours, x, y):
    """Draw the given tile with a black colour."""

    c, colours[x, y] = np.copy(colours[x, y]), BLACK
    r = draw_tile(screen, colours, x, y)
    colours[x, y] = c
    return r

def draw_surroundings(screen, colours, x, y):
    """Draw the tiles in a 3x3 area around the given tile."""

    r = pygame.Rect(0, 0, TILE_WIDTH, TILE_HEIGHT)
    return [
        draw_tile(screen, colours, x+dx, y+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
    ]

def draw_floating_tile_animation(screen, colours, px, py, original):
    """Draw the floating tile animation."""

    # Start with drawing the surroundings of the floating tile.
    x, y = coord = pix_to_coord(px, py)
    to_update = draw_surroundings(screen, colours, x, y)
    # Check if we need to black out the original tile to show it is empty.
    if np.sum(np.abs(np.array(original) - np.array(coord))) <= 3:
        u = black_out_tile(screen, colours, *original)
        to_update.append(u)

    # Draw frame around tile being hovered.
    r = pygame.Rect(x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
    pygame.draw.rect(screen, BLACK, r.inflate(-2, -2), 3)
    to_update.append(r)
    # Draw floating tile and frame.
    r.center = (int(px), int(py))
    pygame.draw.rect(screen, at(colours, original), r)
    pygame.draw.rect(screen, BLACK, r, 2)
    to_update.append(r.inflate(2, 2))

    return to_update


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH*TILE_WIDTH, HEIGHT*TILE_HEIGHT))

    colours = create_grid(WIDTH, HEIGHT)
    correct_colours = np.copy(colours)

    last_axis_all = lambda arr: np.apply_along_axis(np.all, -1, arr)

    # Shuffle colours
    colours = np.reshape(colours, (WIDTH*HEIGHT, 3))
    np.random.shuffle(colours)
    colours = np.reshape(colours, (WIDTH, HEIGHT, 3))
    # Fix corners back into original position.
    for x, y in itertools.product([0, WIDTH-1], [0, HEIGHT-1]):
        colour = correct_colours[x, y]
        is_at = np.where(last_axis_all(colour == colours))
        print(is_at)
        colours[is_at], colours[x, y] = colours[x, y], colours[is_at]
    # Count colours in the correct positions
    correct_tiles = np.sum(last_axis_all(colours == correct_colours))
    print(correct_tiles)
    assert correct_tiles >= 4, "At least the 4 corners should be correct."

    to_update = []
    for x in range(WIDTH):
        for y in range(HEIGHT):
            to_update.append(
                draw_tile(screen, colours, x, y)
            )

    print("HUEHUE INSTRUCTIONS:")
    print("The 4 corners of the board are fixed,")
    print("\tyour job is to rearrange all other tiles to complete a degradee")
    print("\tleft-clicking a tile makes it a source tile")
    print("\tright-clicking a tile swaps it with the last source you clicked")
    print("\tyou can also drag&drop a tile to move it")

    left_clicked = [0, 0]
    clock = pygame.time.Clock()
    dump_frames = False
    frame = 0
    ticks = 0

    while correct_tiles != WIDTH*HEIGHT:
        clock.tick(90)

        ticks += 1
        ticks %= 5
        if not ticks and dump_frames:
            frame += 1
            pygame.image.save(screen, f"{FRAMES}/frame{frame:04}.png")

        pygame.display.update(to_update)
        to_update = []

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == KEYDOWN and ev.key == K_r:
                dump_frames = not dump_frames
                if not os.path.exists(FRAMES):
                    os.makedirs(FRAMES)
            # Check if the user is dragging a tile.
            elif ev.type == MOUSEMOTION:
                if ev.buttons[0] == 1:
                    to_update = draw_floating_tile_animation(
                        screen, colours, *ev.pos, left_clicked
                    )
            # Check if the user (un)clicked a tile.
            elif ev.type == MOUSEBUTTONDOWN or ev.type == MOUSEBUTTONUP:
                if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                    left_clicked = pix_to_coord(*ev.pos)
                elif ev.type == MOUSEBUTTONDOWN and ev.button == 3 or ev.type == MOUSEBUTTONUP and ev.button == 1:
                    right_clicked = pix_to_coord(*ev.pos)

                    if left_clicked in CORNERS or right_clicked in CORNERS:
                        to_update = draw_surroundings(screen, colours, *right_clicked)
                        to_update += [draw_tile(screen, colours, *left_clicked)]
                        continue

                    # Adjust score
                    correct_tiles += (
                        bool(np.all(at(colours,  left_clicked) == at(correct_colours, right_clicked))) +
                        bool(np.all(at(colours, right_clicked) == at(correct_colours,  left_clicked))) -
                        bool(np.all(at(colours,  left_clicked) == at(correct_colours,  left_clicked))) -
                        bool(np.all(at(colours, right_clicked) == at(correct_colours, right_clicked)))
                    )

                    swap_tiles(colours, left_clicked, right_clicked)
                    to_update = draw_surroundings(screen, colours, *right_clicked)
                    to_update += [draw_tile(screen, colours, *left_clicked)]

                    left_clicked = right_clicked

    pygame.display.set_caption("You WON!")
    pygame.display.flip()

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
