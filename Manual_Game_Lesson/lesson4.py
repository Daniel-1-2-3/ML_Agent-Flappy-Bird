import pygame
import os
import time

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
    
    game = True
    while game:
        run = True
        clock = pygame.time.Clock()
        window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        base = Base()
        bird = Bird()
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
                
            base.move()
            draw_window(window, base, bird)
        time.sleep(0.5)

main()