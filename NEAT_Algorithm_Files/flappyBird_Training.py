import pygame
import neat
import os
import sys
import time
import pickle 

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from components.bird import Bird
from components.base import Base
from components.pipe import Pipe

WIN_WIDTH = 500
WIN_HEIGHT = 750

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
pygame.init()
        
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
    #remember the genomes is a list of 30 pieces of genetic information for 30 neural networks that will be used to control the birds
    #the input genomes_tuple list contains both the id of each genome and the their value, we wish to extract just the value and put it into the genomes list
    genomes = [] #genetic information are the weight and bias values of those neural networks
    birds = [] #will contain 30 birds
    nets = [] #this list will contain 30 neural networks
    
    #iterate through each genome
    for genome_id, genome in genomes_tuple:
        genome.fitness = 0 #initialize the fitness score to 0
        net = neat.nn.FeedForwardNetwork.create(genome, config) #load the genetic information into the neural network
        nets.append(net)
        birds.append(Bird(230, 350))
        genomes.append(genome)
    
    base = Base(670)
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pipes = [Pipe(700)]
    addPipe = False
    clock = pygame.time.Clock()
    run = True
    score = 0
    
    global generation
    generation += 1
        
    while run and len(birds) > 0: #loop breaks if no more birds are alive
        clock.tick(100) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
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
            pipes.append(Pipe(700))
            
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
    population = neat.Population(config) #generate a population of birds based on the config file
    #add stat reporters, print statistics on how the algorithm is performing on the console while the program runs (optional)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    
    #population.run will pass the eval_genomes function (thats the fitness function) two parameters:
    #1. The genomes for the 30 neural networks that will be evaluated in the fitness function (The population of the current generation)
    #2. The entire configuration file contents 
    winner = population.run(eval_genomes, 50) #running the fitness function 50 times, means we are evaluating populations of 50 generations of birds to perfect the neural networks's accuracy
    print('\nWinner\n\n', winner)
    #save the weights and bias of the perfect bird/neural network to a file so it can be used in the future
    with open('NEAT_Algorithm_Files\\winning_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__) #gets the directory that we are currently in
    config_path = os.path.join(local_dir, "config.txt") #find the path to the config.txt file
    run_evolution(config_path) #run the AI training 