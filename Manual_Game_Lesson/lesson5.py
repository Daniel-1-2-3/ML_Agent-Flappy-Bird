import pygame
import os
import time
import random

WIN_WIDTH = 500
WIN_HEIGHT = 750

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

class Bird:
    def __init__(self):
        self.x = 230
        self.y = 360
        self.animation_frames = [BIRD_IMGS[0], BIRD_IMGS[0], BIRD_IMGS[0], BIRD_IMGS[1],
                                 BIRD_IMGS[1], BIRD_IMGS[1], BIRD_IMGS[2], BIRD_IMGS[2], BIRD_IMGS[2]]
        self.animation_frames_count = 0
        self.current_bird_frame = self.animation_frames[0]
        
        self.initial_vel = -10.5 #the initial velocitied generated whenever we make the bird jump
        self.tick_count = 0 #how many frames it has been since we last jumped
        self.tilt = 0
        self.last_jump_height = self.y
        
    def move(self):
        self.tick_count += 1
        displacement = self.initial_vel * self.tick_count + 1.5 * self.tick_count**2
        if displacement > 16:
            displacement = 16
        self.y += displacement
        
        if displacement < 0 or self.y < self.last_jump_height:
            self.tilt = 25
        else:
            self.tilt = -40
        
    def jump(self):
        self.tick_count = 0
        self.last_jump_height = self.y
        
    def draw(self, window):
        #animating the bird
        if self.animation_frames_count > 8:
            self.animation_frames_count = 0
        self.current_bird_frame = self.animation_frames[self.animation_frames_count]
        self.animation_frames_count += 1
        
        #tilting the bird
        #rotate the bird according to the tilt (self.tilt) it is currently set to
        rotated_bird = pygame.transform.rotate(self.current_bird_frame, self.tilt)
        #set the origin of the rotation to the center of the bird, instead of the default, which is at the top-left corner of the screen
        #this rectangle is drawn tightly around the bird
        rectangle = rotated_bird.get_rect(center=self.current_bird_frame.get_rect(topleft = (self.x, self.y)).center)
        #renders the bird onto the screen
        window.blit(rotated_bird, rectangle.topleft)

class Pipe:
    def __init__(self):
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #flip_y is True, flip_x is False   
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.x = 700
        self.gap = 170
        self.vel = 5 #how many pixels to move the pipe to the left each frame
        self.height = random.randrange(50, 450) #y coordiante of the TOP of the gap that the bird passes through 
        self.top = self.height - self.PIPE_TOP.get_height() #y coordinates for top left corner of the top pipe and bottom pipe, used to draw them
        self.bottom = self.height + self.gap
        self.passed = False #has this pipe been passed yet?
        
    def move(self):
        self.x -= self.vel #every frame, move the pipe to the left a little bit
        
    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
        
class Base:
    def __init__(self):
        self.y = 670
        self.VEL = 5
        self.WIDTH = BASE_IMG.get_width()
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        elif self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, window):
        window.blit(BASE_IMG, (self.x1, self.y))
        window.blit(BASE_IMG, (self.x2, self.y))
        
def draw_window(window, base, bird, pipes):
    window.blit(BG_IMG, (0, 0))
    bird.draw(window)
    for pipe in pipes:
        pipe.draw(window)
    base.draw(window)
    pygame.display.update()
    
def main():
    pygame.init()
    
    game = True
    while game:
        run = True
        clock = pygame.time.Clock()
        window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        base = Base()
        bird = Bird()
        pipes = [Pipe()]
        start_run = False
        while run:
            clock.tick(30) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
            for event in pygame.event.get(): #game loop where event represents some action by the user, such as typing, clicking, etc
                if event.type == pygame.QUIT: #if the x on the pygame window is clicked
                    run = False
                    game = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        start_run = True
                        bird.jump()
                        
            if start_run:
                
                bird.move()
                if bird.y + bird.current_bird_frame.get_height()> WIN_HEIGHT or bird.y < 0:
                    run = False
                    start_run = False
                
                pipe_to_remove = None
                add_pipe = False
                for pipe in pipes:
                    if bird.x > pipe.x and not pipe.passed:
                        pipe.passed = True
                        add_pipe = True
                    if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                        pipe_to_remove = pipe
                    pipe.move()

                if pipe_to_remove !=  None:
                    pipes.remove(pipe_to_remove)
                if add_pipe:
                    pipes.append(Pipe())
                
            base.move()
            draw_window(window, base, bird, pipes)
        time.sleep(0.5)

main()