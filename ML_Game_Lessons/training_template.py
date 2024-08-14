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
pygame.init()

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
        
def draw_window(window, birds, pipes, base, score, generation):
    #draw the background image
    window.blit(BG_IMG, (0, 0))
    #draw the pipes
    for pipe in pipes:
        pipe.draw(window)
    #draw the base (moving base animation)
    base.draw(window)
    #draw the bird on top of it
    for bird in birds:
        bird.draw(window)
    #put the score
    font = pygame.font.Font(None, 36) #default font, 36 size
    fontLabel = font.render(f"Score: {score}", True, (255, 255, 255))  #text is white
    labelRect = fontLabel.get_rect(center=(70, 40)) #create a rectangle around the text, invisble, used for positioning
    window.blit(fontLabel, labelRect)
    #put the generation
    genLabel = font.render(f"Gen: {generation}", True, (255, 255, 255))
    genLabelRect = fontLabel.get_rect(center=(70, 80))
    window.blit(genLabel, genLabelRect)
    pygame.display.update()
    
generation = 0

def eval_genomes(genomes_tuple, config):
    #remember the genomes is a list of 30 genomes for 30 neural networks that will be used to control the birds
    #the input genomes_tuple list contains both the id of each genome and the their value, we wish to extract just the value and put it into the genomes list
    genomes = [] #genetic information are the weight and bias values of those neural networks
    birds = [] #will contain 30 birds
    nets = [] #this list will contain 30 neural networks
    
    #iterate through each genome
    for genome_id, genome in genomes_tuple:
        genome.fitness = 0 #initialize the fitness score to 0
        net = neat.nn.FeedForwardNetwork.create(genome, config) #load the genomes into the neural network
        nets.append(net)
        birds.append(Bird())
        genomes.append(genome)
    
    base = Base()
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pipes = [Pipe()]
    addPipe = False
    clock = pygame.time.Clock()
    run = True
    score = 0
    
    global generation
    generation += 1
        
    while run and len(birds) > 0: #loop breaks if no more birds are alive
        clock.tick(30) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
        for event in pygame.event.get(): #game loop where event represents some action by the user, such as typing, clicking, etc
            if event.type == pygame.QUIT: #if the x on the pygame window is clicked
                run = False
                pygame.quit()
                quit()

        #in the list of pipes, there could be more than 1 or 2 pipes, need to determine which one to use for the calculations
        pipe_index = 0
        if len(pipes) > 0:
            #if the bird if ahead of the first pipe, use the second pipe's location
            #otherwise, case where bird hasn't passed the first pipe, and second pipe is still off screen, use the first pipe's location
            if birds[0].x > (pipes[0].x + pipes[0].PIPE_TOP.get_width()):
                pipe_index = 1
            
        for i, bird in enumerate(birds): #reward the bird every time it moves forward
            bird.move()
            #small reward for moving forwards, by having 0.1 added to fitness point every frame the bird moves forward
            #since this game runs at 30 frames/second, this means +3 fitness score every second  
            genomes[i].fitness += 0.1
            #pass in 3 inputs to the neural network (bird y pos, distance to top pipe, distance to bottom pipe), and get the result (number between -1 to 1, due to the activation fucntion)
            output = nets[i].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom), abs(bird.x - pipes[pipe_index].x)))
            if output[0] > 0.5: #jump if the nueral network outputs more than 0.5
                bird.jump()
            
        pipes_to_remove = []
        addPipe = False
        for pipe in pipes: 
            pipe.move()
            for bird in birds: #iterate through list of 30 birds/genomes
                if pipe.collide(bird): #if the bird collides with the pipe
                    genomes[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird)) #remove the neural netork at index i, whch correponds to the bird that collided 
                    genomes.pop(birds.index(bird))
                    birds.pop(birds.index(bird)) #remove the bird at index i, which is the bird that collided
                    
                if not pipe.passed and bird.x > pipe.x: #if the bird passed the pipe
                    pipe.passed = True #sets pipe.passed to True to prevent this from registering over and over
                    addPipe = True #spawn another pipe whenever the bird passes a pipe
                    score += 1
                    for genome in genomes:
                        genome.fitness += 5 #if the bird goes through the pipe reward it with 5 fitness points
                            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: #if the pipe is completely off the screen
                pipes_to_remove.append(pipe) #add this pipe to the list of pipes that needs to be removed
                    
        if len(pipes_to_remove) > 0:
            for pipe_to_remove in pipes_to_remove:
                pipes.remove(pipe_to_remove)
                    
        if addPipe: #spawn a new pipe if addPipe is true, then set addPipe back to false after finished adding
            pipes.append(Pipe())
            
        #check if any of the birds hit the ground or fly too high off screen, remove them
        for bird in birds:
            if bird.y > 750 or bird.y <= 0:
                nets.pop(birds.index(bird)) #remove the neural netork at index i, whch correponds to the bird that collided 
                genomes.pop(birds.index(bird))
                birds.pop(birds.index(bird)) #remove the bird at index i, which is the bird that collided
                
        base.move()
        draw_window(window, birds, pipes, base, score, generation)
        
        if score >= 30: #if the score is over 30, it means a perfect bird has already been created
            break
        
    time.sleep(0.5)

def run_evolution(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_file) #the variable config here is the configruation file fully loaded in
    algorithm = neat.Population(config) #initialize the NEAT algorithm with the parameters specified in the configuration file
    #population.run will pass the eval_genomes function (thats the fitness function) two parameters:
    #1. The genomes for the 30 neural networks that will be evaluated in the fitness function (The population of the current generation)
    #2. The entire configuration file contents 
    winner = algorithm.run(eval_genomes, 50) #running the fitness function 50 times, means we are evaluating populations of 50 generations of birds to perfect the neural networks's accuracy
    print('\nWinner\n\n', winner)
    #save the weights and bias of the perfect bird/neural network to a file so it can be used in the future
    with open('winning_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__) #gets the directory that we are currently in
    config_path = os.path.join(local_dir, "config.txt") #find the path to the config.txt file
    run_evolution(config_path) #run the AI training 