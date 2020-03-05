from pygame.locals import *
import pygame
import random
import os
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
IMAGE_BIN = "polygonbin"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def board_to_pixels(coords):
    # receives a pair (x, y) pertaining a card position on the table
    # transforms it into a pair (xc, yc) of pixel coordinates of the
    #   top left corner of the card
    xc = (coords[0]+1)*PIXEL_BORDER + coords[0]*CARD_PIXEL_WIDTH
    yc = (coords[1]+1)*PIXEL_BORDER + coords[1]*CARD_PIXEL_WIDTH
    return xc, yc

# does the board have legal dimensions?
if width*height % 2:
    print("Either 'width' or 'height' must be an even number")
    sys.exit()
# choose the cards to be used
cards = random.sample(os.listdir(IMAGE_BIN), (width*height)//2)
images = dict()
for card in cards:
    path = os.path.join(IMAGE_BIN, card)
    images[card] = load_image(path)
cards = cards*2
random.shuffle(cards)
# card_list is a 2D array with the same structure as the game table
card_list = [cards[height*i:height*(i+1)] for i in range(width)]

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

        elif ev.type == MOUSEBUTTONDOWN:
            # find the card in which we clicked; ignore clicks in the gaps between cards
            x, pad = divmod(ev.pos[0], PIXEL_BORDER+CARD_PIXEL_WIDTH)
            if x >= width or pad < PIXEL_BORDER:
                continue
            y, pad = divmod(ev.pos[1], PIXEL_BORDER+CARD_PIXEL_WIDTH)
            if y >= height or pad < PIXEL_BORDER:
                continue

            # find the top left corner of the clicked card
            xc, yc = board_to_pixels((x, y))
            rect = pygame.Rect(xc, yc, CARD_PIXEL_WIDTH, CARD_PIXEL_WIDTH)

            screen.blit(images[card_list[x][y]][0], (xc, yc))
            pygame.display.update(rect)
