import pygame
import os

WIN_WIDTH = 500
WIN_HEIGHT = 750

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

def draw_window(window):
    window.blit(BG_IMG, (0, 0))
    pygame.display.update()
    
def main():
    pygame.init()
    run = True
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    while run:
        clock.tick(30) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
        for event in pygame.event.get(): #game loop where event represents some action by the user, such as typing, clicking, etc
            if event.type == pygame.QUIT: #if the x on the pygame window is clicked
                run = False
        draw_window(window)

main()