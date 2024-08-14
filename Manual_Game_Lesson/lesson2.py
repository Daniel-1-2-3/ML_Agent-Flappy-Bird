import pygame
import os

WIN_WIDTH = 500
WIN_HEIGHT = 750

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))

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
        
def draw_window(window, base):
    window.blit(BG_IMG, (0, 0))
    base.draw(window)
    pygame.display.update()
    
def main():
    pygame.init()
    run = True
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    base = Base()
    while run:
        clock.tick(30) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
        for event in pygame.event.get(): #game loop where event represents some action by the user, such as typing, clicking, etc
            if event.type == pygame.QUIT: #if the x on the pygame window is clicked
                run = False
        base.move()
        draw_window(window, base)

main()