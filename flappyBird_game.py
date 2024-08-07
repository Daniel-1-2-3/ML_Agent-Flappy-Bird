import time
import pygame
import neat
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 750

#load images, and scale to double the size
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))] 
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

class Bird:
    BIRD_IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #rotation used later for tilting the bird, during up/down movement 
    ROT_VEL = 10 #rotation velocity, speed at which the bird rotates (number of degrees rotated per frame)
    ANIMATION_TIME = 5

    def __init__ (self, x, y): 
        #initialize the starting position of the bird, and starting tilt
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0 #tick_count keeps track of how many frames went by since the bird last jumped
        self.vel = -10.5
        self.height = self.y #height will be used during each jump, to record the height at which the bird starting the jump from
        self.img_count = 0 #the flapping animation cycle goes through 3 different images of the bird, with wings at different angles. 
        #each image should only be on the screen for 5 frames (ANIMATION_TIME = 5). img_count keeps track of hong many frames each image has already been on the screen for
        self.img = self.BIRD_IMGS[0] #starting with the default position of the bird (no flapping wings)
    
    def jump(self):
        self.tick_count = 0 #reset the value
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        #calculates how many pixels the bird should move up/down in this frame, due to gravity and flapping
        #using the physics equation (v)(t) + 1/2(a)(t^2), where v is the initial accelaration, t is time, and a is acceleration
        #tick_count is equivelant to time in the video game, as one frame passing represents one unit of time
        #self.vel * tick_count calculates the initial displacement due to flapping. (1.5*self.tick_count**2) simulates the bird falling due to "gravity"
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count**2 
        
        if displacement >= 16:
            #if we are moving more than 16 pixels/units up/down, just set the amount of movement to 16 pixels. Prevents too much acceleration to the bird
            displacement = 16
    
        self.y = self.y + displacement
        if self.y < 0: #prevent bird from flying too high and out of frame
            self.y = 0
        
        #tilt the bird upwards if it is currently jumping, or its position is anywhere above where it last jumped from
        if displacement < 0 or self.y < self.height:
            if self.tilt < self.MAX_ROTATION: #this is for cautionary purposes, not nessecarily needed, makes sure bird cannot tilt more than max rotation (25 deg)
                self.tilt = self.MAX_ROTATION
        #tilt the bird downwards otherwise, this is process of making the bird tilt more and more downwards as it falls, until it reaches 90 degs (pointing straight down)
        else:
            if self.tilt >= -90:
                self.tilt -= self.ROT_VEL
                
    def draw(self, window): #draw the bird onto the screen, animate it
        #this following code will draw the flapping animation of the bird, it is a cycle
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME: #first 5 frames of cycle, bird is neutral
            self.img = self.BIRD_IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2: #5th - 10th frames of cycle, wing at middle
            self.img = self.BIRD_IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3: #10th - 15th frames of cycle, wing at peak
            self.img = self.BIRD_IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4: #15th - 20th frames of cycle, wing at middle
            self.img = self.BIRD_IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1: #after 5*4 + 1 frames, the flapping animation cycle resets
            self.img = self.BIRD_IMGS[0]
            self.img_count = 0
                    
        #rotate the bird according to the tilt (self.tilt) it is currently set to
        rotated_bird = pygame.transform.rotate(self.img, self.tilt)
        #set the origin of the rotation to the center of the bird, instead of the default, which is at the top-left corner of the screen
        #this rectangle is drawn tightly around the bird
        rectangle = rotated_bird.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        
        #renders the bird onto the screen
        window.blit(rotated_bird, rectangle.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

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
        
def draw_window(window, bird, pipes, base):
    #draw the background image
    window.blit(BG_IMG, (0, 0))
    #draw the pipes
    for pipe in pipes:
        pipe.draw(window)
    #draw the base (moving base animation)
    base.draw(window)
    #draw the bird on top of it
    bird.draw(window)
    pygame.display.update()
    
def main():
    game = True
    while game:
        bird = Bird(230,350) #starting position of 200, 200 for the bird class
        base = Base(670)
        window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pipes = [Pipe(700)]
        addPipe = False
        clock = pygame.time.Clock()
        run = True
        startGame = False
        runOver = False
        score = 0
        
        while run:
            clock.tick(25) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
            for event in pygame.event.get(): #game loop where event represents some action by the user, such as typing, clicking, etc
                if event.type == pygame.QUIT: #if the x on the pygame window is clicked
                    run = False
                    game = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and not runOver: #disable controls when runOver
                        startGame = True
                        bird.jump()
            
            if startGame:
                #game over if bird touches the bottom of screen
                if bird.y > WIN_HEIGHT:
                    run = False
                
                pipes_to_remove = []
                addPipe = False
                for pipe in pipes:
                    
                    if pipe.collide(bird): #if the bird collides with the pipe
                        print('Collided')
                        runOver = True
                        bird.vel = 0 #set velocity of bird to 0 to send it into nosedive
                    
                    if not pipe.passed and bird.x > pipe.x: 
                        score += 1
                        pipe.passed = True #sets pipe.passed to True to prevent this from registering over and over
                        addPipe = True #spawn another pipe whenever the bird passes a pipe
                        
                    if pipe.x + pipe.PIPE_TOP.get_width() < 0: #if the pipe is completely off the screen
                        pipes_to_remove.append(pipe) #add this pipe to the list of pipes that needs to be removed
                    if not runOver:
                        pipe.move()
                    
                if len(pipes_to_remove) > 0:
                    for pipe_to_remove in pipes_to_remove:
                        pipes.remove(pipe_to_remove)
                    pipes_to_remove = []
                    
                if addPipe: #spawn a new pipe if addPipe is true, then set addPipe back to false after finished adding
                    pipes.append(Pipe(700))
                
                bird.move()
            if not runOver:
                base.move()
            draw_window(window, bird, pipes, base)
            
    pygame.quit()
    
main()