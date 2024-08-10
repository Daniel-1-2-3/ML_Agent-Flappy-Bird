import pygame
import os
from components.bird import Bird
from components.base import Base
from components.pipe import Pipe

WIN_WIDTH = 500
WIN_HEIGHT = 750

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
        
def draw_window(window, bird, pipes, base, score):
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
                    pipes_to_remove = []
                    
                if addPipe: #spawn a new pipe if addPipe is true, then set addPipe back to false after finished adding
                    pipes.append(Pipe(700))
                
                bird.move()
            if not runOver:
                base.move()
            draw_window(window, bird, pipes, base, score)
            
            print(len(pipes))
            
    pygame.quit()
    
main()