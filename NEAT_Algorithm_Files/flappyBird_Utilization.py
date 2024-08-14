import pygame
import os
import sys
import neat 
import pickle

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from components.bird import Bird
from components.base import Base
from components.pipe import Pipe

WIN_WIDTH = 500
WIN_HEIGHT = 750

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

def loadNeuralNetwork():
    local_dir = os.path.dirname(__file__) #gets the directory that we are currently in
    config_file = os.path.join(local_dir, "config.txt") #find the path to the config.txt file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_file)
    with open('NEAT_Algorithm_Files\\winning_genome.pkl', 'rb') as f:
        perfect_genome = pickle.load(f)
    neural_network = neat.nn.FeedForwardNetwork.create(perfect_genome, config)
    return neural_network
    
def draw_window(window, bird, pipes, base, score, pipe_index):
    #draw the background image
    window.blit(BG_IMG, (0, 0))
    #draw the pipes
    for pipe in pipes:
        pipe.draw(window)
    #draw the base (moving base animation)
    base.draw(window)
    #draw the bird on top of it
    bird.draw(window)
    #put the score
    font = pygame.font.Font(None, 36) #default font, 36 size
    fontLabel = font.render(f"Score: {score}", True, (255, 255, 255))  #text is white
    labelRect = fontLabel.get_rect(center=(70, 40)) #create a rectangle around the text, invisble, used for positioning
    window.blit(fontLabel, labelRect)
    
    #draw lines that represent what input the neural network is taking
    #pygame.draw.line(window, (200, 0, 0), ((bird.x + bird.img.get_width()/2), (bird.y + bird.img.get_height()/2)), (pipes[pipe_index].x + pipes[pipe_index].PIPE_BOTTOM.get_width()/2, pipes[pipe_index].height), 3)
    #pygame.draw.line(window, (200, 0, 0), ((bird.x + bird.img.get_width()/2), (bird.y + bird.img.get_height()/2)), (pipes[pipe_index].x + pipes[pipe_index].PIPE_BOTTOM.get_width()/2, pipes[pipe_index].bottom), 3)
    
    pygame.display.update()
    
def main():
    pygame.init()
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
            clock.tick(30) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
            for event in pygame.event.get(): #game loop where event represents some action by the user, such as typing, clicking, etc
                if event.type == pygame.QUIT: #if the x on the pygame window is clicked
                    run = False
                    game = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or pygame.K_UP and not runOver: #disable controls when runOver
                        startGame = True

            pipe_index = 0
            if bird.x > (pipes[0].x + pipes[0].PIPE_TOP.get_width()):
                pipe_index = 1
                
            net = loadNeuralNetwork()
            output = net.activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom), abs(bird.x - pipes[pipe_index].x)))
            if output[0] > 0.5:
                bird.jump()
            
            if startGame:
                #game over if bird touches the bottom of screen
                if bird.y > WIN_HEIGHT:
                    run = False
                
                pipes_to_remove = []
                addPipe = False
                for pipe in pipes:
                    
                    if pipe.collide(bird): #if the bird collides with the pipe
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
                        pipe_index -= 1
                    pipes_to_remove = []
                    
                if addPipe: #spawn a new pipe if addPipe is true, then set addPipe back to false after finished adding
                    pipes.append(Pipe(700))
                
                bird.move()
            if not runOver:
                base.move()
            draw_window(window, bird, pipes, base, score, pipe_index)
            
    pygame.quit()
    
main()