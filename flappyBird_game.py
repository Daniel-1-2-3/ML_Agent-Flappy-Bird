import time
import pygame
import neat
import os
import random

WIN_WIDTH = 600
WIN_HEIGHT = 800

#load images, and scale to double the size
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird3.png")))] 
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #rotation used later for tilting the bird, during up/down movement 
    ROT_VEL = 20 #rotation velocity, speed at which the bird rotates (number of degrees rotated per frame)
    ANIMATION_TIME = 5

