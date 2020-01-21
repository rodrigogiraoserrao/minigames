#!/usr/bin/env python3

import os
import sys
import math
import random
import pygame
from pygame.locals import *

pygame.init()

def load_image(name, transparent=False):
    """Function that handles image loading
    Returns the image and its Rect"""
    path_to = os.path.join("bin", name)
    try:
        img = pygame.image.load(path_to)
    except pygame.error:
        raise SystemExit("Could not load image " + name)
    if not transparent:
        img = img.convert()
    img = img.convert_alpha()
    img_rect = img.get_rect()

    return img, img_rect


class Background_Manager(pygame.sprite.Group):
    """Manager to control all the sprites in the scenery
    Inherites from pygame.sprite.Group because of its handy methods.
    Gets a background surface and optional sprites.
    Implements:
    update() > override Group.update because the background isn't
    part of the sprites contained;
    also decide whether to create a new Person or not
    draw() > override so that it calls every draw_it()
    add() > override so that we can separately keep track of
    falling poops AND people"""
    def __init__(self, bg, *sprites):
        pygame.sprite.Group.__init__(self, sprites)
        self.background = bg

    def draw(self):
        self.background.draw_it()
        for sprite in self.sprites():
            sprite.draw_it()

    def update(self):
        self.background.update()
        for sprite in self.sprites():
            sprite.update()
            if sprite.rect.right <= 0:
                self.remove(sprite)


