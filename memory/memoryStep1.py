from pygame.locals import *
import pygame
import sys

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

width = 5
height = 4
CARD_PIXEL_WIDTH = 50
PIXEL_BORDER = 5
WIDTH = width*(CARD_PIXEL_WIDTH) + (width+1)*PIXEL_BORDER
HEIGHT = height*(CARD_PIXEL_WIDTH) + (height+1)*PIXEL_BORDER
BACKGROUND_COLOR = (20, 200, 20)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

cardback, cardbackrect = load_image("cardback.png")

# initialize the screen
screen.fill(BACKGROUND_COLOR)
for x in range(width):
    for y in range(height):
        xc = (x+1)*PIXEL_BORDER + x*CARD_PIXEL_WIDTH
        yc = (y+1)*PIXEL_BORDER + y*CARD_PIXEL_WIDTH
        screen.blit(cardback, (xc, yc))

pygame.display.update()

while True:
    for ev in pygame.event.get():
        if ev.type == QUIT:
            pygame.quit()
            sys.exit()
