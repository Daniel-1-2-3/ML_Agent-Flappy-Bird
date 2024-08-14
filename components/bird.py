import pygame
import os

#load images, and scale to double the size
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), 
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))] 

class Bird:
    BIRD_IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #rotation used later for tilting the bird, during up/down movement 
    ROT_VEL = 10 #rotation velocity, speed at which the bird rotates (number of degrees rotated per frame)
    ANIMATION_TIME = 5

    def __init__ (self, x, y): 
        #initialize the starting position of the bird, and starting tilt
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0 #tick_count keeps track of how many frames went by since the bird last jumped
        self.vel = -10.5 #pixels/frame
        self.height = self.y #height will be used during each jump, to record the height at which the bird starting the jump from
        self.img_count = 0 #the flapping animation cycle goes through 3 different images of the bird, with wings at different angles. 
        #each image should only be on the screen for 5 frames (ANIMATION_TIME = 5). img_count keeps track of hong many frames each image has already been on the screen for
        self.img = self.BIRD_IMGS[0] #starting with the default position of the bird (no flapping wings)
    
    def jump(self):
        self.tick_count = 0 #reset the value
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        #calculates how many pixels the bird should move up/down in this frame, due to gravity and flapping
        #using the physics equation (v)(t) + 1/2(a)(t^2), where v is the initial accelaration, t is time, and a is acceleration
        #tick_count is equivelant to time in the video game, as one frame passing represents one unit of time
        #self.vel * tick_count calculates the initial displacement due to flapping. (1.5*self.tick_count**2) simulates the bird falling due to "gravity"
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count**2 
        
        if displacement >= 16:
            #if we are moving more than 16 pixels/units up/down, just set the amount of movement to 16 pixels. Prevents too much acceleration to the bird
            displacement = 16
    
        self.y = self.y + displacement
        if self.y < 0: #prevent bird from flying too high and out of frame
            self.y = 0
        
        #tilt the bird upwards if it is currently jumping, or its position is anywhere above where it last jumped from
        if displacement < 0 or self.y < self.height:
            if self.tilt < self.MAX_ROTATION: #this is for cautionary purposes, not nessecarily needed, makes sure bird cannot tilt more than max rotation (25 deg)
                self.tilt = self.MAX_ROTATION
        #tilt the bird downwards otherwise, this is process of making the bird tilt more and more downwards as it falls, until it reaches 90 degs (pointing straight down)
        else:
            if self.tilt >= -90:
                self.tilt -= self.ROT_VEL
                
    def draw(self, window): #draw the bird onto the screen, animate it
        #this following code will draw the flapping animation of the bird, it is a cycle
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME: #first 5 frames of cycle, bird is neutral
            self.img = self.BIRD_IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2: #5th - 10th frames of cycle, wing at middle
            self.img = self.BIRD_IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3: #10th - 15th frames of cycle, wing at peak
            self.img = self.BIRD_IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4: #15th - 20th frames of cycle, wing at middle
            self.img = self.BIRD_IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1: #after 5*4 + 1 frames, the flapping animation cycle resets
            self.img = self.BIRD_IMGS[0]
            self.img_count = 0
                    
        #rotate the bird according to the tilt (self.tilt) it is currently set to
        rotated_bird = pygame.transform.rotate(self.img, self.tilt)
        #set the origin of the rotation to the center of the bird, instead of the default, which is at the top-left corner of the screen
        #this rectangle is drawn tightly around the bird
        rectangle = rotated_bird.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        
        #renders the bird onto the screen
        window.blit(rotated_bird, rectangle.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)