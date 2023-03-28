import pygame
from pygame.locals import *
import sys
import random

WIDTH, HEIGHT = 1500, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
FPS_CLOCK = pygame.time.Clock()
FPS = 60
BG = (50, 50, 50)
BLACK = (0, 0, 0)

sprite_sheet_image = pygame.image.load('Testing.png').convert_alpha()


def get_animation_list(sheet, width, height, scale, numFrames):
    frames = []
    frame = 0
    while frame < numFrames:
        image = pygame.Surface((width, height))
        image.blit(sheet, (0, 0), ((frame * width), 0, (width * (frame + 1)), height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(BLACK)
        frames.append(image)
        numFrames += 1

    return frames


animation = get_animation_list(sprite_sheet_image, 48, 48, 3, 8)

print(animation)
print(3)




