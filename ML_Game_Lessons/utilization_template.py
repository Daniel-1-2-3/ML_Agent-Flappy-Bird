import pygame
import os
import time
import random
import pickle
import neat 

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
        self.current_bird = self.animation_frames[0]
        
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
        self.current_bird = self.animation_frames[self.animation_frames_count]
        self.animation_frames_count += 1
        
        #tilting the bird
        #rotate the bird according to the tilt (self.tilt) it is currently set to
        rotated_bird = pygame.transform.rotate(self.current_bird, self.tilt)
        #set the origin of the rotation to the center of the bird, instead of the default, which is at the top-left corner of the screen
        #this rectangle is drawn tightly around the bird
        rectangle = rotated_bird.get_rect(center=self.current_bird.get_rect(topleft = (self.x, self.y)).center)
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
    
    def collide(self, bird):
        bird_mask = pygame.mask.from_surface(bird.current_bird) #get a mask (mask is explained in the slideshow)
        top_pipe_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_pipe_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y)) #distance between the bird and the top pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) #distance between the bird and the bottom pipe
        
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
        
def loadNeuralNetwork():
    local_dir = os.path.dirname(__file__) #gets the directory that we are currently in
    config_file = os.path.join(local_dir, "config.txt") #find the path to the config.txt file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_file)
    with open('NEAT_Algorithm_Files\\winning_genome.pkl', 'rb') as f:
        perfect_genome = pickle.load(f)
    neural_network = neat.nn.FeedForwardNetwork.create(perfect_genome, config)
    return neural_network

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
    net = loadNeuralNetwork()
    
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
                
                pipe_index = 0
                if bird.x > (pipes[0].x + pipes[0].PIPE_TOP.get_width()):
                    pipe_index = 1
                
                output = net.activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom), abs(bird.x - pipes[pipe_index].x)))
                if output[0] > 0.5:
                    bird.jump()
                
                bird.move()
                if bird.y + bird.current_bird.get_height() > WIN_HEIGHT or bird.y < 0:
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
                    if pipe.collide(bird):
                        run = False
                        start_run = False
                    pipe.move()

                if pipe_to_remove !=  None:
                    pipes.remove(pipe_to_remove)
                if add_pipe:
                    pipes.append(Pipe())
                
            base.move()
            draw_window(window, base, bird, pipes)
        time.sleep(0.5)

main()