# -*- coding: utf-8 -*-
import sys
import pygame
from pygame.locals import *
from creeper import FollowerFactory
from math import sqrt
from random import randint, random

# screen dimensions
WIDTH = 800
HEIGHT = 500
# some colours
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
# game constants
FPS = 60
PLAYERRADIUS = 10
CREEPERRADIUS = 10
# dictionary with movement directions
ORIENT = {"N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1),
            "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1)}

class MovingObject(object):
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    def move(self, speed):
        dx = self.direction[0]
        dy = self.direction[1]
        factor = sqrt(dx**2 + dy**2)
        if factor:
            dx *= speed/factor
            dy *= speed/factor
        self.pos[0] += dx
        self.pos[1] += dy

class BasePlayer(object):
    def __init__(self, pos):
        self.up = self.down = self.left = self.right = False
        self.orient = "E"
        self.pos = pos

    def move(self, speed):
        dx = self.right - self.left
        dy = self.down - self.up
        factor = sqrt(dx**2 + dy**2)
        if factor:
            dx *= speed/factor
            dy *= speed/factor
        self.pos[0] += dx
        self.pos[1] += dy

    def bind(self, key_dict):
        """The function 'bind' tells the BasePlayer class what keys
        will be controlling the movement. The dictionary 'key_dict' must
        have four 'pygame key':'string' pairs for N,S,E,W, corresponding
        to moving up, down, right and left respectively"""
        self.mov_keys = key_dict

    def key_pressed(self, key):
        point_to_var = {"N":"up", "S":"down", "W":"left", "E":"right"}
        opposite = {"N":"S", "E":"W", "S":"N", "W":"E"}
        # a direction can be just one of the four points, or a string
        # of length two, composed by a prefix point and a suffix point
        prefixes = "NS"
        suffixes = "EW"
        going_to = self.mov_keys[key]
        setattr(self, point_to_var[going_to], True)
        setattr(self, point_to_var[opposite[going_to]], False)
        if self.up+self.down+self.left+self.right == 1:
            self.orient = going_to
        else:
            pre = set(prefixes).intersection(set(self.orient))
            if going_to in prefixes:
                pre = going_to
            elif not pre:
                pre = ""
            else:
                pre = pre.pop()
            suf = set(suffixes).intersection(set(self.orient))
            if going_to in suffixes:
                suf = going_to
            elif not suf:
                suf = ""
            else:
                suf = suf.pop()
            self.orient = pre+suf

    def key_up(self, key):
        point_to_var = {"N":"up", "S":"down", "W":"left", "E":"right"}
        prefixes = "NS"
        suffixes = "EW"
        going_to = self.mov_keys[key]
        setattr(self, point_to_var[going_to], False)
        if len(self.orient) == 2:
            if going_to in prefixes:
                self.orient = self.orient[1]
            elif going_to in suffixes:
                self.orient = self.orient[0]

class Player(BasePlayer):
    def __init__(self, surf, pos):
        self.surf = surf
        BasePlayer.__init__(self, pos)
        self.bind({K_w:"N", K_s:"S", K_a:"W", K_d:"E"})
        self.speed = 5
        self.radius = PLAYERRADIUS
        self.shots = []
        self.maxlife = 100
        self.life = self.maxlife

    def update_and_draw(self):
        i = 0
        while i < len(self.shots):
            shot = self.shots[i]
            shot.move(2*self.speed)
            if shot.pos[0] < 0 or shot.pos[0] > WIDTH or \
                shot.pos[1] < 0 or shot.pos[1] > HEIGHT:
                self.shots.pop(i)
            else:
                rounded = [round(shot.pos[0]), round(shot.pos[1])]
                pygame.draw.circle(self.surf, WHITE, rounded, self.radius//3)
                i += 1
        self.move(self.speed)
        self.pos[0] = max(0, min(WIDTH, self.pos[0]))
        self.pos[1] = max(0, min(HEIGHT, self.pos[1]))
        rounded = [round(self.pos[0]), round(self.pos[1])]
        pygame.draw.circle(self.surf, WHITE, rounded, self.radius)

    def shoot(self, ev, aim_at):
        # use the BasePlayer because it already implements the .move to update
        direction = [aim_at[0]-self.pos[0], aim_at[1]-self.pos[1]]
        s = MovingObject(self.pos[::], direction)
        self.shots.append(s)

class DrawableCreeper(object):
    def __init__(self, surface, colour, radius):
        self.c = colour
        self.surface = surface
        self.radius = radius

    def draw(self):
        rounded = [round(self.pos[i]) for i in range(2)]
        pygame.draw.circle(self.surface, self.c, rounded, self.radius)

GC = FollowerFactory(10, 1)
RC = FollowerFactory(20, 2)
BC = FollowerFactory(0, 3)

class GreenCreeper(DrawableCreeper, GC):
    def __init__(self, surface, pos, follow):
        GC.__init__(self, pos, follow)
        DrawableCreeper.__init__(self, surface, GREEN, CREEPERRADIUS)

    def update_and_draw(self):
        self.move()
        self.draw()

class RedCreeper(DrawableCreeper, RC):
    def __init__(self, surface, pos, follow):
        RC.__init__(self, pos, follow)
        DrawableCreeper.__init__(self, surface, RED, CREEPERRADIUS+2)

    def update_and_draw(self):
        self.move()
        self.draw()

class BlueCreeper(DrawableCreeper, BC):
    def __init__(self, surface, pos, follow):
        RC.__init__(self, pos, follow)
        DrawableCreeper.__init__(self, surface, BLUE, CREEPERRADIUS)

    def update_and_draw(self):
        self.move()
        self.draw()

def dist(p, q):
    return sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)

def new_creeper():
    if random() < 0.5:
        # make it appear from up/down
        pos = [randint(0, WIDTH), round(random())*HEIGHT]
    else:
        pos = [round(random())*WIDTH, randint(0, HEIGHT)]
    r = random()
    if r <= 0.45:
        creepers.append(RedCreeper(screen, pos, p))
    elif r <= 0.9:
        creepers.append(GreenCreeper(screen, pos, p))
    else:
        creepers.append(BlueCreeper(screen, pos, p))

def draw_lifebar(surf, p):
    lifebar_width = 200
    lifebar_height = 20
    margin = 10
    width = round(p*lifebar_width)
    r = pygame.Rect(surf.get_width()-lifebar_width-margin, surf.get_height()-lifebar_height-margin, width, lifebar_height)
    pygame.draw.rect(surf, RED, r)
    r.width = lifebar_width
    pygame.draw.rect(surf, RED, r, 2)

def draw_score(surf, score):
    textsurf = font.render("{:06}".format(score), False, WHITE)
    surf.blit(textsurf, (surf.get_width()-textsurf.get_width()-10, 10))

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

font = pygame.font.SysFont("Comic Sans", 30)

p = Player(screen, [WIDTH//2, HEIGHT//2])
creepers = []

frame = 0
creeper_counter = 1
clock = pygame.time.Clock()
score = 0
multiplier = 1
while p.life > 0:
    frame += 1
    clock.tick(FPS)

    for ev in pygame.event.get():
        if ev.type == QUIT:
            pygame.quit()
            sys.exit()
        elif ev.type == KEYDOWN:
            if ev.key in [K_w, K_s, K_a, K_d]:
                p.key_pressed(ev.key)
            elif ev.key == K_SPACE:
                p.shoot(ev, pygame.mouse.get_pos())
        elif ev.type == KEYUP:
            if ev.key in [K_w, K_s, K_a, K_d]:
                p.key_up(ev.key)
        elif ev.type == MOUSEBUTTONDOWN:
            if ev.button == 1:
                p.shoot(ev, ev.pos)

    creeper_counter += 1
    creeper_counter %= FPS
    if creeper_counter == 0:
        new_creeper()

    screen.fill(BLACK)

    j = 0
    while j < len(creepers):
        creeper = creepers[j]
        if dist(creeper.pos, p.pos) <= 0.9+(PLAYERRADIUS+CREEPERRADIUS):
            creepers.pop(j)
            p.life -= 5
            multiplier = 1
        else:
            i = 0
            while i < len(p.shots):
                shot = p.shots[i]
                if dist(shot.pos, creeper.pos) <= 1.01*creepers[j].radius:
                    creepers[j].radius -= 1
                    p.shots.pop(i)
                    if creepers[j].radius < CREEPERRADIUS:
                        creepers.pop(j)
                        score += multiplier
                        multiplier += 1
                        if p.life < p.maxlife:
                            p.life += 1
                        break
                i += 1
            creeper.update_and_draw()
            j += 1

    draw_score(screen, score)
    draw_lifebar(screen, p.life/p.maxlife)
    p.update_and_draw()
    pygame.display.update()