from pygame.locals import *
import pygame
import sys
import random as rnd
from math import sqrt

FPS = 30

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
WIDTH = screen.get_width()
HEIGHT = screen.get_height()

class BattleField(object):
    def __init__(self, surf):
        self.surf = surf
        self.w = self.surf.get_width()
        self.h = self.surf.get_height()

        self.p1 = Cell(self.surf, (WIDTH//3, HEIGHT//2), (255,0,0))
        self.p2 = Cell(self.surf, (2*WIDTH//3, HEIGHT//2), (0,0,255))

        self.foods = []

    def generate_food(self):
        c = get_random_colour()
        x = rnd.randint(0, WIDTH)
        y = rnd.randint(0, HEIGHT)
        self.foods.append((x,y,c))

    def movep1(self, ev):
        btn_down = {K_w: (0,-1),
                    K_s: (0, 1),
                    K_a: (-1,0),
                    K_d: ( 1,0)}
        if ev.type == KEYDOWN:
            dx, dy = btn_down[ev.key]
            if dx:
                self.p1.vx = dx*self.p1.speed
            if dy:
                self.p1.vy = dy*self.p1.speed
        elif ev.type == KEYUP:
            if ev.key in [K_w, K_s]:
                self.p1.vy = 0
            elif ev.key in [K_a, K_d]:
                self.p1.vx = 0

    def movep2(self, ev):
        btn_down = {K_i: (0,-1),
                    K_k: (0, 1),
                    K_j: (-1,0),
                    K_l: ( 1,0)}
        if ev.type == KEYDOWN:
            dx, dy = btn_down[ev.key]
            if dx:
                self.p2.vx = dx*self.p2.speed
            if dy:
                self.p2.vy = dy*self.p2.speed
        elif ev.type == KEYUP:
            if ev.key in [K_i, K_k]:
                self.p2.vy = 0
            elif ev.key in [K_j, K_l]:
                self.p2.vx = 0

    def update_and_draw(self):
        if len(self.foods) < 100:
            self.generate_food()

        self.surf.fill((0,0,0))
        i = 0
        while i < len(self.foods):
            x,y,c = self.foods[i]
            if dist((x,y), (self.p1.x,self.p1.y)) <= self.p1.radius:
                self.p1.eat()
                self.foods.pop(i)
            elif dist((x,y), (self.p2.x,self.p2.y)) <= self.p2.radius:
                self.p2.eat()
                self.foods.pop(i)
            else:
                pygame.draw.circle(self.surf, c, (x,y), 3)
                i += 1
        d = dist((self.p1.x,self.p1.y), (self.p2.x,self.p2.y))
        if self.p1.radius > 1.2*self.p2.radius:
            # p1 can eat p2, is it close enough?
            if d < 1.2*(self.p1.radius - self.p2.radius):
                self.p1.radius += self.p2.radius
                self.p2.radius = 0
        elif self.p2.radius > 1.2*self.p1.radius:
            if d < 1.2*(self.p2.radius - self.p1.radius):
                self.p2.radius += self.p1.radius
                self.p1.radius = 0
        if self.p1.radius > self.p2.radius:
            self.p1.update_and_draw()
            self.p2.update_and_draw()
        else:
            self.p2.update_and_draw()
            self.p1.update_and_draw()

class Cell(object):
    def __init__(self, surf, pos, c):
        self.surf = surf
        self.x, self.y = pos
        self.c = c
        
        self.vx = 0
        self.vy = 0

        self.maxSpeed = 7
        self.speed = self.maxSpeed
        self.minSpeed = 1
        self.radius = 7

    def eat(self):
        self.radius += 1
        if self.speed > self.minSpeed:
            self.speed -= 0.04

    def update_and_draw(self):
        if self.radius == 0:
            return
        sp = dist((0,0), (self.vx,self.vy))
        if sp != 0:
            excess = sp/self.speed
            self.vx /= excess
            self.vy /= excess
            self.x += self.vx
            self.y += self.vy

        pygame.draw.circle(self.surf, self.c, (round(self.x),round(self.y)), self.radius)

def get_random_colour():
    return [rnd.randint(0, 255) for i in range(3)]

def sgn(n):
    if n == 0:
        return 0
    elif n < 0:
        return -1
    else:
        return 1

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    
BF = BattleField(screen)
clock = pygame.time.Clock()
while True:
    clock.tick(FPS)
    for ev in pygame.event.get():
        if ev.type == QUIT:
            pygame.quit()
            sys.exit()
        elif ev.type == KEYDOWN:
            if ev.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif ev.key in [K_w, K_s, K_a, K_d]:
                BF.movep1(ev)
            elif ev.key in [K_j, K_k, K_l, K_i]:
                BF.movep2(ev)
        elif ev.type == KEYUP:
            if ev.key in [K_w, K_s, K_a, K_d]:
                BF.movep1(ev)
            elif ev.key in [K_j, K_k, K_l, K_i]:
                BF.movep2(ev)

    if len(BF.foods) < 100:
        BF.generate_food()
    BF.update_and_draw()
    pygame.display.update()