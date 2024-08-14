import pygame
import os

WIN_WIDTH = 500
WIN_HEIGHT = 750

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
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
    
    def draw(self, window):
        if self.animation_frames_count > 8:
            self.animation_frames_count = 0
        self.current_bird_frame = self.animation_frames[self.animation_frames_count]
        self.animation_frames_count += 1
        
        window.blit(current_bird_frame, (self.x, self.y))
        
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
        
def draw_window(window, base, bird):
    window.blit(BG_IMG, (0, 0))
    base.draw(window)
    bird.draw(window)
    pygame.display.update()
    
def main():
    pygame.init()
    run = True
    clock = pygame.time.Clock()
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    base = Base()
    bird = Bird()
    while run:
        clock.tick(30) #limits the FPS that the game runs at. This line limits the FPS of the game to 30 FPS
        for event in pygame.event.get(): #game loop where event represents some action by the user, such as typing, clicking, etc
            if event.type == pygame.QUIT: #if the x on the pygame window is clicked
                run = False
        base.move()
        draw_window(window, base, bird)

main()