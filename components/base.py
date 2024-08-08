import pygame
import os

#load images, and scale to double the size
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    
    def __init__(self, y):
        self.y = y 
        self.x1 = 0 #first base on screen
        self.x2 = self.WIDTH #second base emmediately to the right of the first one, off screen
    
    def move(self):
        #shift both bases to the left, when the first one gets off screen, 
        #it will relocate to emmediately to the right of the second one, and both will continue shifting to the left
        #this cycle is better explained with a diagram
        self.x1 -= self.VEL 
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0: #if the first block is off screen
            self.x1 = self.x2 + self.WIDTH #got to right of second block
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, window):
        window.blit(BASE_IMG, (self.x1, self.y))
        window.blit(BASE_IMG, (self.x2, self.y))