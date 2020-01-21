import sys
import random
import pygame
from pygame.locals import *

WIDTH = 400
HEIGHT = 300
GRAY = (230,230,230)
BLACK = (0,0,0)

class ShrinkingCircle(object):
    def __init__(self, surface, pos, radius, lifespan):
        self.surface = surface
        self.pos = pos
        self.radius = radius
        self._radius = radius
        self.lifespan = lifespan
        self.lifetime = pygame.time.get_ticks() + lifespan
        self.alive = True

    def hit(self, p):
        return (p[0]-self.pos[0])**2 + (p[1]-self.pos[1])**2 <= self._radius**2

    def draw(self):
        ticks = pygame.time.get_ticks()
        if ticks > self.lifetime:
            self.alive = False
        if self.alive:
            r = round(self.radius*(self.lifetime-ticks)/self.lifespan)
            self._radius = r
            if r >= 1:
                pygame.draw.circle(self.surface, BLACK, self.pos, r, 1)

    def is_alive(self):
        return self.alive

pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
screen.fill(GRAY)

clock = pygame.time.Clock()

circles = []

while True:
    clock.tick(90)

    for ev in pygame.event.get():
        if ev.type == QUIT or (ev.type == KEYDOWN and (ev.key == K_q or ev.key == K_ESCAPE)):
            pygame.quit()
            sys.exit()
        elif ev.type == MOUSEBUTTONDOWN:
            for i, circle in enumerate(circles):
                if circle.hit(ev.pos):
                    circle.alive = False
                    break

    i = 0
    while i < len(circles):
        if not circles[i].is_alive():
            circles.pop(i)
        else:
            i += 1
    while len(circles) < 3:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        r = random.randint(20, 30)
        life = random.randint(1500, 4500)
        circles.append(
            ShrinkingCircle(screen, [x,y], r, life)
        )
    screen.fill(GRAY)
    for circle in circles:
        circle.draw()

    pygame.display.update()