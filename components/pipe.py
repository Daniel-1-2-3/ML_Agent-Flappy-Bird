import pygame
import os
import random

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))

class Pipe:
    GAP = 170 #gap between top and bottom pipe
    VEL = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0 #y coordiante of the TOP of the gap that the bird passes through 
        self.passed = False #has this pipe been passed yet?
        
        self.top = 0 #variables for where the top and bottom of the pipe (y values) will be drawn, their top-left corner
        self.bottom = 0
        #each 'obstacle' in flappy bird as a top pipe and a bottom pipe, with a gap in the middle. Top pipe is the pipe png flipped verticaly
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #flip_y is True, flip_x is False   
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.set_height()
    
    def set_height(self): #function will randomly define 
        self.height = random.randrange(50, 450) #randomly generate y coordinates for self.height, between 50-450
        self.top = self.height - self.PIPE_TOP.get_height() 
        self.bottom = self.height + self.GAP
    
    def move(self):
        self.x -= self.VEL #every frame, move the pipe to the left a little bit
    
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y))#distance between the bird and the top pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))#distance between the bird and the bottom pipe
        
        #check if the bird collides with the top pipe, by checking if their masks overlap
        ##this function utlizes the location of the pixels in the bird's mask, the location of the pixels in the pipe's mask, and the distance between those objects
        collision_point_top_pipe = bird_mask.overlap(top_pipe_mask, top_offset)#returns none if they DO NOT overlap
        collision_point_bottom_pipe = bird_mask.overlap(bottom_pipe_mask, bottom_offset)
        
        if collision_point_top_pipe or collision_point_bottom_pipe: #if either of them is not none, meaning their IS a collision
            return True #has collided with something
        else:
            return False
        
    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))