class Background_Scroller(pygame.sprite.Sprite):
    """Class to update the background.
    Takes a name of the image to be used and the scrolling speed
    in pixels per second."""
    def __init__(self, name, speed, screen):
        self.image, self.rect = load_image(name)
        self.scroll_speed = speed
        self.screen = screen
        
        self.offset = int(self.rect.width/2)
        self.rect = pygame.Rect(0, 0, self.offset, self.rect.height)

    def update(self):
        self.rect.move_ip(self.get_scroll())

        if self.rect.left >= self.offset:
            self.rect.left -= self.offset

    def draw_it(self):
        self.screen.blit(self.image, (0, 0), self.rect)

    def get_scroll(self):
        return (self.scroll_speed[0]//FPS, self.scroll_speed[1]//FPS)


class Pigeon(pygame.sprite.Sprite):
    """Implements the main character: the pooping pigeon"""

    hits = 0
    people_appeared = 0
    times_pooped = 0

    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("pigeon.png", transparent=True)
        self.state = "down"
        self.float_between = (13, 26)
        self.rect.left = 160
        self.rect.top = random.randint(*self.float_between)

        self.screen = screen

    def update(self):
        if self.rect.top >= self.float_between[1]:
            self.state = "up"
        elif self.rect.top <= self.float_between[0]:
            self.state = "down"

        f = random.randint(1,2)
        f = f if self.state == "down" else -f
        self.rect.move_ip((0, f))

    def draw_it(self):
        self.screen.blit(self.image, self.rect)

    def poop(self):
        bg_man = self.groups()[0]
        bg_man.add(Poop(self.rect.center, self.screen))


class Poop(pygame.sprite.Sprite):
    """Implements the poops pooped by the Pigeon"""
    def __init__(self, pooped_from, screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.image, self.rect = load_image("poop.png", transparent=True)
        self.fall = 1
        self.state = "falling"
        
        self.rect.center = pooped_from

    def update(self):
        if self.state == "falling":
            self.rect.move_ip((-1, self.fall))
            self.fall += 0.5
        elif self.state == "fell":
            self.rect.move_ip((-SCROLL_SPEED/FPS, 0))

        # stop it from testing for collisions if it has
        # already fell!
        if self.state == "fell":
            return

        # test for ground collision
        if self.rect.bottom >= GROUND_LEVEL:
            self.state = "fell"
            self.image, new_rect = load_image("ground_poop.png",
                                                transparent=True)
            new_rect.left = self.rect.left
            new_rect.top = self.rect.top
            self.rect = new_rect
        # test for person collision
        else:
            # test to see if poop collided with any Person object
            # the callback already tests the type of collision
            # to prevent poop <> poop collision
            l = pygame.sprite.spritecollide(self, bg_manager, False,
                                            Poop.is_colliding)
            if l:
                self.state = "fell"
                self.image, r = load_image("person_poop.png",
                                            transparent=True)
                r.left = self.rect.left
                r.top = self.rect.top+r.height-2
                self.rect = r
                Pigeon.hits += 1
                for person in l:
                    person.swap()

    def draw_it(self):
        self.screen.blit(self.image, self.rect)

    def is_colliding(poop, sprite):
        if not isinstance(sprite, Person):
            return False

        # get head rect. collides?
        top = sprite.rect.top
        left = sprite.rect.left+4
        width = height = 13
        head_rect = pygame.Rect(left, top, width, height)
        
        if head_rect.collidepoint(poop.rect.center):
            return True

        # get arms rect
        width, height = 21, 4
        top = sprite.rect.top + 13
        left = sprite.rect.left
        arms_rect = pygame.Rect(left, top, width, height)

        return arms_rect.collidepoint(poop.rect.center)


class Person(pygame.sprite.Sprite):
    """Implements a person object
    takes the image file as argument (different colours!)
    takes its walking speed as well"""
    def __init__(self, name, colour, speed, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(name, transparent=True)
        self.n = colour
        self.rect.left = screen.get_rect().right + 20
        self.rect.top = random.randint(70, 97)

        self.walk_speed = speed
        self.screen = screen


    def update(self):
        self.rect.move_ip((-SCROLL_SPEED/FPS, 0))

    def draw_it(self):
        self.screen.blit(self.image, self.rect)

    def swap(self):
        self.image, r = load_image("person"+str(self.n)+"p.png",
                                    transparent=True)


class Person_Factory(object):
    """Returns a random Person object"""
    def __init__(self, screen):
        self.screen = screen

    def create(self):
        """Create a random person object
        For now, disable the walking speed"""
        Pigeon.people_appeared += 1

        colour = random.randint(1, 8)
        name = "person" + str(colour) + ".png"
        # for now, Person objects don't walk
        return Person(name, colour, 0, self.screen)

screen = pygame.display.set_mode((1000, 140))
pygame.display.set_caption("Pigeon (pooping) Simulator")

if pygame.font:
    lvl = 1
    font1, font2 = pygame.font.Font(None, 18), pygame.font.Font(None, 24)
    text1 = font1.render("Please choose the difficulty level: (1 to 10)", 1, (250, 250, 250))
    text1pos = text1.get_rect(centerx = screen.get_rect().centerx)
    text1pos.top = 35
    screen.blit(text1, text1pos)
    text3 = font1.render("(ENTER to confirm)", 1, (250, 250, 250))
    text3pos = text3.get_rect(centerx = screen.get_rect().centerx)
    text3pos.top = 50
    screen.blit(text3, text3pos)

    text2 = font2.render(str(lvl), 1, (250, 250, 250))
    text2pos = text2.get_rect(centerx = screen.get_rect().centerx)
    text2pos.top = 85
    screen.blit(text2, text2pos)

    pygame.display.update([text1pos, text2pos, text3pos])

    choosing = True
    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key in [K_RIGHT, K_LEFT, K_PLUS, K_MINUS]:
                    screen.fill((0, 0, 0), text2pos)
                    pygame.display.update(text2pos)
                    if event.key in [K_PLUS, K_RIGHT] and lvl < 10:
                        lvl += 1
                    elif event.key in [K_MINUS, K_LEFT] and lvl > 1:
                        lvl -= 1
                    text2 = font2.render(str(lvl), 1, (250, 250, 250))
                    text2pos = text2.get_rect(centerx =
                                            screen.get_rect().centerx)
                    text2pos.top = 85
                    screen.blit(text2, text2pos)
                    pygame.display.update(text2pos)
                elif event.key == K_RETURN:
                    choosing = False
                elif event.key == K_q:
                    sys.exit(0)
else:
    print("Please type in the difficulty level from 1 to 10")
    lvl = ""
    lvls = "1 2 3 4 5 6 7 8 9 10".split()
    while lvl not in lvls:
        lvl = input("Level 1-10 >> ")
    lvl = int(lvl)
    
FPS = 30  # maximum number of frames per second
SCROLL_SPEED = 30*lvl # the number of pixels the BG scrolls per second
GROUND_LEVEL = 118  # the level at which the poop collides with the floor
POOP_WAIT = int(40/lvl)  # number of rest cycles between poopings
GAME_DURATION = 60000  # game duration in milisseconds (60s for now)

PersonFact = Person_Factory(screen)

bg_scroller = Background_Scroller("city.png", (SCROLL_SPEED, 0), screen)
pigeon = Pigeon(screen)

bg_manager = Background_Manager(bg_scroller)
bg_manager.add(pigeon)
bg_manager.draw()

pygame.display.update()
clock = pygame.time.Clock()

next_per_countdown = int(100/lvl)+5
poop_cooldown = POOP_WAIT
game_start = pygame.time.get_ticks()
go = True
while go:
    clock.tick(FPS)
    next_per_countdown -= 1

    if poop_cooldown:
        poop_cooldown -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == KEYDOWN:
            if event.key == K_q:
                go = False
            elif event.key == K_SPACE:
                if not poop_cooldown:
                    pigeon.poop()
                    Pigeon.times_pooped += 1
                    poop_cooldown = POOP_WAIT

    if next_per_countdown == 0:
        next_per_countdown = random.randint(int(80/lvl), int(240/lvl))
        bg_manager.add(PersonFact.create())

    bg_manager.update()
    bg_manager.draw()
    
    pygame.display.update()

    if pygame.time.get_ticks() - game_start >= GAME_DURATION:
        go = False

s = """\
You, an amazing pigeon, have flown for {GD} seconds.
For that period of time, you had the chance to ruin {pc} person's days.
You managed to hit a total of {hc}, from a total of {pooped} poops.
That means {pper}% of the poops landed and
{hper}% of the people got their days ruined!.""".format(
    GD = GAME_DURATION/1000,
    pc = Pigeon.people_appeared,
    hc = Pigeon.hits,
    pooped = Pigeon.times_pooped,
    pper = int(Pigeon.hits/Pigeon.times_pooped*100),
    hper = int(Pigeon.hits/Pigeon.people_appeared*100))
if pygame.font:
    screen.fill((0, 0, 0))

    font = pygame.font.Font(None, 18)

    lines = s.split("\n")
    top_pos = 20
    for line in lines:
        text = font.render(line, 1, (250, 250, 250))
        textpos = text.get_rect(centerx = screen.get_width()/2)
        textpos.top = top_pos
        screen.blit(text, textpos)
        top_pos += 20
    pygame.display.update()

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                sys.exit(0)
            elif ev.type == KEYDOWN and ev.key == K_q:
                sys.exit(0)

else:
    print(s)
