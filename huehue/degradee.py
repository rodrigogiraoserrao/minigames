import pygame
from random import randint as ri
import sys

pygame.init()

screen = pygame.display.set_mode((300, 300))

lu = (ri(0,255), ri(0,255), ri(0,255))
ru = (ri(0,255), ri(0,255), ri(0,255))
ld = (ri(0,255), ri(0,255), ri(0,255))
rd = (ri(0,255), ri(0,255), ri(0,255))

ldiffsv = [(ld[i]-lu[i])/30 for i in range(3)]
rdiffsv = [(rd[i]-ru[i])/30 for i in range(3)]

for line in range(30):
    lc = [lu[j] + line*ldiffsv[j] for j in range(3)]
    rc = [ru[j] + line*rdiffsv[j] for j in range(3)]
    diffs = [(rc[j]-lc[j])/30 for j in range(3)]
    for column in range(30):
        r = pygame.Rect(10*column, 10*line, 10, 10)
        c = [round(lc[j] + column*diffs[j]) for j in range(3)]
        pygame.draw.rect(screen, c, r)

pygame.display.update()

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()