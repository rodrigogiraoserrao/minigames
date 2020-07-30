from PIL import Image, ImageDraw
import sys
import os
from math import pi, sin, cos

def generate_polygon(n, colours):
    theta = (2*pi)/n
    vertices = [(20*cos(theta*j), 20*sin(theta*j)) for j in range(0, n)]
    for j in range(1, n//2+1):
        vertices[j] = (vertices[n-j][0], -vertices[n-j][1])
    vertices = [(v[0]+25, v[1]+25) for v in vertices]

    im = Image.new("RGB", (50,50), (255,255,255))
    for name in colours.keys():
        c = colours[name]
        draw = ImageDraw.Draw(im)
        draw.polygon(vertices, fill=c, outline=c)
        im.save(os.path.join("polygonbin", "sides"+str(n)+name+".png"))

# colours taken from https://www.w3schools.com/tags/ref_colornames.asp
COLOURS = {
    "Black": (0,0,0),
    "Red": (255,0,0),
    "Green": (0,255,0),
    "Blue": (0,0,255),
    "Aqua": (0,255,255),
    "Brown": (165, 42, 42),
    "Chocolate": (210, 105, 30),
    "Crimson": (220, 20, 60),
    "DarkGoldenRod": (184, 134, 11),
    "DarkGreen": (0, 100, 0),
    "DarkOrange": (255, 140, 0),
    "Fuchsia": (255, 0, 255),
    "Gold": (255, 190, 0),
    "SeaGreen": (46, 139, 87),
    "Yellow": (255, 255, 0)
}

if __name__ == "__main__":
    n = -1
    while True:
        try:
            n = int(input("# of sides >> "))
            if n == 0:
                sys.exit()
        except Exception:
            continue

        generate_polygon(n, COLOURS)