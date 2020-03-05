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

width = 2
height = 3
CARD_PIXEL_WIDTH = 50
PIXEL_BORDER = 5
TIMEBARWIDTH = 25
WIDTH = width*(CARD_PIXEL_WIDTH) + (width+2)*PIXEL_BORDER + TIMEBARWIDTH
HEIGHT = height*(CARD_PIXEL_WIDTH) + (height+1)*PIXEL_BORDER
BACKGROUND_COLOR = (20, 200, 20)
IMAGE_BIN = "polygonbin"
BONUSTIME = 3000
PENALTYTIME = 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def board_to_pixels(coords):
    # receives a pair (x, y) pertaining a card position on the table
    # transforms it into a pair (xc, yc) of pixel coordinates of the
    #   top left corner of the card
    xc = (coords[0]+1)*PIXEL_BORDER + coords[0]*CARD_PIXEL_WIDTH
    yc = (coords[1]+1)*PIXEL_BORDER + coords[1]*CARD_PIXEL_WIDTH
    return xc, yc

def draw_timebar(percentage):
    # draws a black timebar to let the user know how much time is left
    # find the total height of the bar
    height_used = height*(CARD_PIXEL_WIDTH) + (height-1)*PIXEL_BORDER
    # cover the existing timebar with the background color
    pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(width*(CARD_PIXEL_WIDTH) + (width+1)*PIXEL_BORDER,
                                                    PIXEL_BORDER,
                                                    TIMEBARWIDTH, height_used))
    # draw the timebar frame
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(width*(CARD_PIXEL_WIDTH) + (width+1)*PIXEL_BORDER,
                                                    PIXEL_BORDER,
                                                    TIMEBARWIDTH, height_used), 3)
    # draw the time that is still left
    pygame.draw.rect(screen, (0,0,0), pygame.Rect(width*(CARD_PIXEL_WIDTH) + (width+1)*PIXEL_BORDER,
                                                    PIXEL_BORDER+(1-percentage)*height_used,
                                                    TIMEBARWIDTH, percentage*height_used))
    # update the timebar area
    pygame.display.update(pygame.Rect(width*(CARD_PIXEL_WIDTH) + (width+1)*PIXEL_BORDER,
                                                    PIXEL_BORDER,
                                                    TIMEBARWIDTH, height_used))

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

# auxiliary variables to control the state of the game
is_flipped = False
flipped_card = []
flipped_coords = []
to_find = len(cards)/2
found_cards = []

wait = False
wait_until = None
end = pygame.time.get_ticks() + BONUSTIME*width*height
score = 0
while to_find > 0 and pygame.time.get_ticks() < end + score:
    # find the percentage of time left and update the timebar
    perc = min(1, (end+score-pygame.time.get_ticks())/(BONUSTIME*width*height))
    draw_timebar(perc)
    
    if wait and pygame.time.get_ticks() > wait_until:
        # we have waited already, now we take care of the cards
        wait = False
        pygame.event.set_allowed(MOUSEBUTTONDOWN)
        # if we got it right
        x1, y1 = flipped_coords[0]
        x2, y2 = flipped_coords[1]
        if card_list[x1][y1] == card_list[x2][y2]:
            to_find -= 1
            # this is the old rect pointing to the card
            # that was most recently turned up
            pygame.draw.rect(screen, BACKGROUND_COLOR, rect)
            pygame.display.update(rect)
            # erase the oldest facing up card from the game table
            xc, yc = board_to_pixels((x1, y1))
            rect = pygame.Rect(xc, yc, CARD_PIXEL_WIDTH, CARD_PIXEL_WIDTH)
            pygame.draw.rect(screen, BACKGROUND_COLOR, rect)
            pygame.display.update(rect)
            # flag these two cards as found
            found_cards.append((x1, y1))
            found_cards.append((x2, y2))
            score += BONUSTIME
        # if we got it wrong
        else:
            # cover both cards again
            screen.blit(cardback, (xc, yc))
            pygame.display.update(rect)
            xc, yc = board_to_pixels((x1, y1))
            rect = pygame.Rect(xc, yc, CARD_PIXEL_WIDTH, CARD_PIXEL_WIDTH)
            screen.blit(cardback, (xc, yc))
            pygame.display.update(rect)
            score -= PENALTYTIME
        is_flipped = False

    for ev in pygame.event.get():
        if ev.type == QUIT:
            pygame.quit()
            sys.exit()

        elif ev.type == MOUSEBUTTONDOWN:
            if wait:
                continue
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

            if (x,y) in found_cards:
                continue
            elif not is_flipped:
                screen.blit(images[card_list[x][y]][0], (xc, yc))
                pygame.display.update(rect)
                is_flipped = True
                flipped_card = [card_list[x][y]]
                flipped_coords = [(x, y)]
            # there is a card face up
            else:
                # I just clicked it
                if flipped_coords[0] == (x, y):
                    continue
                else:
                    # set a waiting interval where no events are allowed
                    wait = True
                    # turn this new card face up; wait
                    screen.blit(images[card_list[x][y]][0], (xc, yc))
                    pygame.display.update(rect)
                    # disable new clicks
                    pygame.event.set_blocked(MOUSEBUTTONDOWN)
                    if flipped_card[0] != card_list[x][y]:
                        flipped_card.append(card_list[x][y])
                        wait_until = pygame.time.get_ticks() + 800
                    else:
                        wait_until = pygame.time.get_ticks() + 300
                    flipped_coords.append((x,y))
