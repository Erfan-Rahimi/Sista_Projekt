# File: Shooter 
# Author: Erfan Rahimi
# Date: 2024-05-23
# Description: This is a 2D shooter game made in python that is mainly created for 
# entertainment purposes. 

#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Load all the important libraries and files 
import pygame 
from pygame import mixer 
import os 
import random 
import csv
import button 

#Inishelize pygame and mixer for handling sound 
pygame.init()
mixer.init()

# Set the screen dimensions 
SCREEN_WIDTH = 800 
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)


#We assign the game window to a variable with our previous variables and give our screen a name 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Poop')

#Set our framerate
clock = pygame.time.Clock()
FPS = 60 

# Define game variables 
GRAVITY = 0.75
SCROLL_THRESH = 200 # Threashold for scrolling the screen
ROWS = 16 # Number of rows for each level 
COLS = 150 # Number of collumns for each level 
TILE_SIZE = SCREEN_HEIGHT // ROWS # Size of each tile in our levels
TILE_TYPES = 21 # 21 different tile types 
MAX_LEVELS = 2 # Max level is two. We only have two maps.
screen_scroll = 0 # Track screen scroll
bg_scroll = 0 # Track background scroll
level = 1 # Current level is level one.
start_game = False # Boolean to indicate that the game is started
dying_sound = False # Boolean to indicate that the dying sound has been played 

#Define the player action variables 
moving_left = False 
moving_right = False 
shoot = False 
rocket = False 
grenade = False 
grenade_thrown = False
end = True 

#load music and sounds 
pygame.mixer.music.load('audio/103.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 5000) # Loop the background music 
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)
dying_fx = pygame.mixer.Sound('audio/yoda.mp3')
dying_fx.set_volume(0.5)
music_fx = pygame.mixer.Sound('audio/103.mp3')
music_fx.set_volume(0.5)
end_music = pygame.mixer.Sound('audio/end.mp3')


#load images 
#Background images 
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
menu_img = pygame.image.load('img/Background/menu.jpg').convert_alpha()
ending_img = pygame.image.load('img/Background/winner.jpg').convert_alpha()
#Button images 
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

#Store all the tiles in one list 
img_list = [] # Create empty list 
for x in range(TILE_TYPES): # Go through all the tiles 
	img = pygame.image.load(f'img/Tile/{x}.png') # The f'img/Tile/{x}.png' string is a formatted string that dynamically creates the path for each tile image based on the current value of x. For example, if x is 0, it loads img/Tile/0.png; if x is 1, it loads img/Tile/1.png, and so on. This way, it systematically loads all tile images.
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) # Changes the sizes of the pictures to a desired size
	img_list.append(img) # Put the img into the list.
    
# Its our weapons. Bullets, rockets and grenades.
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
rocket_img = pygame.image.load('img/icons/rocket.png').convert_alpha()
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

# Loot boxes.
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()

# Create a dictionary that will load the different boxes 
item_boxes = {
    'Health' : health_box_img,
    'Ammo'   : ammo_box_img,
    'Grenade' : grenade_box_img

}




#Define our colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0,0,0)

#define font 
font = pygame.font.SysFont('Futura', 30)



# This function draws an text on the screen
# font.render() creates a new surface with the text onto it 
# text is the string to render, True makes the text look smoother and text_col the colour.
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col) 
    screen.blit(img, (x, y)) # Draws on the specified coordinates

#Update our background to avoid picture cloning for out character.
#Also we have added some pictures for the background scenary that will use to scroll the map with. 
def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5,0))
        screen.blit(mountain_img, ((x * width)  - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width)  - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() -150 ))
        screen.blit(pine2_img, ((x * width)  - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height() ))


# When ever we restart a level or go to the next one, each list is emptied 
# This makes sure so that the game runs a bit more smoothly.
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    water_group.empty()
    decoration_group.empty()
    exit_group.empty()

    #create empty tile list. This takes our tile numbers and draws them out.
    data = []
    for row in range(ROWS):
        r = [-1] * COLS 
        data.append(r)
    return data 


# Creates our menu for us at the bigenning of the game.
def draw_menu():
    screen.fill(BG)
    scaled_menu_img = pygame.transform.scale(menu_img, (SCREEN_WIDTH, SCREEN_HEIGHT + 200))
    menu_rect = menu_img.get_rect()
    menu_rect.topleft = (0,0)
    screen.blit(scaled_menu_img, menu_rect)


# This is a soldier class that is a blueprint for all the enemies and player.
# It takes all the listed arguments.
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades, rockets):
        pygame.sprite.Sprite.__init__(self)

        # Inizialize all the attributes 
        self.alive = True 
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo 
        self.rockets = rockets 
        self.start_ammo = ammo 
        self.shoot_cooldown = 0 
        self.grenades = grenades 
        self.health = 100
        self.max_health = self.health

        # Direction the soldier is facing (1 for right, -1 for left)
        self.direction = 1
        self.vel_y = 0 # Vertical velocity
        self.jump = False # Look if the soldier is jumping
        self.flip = False # Indicates if the image of the soldier should be flipped
        self.in_air = True # Indicates if the soldier is in the air 


        # We need to create a animation list for out characters movements 
        self.animation_list = []
        self.frame_index = 0 # Current frame index
        self.action = 0 
        self.update_time = pygame.time.get_ticks()

        #Create ai specific variables 
        self.move_counter = 0 
        self.vision = pygame.Rect(0, 0, 150, 20) # The ai vision
        self.idling = False # See if ai is walking 
        self.idling_counter = 0 
       
       # We will create a list for all types of animations
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = [] # We create a temporary list 
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}')) # We do not know how many pictures each folder has, therefore we will count the number of files in each folder
            for i in range(num_of_frames):
                img = pygame .image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha() # Load the images
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))) # Change its size
                temp_list.append(img) # Append the pictures and create sequences
            self.animation_list.append(temp_list) # Create a list of list

        # Set the current image to the current action and frame indexes.
        # Create the player rectangle and indicate where its center is.
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    # Update the animation and check if the soldier is alive 
    #update cooldown for shooting.
    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    #Our moving method and reset movement variables 
    def move(self, moving_left, moving_right):
        screen_scroll = 0 
        dx = 0 
        dy = 0 

        # Assign movement variables if moving left or right ( Based on input )
        if moving_left:
            dx = -self.speed
            self.flip = True 
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False  
            self.direction = 1
        
        # Handle jumping 
        if self.jump == True and self.in_air == False:
            self.vel_y = -13
            self.jump = False 
            self.in_air = True 

        #apply gravity 
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y 
        dy += self.vel_y

        #Check collision. Checking collision in the x direction and y direction seperatly
        #Check collision in the x direction, but it is increased by 5 pixels so that it can detect is easier.
        #In that case it stops moving 
        # We will use our obstacle list 
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): 
                dx = 0 

                #if the ai has hit a wall, then make it turn around 
                if self.char_type == 'enemy':
                    self.direction *= -1 
                    self.move_counter = 0 

            #Check for collision in the y direction. Same thing but now we are looking up and down with + 5 px.
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):

                #Check if you are low, in other words, jumping
                if self.vel_y < 0:
                    self.vel_y = 0 
                    dy = tile[1].bottom - self.rect.top

                #check if above the ground, in other words falling 
                elif self.vel_y >= 0:
                    self.vel_y = 0 
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #Check collision with water 
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0 

        #Check collision with sign 
        level_complete = False 
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True 


        
        #Check for player falling of
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0 

        #see if the player has gone off the edge of the screen 
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0 

        #Update rectangle position 
        self.rect.x += dx 
        self.rect.y += dy 

        #Scroll depending on the players position 
        # It is only the player that can effect that.
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    # Method for all the shooting and where the bullets come from. And when you have no more. It wont shoot
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + ( self.direction * (self.rect.size[0])* 0.8), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1

    # Same thing as the bullet but for rockets 
    def shoot_rocket(self):
        if self.shoot_cooldown == 0 and self.rockets > 0:
            self.shoot_cooldown = 20
            rocket = Rocket(self.rect.centerx + ( self.direction * (self.rect.size[0])* 0.6), self.rect.centery, self.direction)
            rocket_group.add(rocket)
            #reduce ammo
            self.rockets -= 1

    #Define ai behavior
    def ai(self):
        # Randomly decide if the AI should idle when it is alive ( 0.5% chanse)
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True 
                self.idling_counter = 50 # It should idle a number of frames

            # Check if the ai is near the player, in that case shoot
            if self.vision.colliderect(player.rect):
                self.update_action(0) 
                self.shoot()
            else:
                # Determine the direction, either left or right 
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else :
                        ai_moving_right = False 
                    ai_moving_left = not ai_moving_right

                    # Update the animation and movement 
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1

                    #update ai vision as the enemy moves 
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    # Check if AI has moved a full tile (indicating it should turn around)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    # Stop idling when the counter reaches zero.
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #scroll/ this is moving the enemies.
        self.rect.x += screen_scroll

    #Method for updating the character animation 
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN: #check if enough time has passed since the last update 
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # When our animation pictures run out, we will reset from the first image 
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0 

    #Create method to handle our actions
    #Check if new action is different to the previous one
    #Update the animation time 
    def update_action(self, new_action):
        if new_action != self.action: 
            self.action = new_action
            self.frame_index = 0 
            self.update_time = pygame.time.get_ticks()
    
    #Method to check if the enemy or the player is dead
    #If the health goes down to 0, player or enemy stops in motion and they die
    def check_alive(self):
        if self.health <= 0:
            self.health = 0 
            self.speed = 0 
            self.alive = False 
            self.update_action(3)

    #We have to use a blit function and draw on our screen
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)



# This will help us to transform our csv file into our map 
class World():
    def __init__(self):
        self.obstacle_list = []

    # Process and convert the data to create the map. 
    # Here we level length based on the amount of columns and iterate through each value un level data file  
    def  process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile] # Get the correct image for the tile
                    img_rect = img.get_rect()

                    # Allows us to have a adjustable tile size 
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)

                    # These are the only tiles that are colidble. We represent them as number and the 
                    # code detects it based on the integer
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x*TILE_SIZE, y*TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <=14: # Just some fine decoration tiles
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: #This is our player, therefore we will create a player
                        player = Soldier('player', x *TILE_SIZE, y*TILE_SIZE, 1.65, 5, 20, 5, 2)
                        health_bar = HealthBar(10, 10, player.health, player.health) 
                    elif tile == 16: #We will create enemies 
                        enemy = Soldier('enemy', x*TILE_SIZE, y*TILE_SIZE, 1.65, 2, 20, 0, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: #Our ammo box 
                        item_box = ItemBox('Ammo', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18: #Gernade 
                        item_box = ItemBox('Grenade', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19: #Health 
                        item_box = ItemBox('Health',  x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20: # Our exit 
                        exit = Exit(img, x*TILE_SIZE, y*TILE_SIZE)
                        exit_group.add(exit)

        # Return the player and health bar objects for further use 
        return player, health_bar
    
    # Here we are iterating through the map and creating only 
    # the obstacle / the colidables 
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll # Adjust the tile's x-coordinate based on screen scroll
            screen.blit(tile[0], tile[1]) # Draw the tile image at the updated position

# Class for decorative elements such as grass
class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img 
        self.rect= self.image.get_rect()
        # Positioning our image or box in the middle of the grid 
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    # Method to update the position of the decoration
    def update(self):
        self.rect.x += screen_scroll


#Water class that represents water tiles 
class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img 
        self.rect= self.image.get_rect()
        # Positioning our image or box in the middle of the grid 
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


# Class for representing the exit points for each level 
class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img 
        self.rect= self.image.get_rect()
        # Positioning our image or box in the middle of the grid 
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
     self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        # Depending on the collected item, we load a different picture 
        # We feed in an string and then It picks the different items for us 
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        # We are not going to place its positioning or coordinates in the center as we have done previously 
        #But rather, we place it on the top since it is not going to be the same size as our tiles 
        self.rect.midtop = (x + (TILE_SIZE * 0.5), y + (TILE_SIZE - self.image.get_height()))
    
    # Function that helps us scroll with background and check if the player has picked any boxes.
    def update(self):
          self.rect.x += screen_scroll
          if pygame.sprite.collide_rect(self, player):
            
            #Check what type of box it was and what it does 
            if self.item_type == 'Health':
                  player.health += 25 
                  if player.health > player.max_health:
                      player.health = player.max_health
            elif  self.item_type == 'Ammo':
                  player.ammo += 10 
            elif self.item_type == 'Grenade':
                  player.grenades += 3 
            # Delte the item box that was collected
            self.kill()


# Class that represents the healthbar 
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x 
        self.y = y 
        self.health = health 
        self.max_health = max_health  

    # function for drawing the updated health 
    def draw(self, health):
        self.health = health 
        # Calculate health ratio and draw with colour layers.
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20 ))


# We create the class for all bullets and they all share the same speed
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10 
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    # Update function for the bullet 
    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # Check if bullet has gone out of screen, in that case delete it 
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #Check for collision for level and tiles 
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #Check collision for bullet with characters and for damage
        # The enemies and the player can take damage 
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        
        #Same thing for the enemies 
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 8
                    self.kill()

# The rocket class is pretty much exactly like the bullet classs
# It has an explosion animation 
class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = rocket_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = 10 
    
    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
            

        #Turns the rocket when the player is turned around
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

         #Check for collision for level 
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
                explosion = Explosion(self.rect.x, self.rect.y, 0.5)
                explosion_group.add(explosion)
                
                # Make the rocket do damage to whatever inside of its radius 
                # Our explosion radius is our rectangle and then we compare the center of the players 
                # to the center of the grenade and if they are in the radius, they will take damage
                # We do the same to both the player and the enemy since the enemy has the ability to damage itself
                if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                    player.health -= 50
                elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 0.5 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 0.5:
                    player.health -= 100
                for enemy in enemy_group:
                    if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                        enemy.health -= 50
                    elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 0.5 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 0.5:
                        enemy.health -= 100

        #Same thing for the enemies 
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, rocket_group, False):
                if enemy.alive:
                    #When the bullets hit it does damage to the enemy 
                    enemy.health -= 50
                    self.kill()
                    explosion = Explosion(self.rect.x, self.rect.y, 0.5)
                    explosion_group.add(explosion)

                    # Make the rocket do damage to whatever inside of its radius 
                    # Our explosion radius is our rectangle and then we compare the center of the players 
                    # to the center of the grenade and if they are in the radius, they will take damage
                    # We do the same to both the player and the enemy since the enemy has the ability to damage itself
                    if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                        player.health -= 50
                    elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 0.5 and \
                        abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 0.5:
                        player.health -= 100
                    for enemy in enemy_group:
                        if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                            enemy.health -= 50
                        elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 0.5 and \
                            abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 0.5:
                            enemy.health -= 100

    

#Sprite class for grenades
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        # time for the grenade to blow up
        self.timer = 100  # Corrected to match the second version
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
    
    # Check the grenades position and apply gravity 
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # Check with collision with the tiles, collision in x direction
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1 # Reverse the direction when it hits a wall
                dx = self.direction * self.speed

            # 
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # Check if below the ground, in other words thrown
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if above the ground, in other words falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # Update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Create a timer that indicates the explosion of our grenade
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # Make the grenade do damage to whatever inside of its radius 
            # Our explosion radius is our rectangle and then we compare the center of the players 
            # to the center of the grenade and if they are in the radius, they will take damage
            # We do the same to both the player and the enemy since the enemy has the ability to damage itself
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
               abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            elif abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 0.5 and \
                 abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 0.5:
                player.health -= 100
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                   abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50
                elif abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 0.5 and \
                     abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 0.5:
                    enemy.health -= 100


# This class handles the explosions 
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        # We create a list for our gernade animatins and run through them one by one
        # We have 6 pictures in total and we scale them accordingly 
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0 
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # We add a counter for the gernade which is what shows the animation itself
        self.counter = 0 

    #We have to create an update method 
    def update(self): 
        self.rect.x += screen_scroll

        #How quickly the images change and animateun
        EXPLOSION_SPEED = 4 
        #Update explosion animation
        self.counter += 1 

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0 
            self.frame_index += 1
            # If the animation is complete, then we will delete the explosion 
            # And it depends on weather if we have reached the end of the image list that we had 
            # If we havent reached the end, then we will keep  loading the images 
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
    


    


# Create buttons 
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 +50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 85, SCREEN_HEIGHT // 2 - 20, restart_img, 1.5)


#create sprite groups 
bullet_group = pygame.sprite.Group()
rocket_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()






#Creating our map as a list of lists. Simliar to that of an text based adventure game 
world_data = []
# This is our rows. We have 16 rows and for each row we create the specific values 
#and everytime we do that we append that into our epmty world data list 
for row in range(ROWS):
    r = [-1] * COLS 
    world_data.append(r)
# load in level data 
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row): 
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)


# We want the screen to be constently running and not close 
run = True 
end = False 
while run:

    clock.tick(FPS)

    if start_game == False:
        #draw menu
        draw_menu()
        #Add the buttons 
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False 
        pass
    elif end:
        screen.fill(BG)

        if not pygame.mixer.music.get_busy():
            end_music.play()

        pygame.mixer.music.stop()
        scaled_ending_img = pygame.transform.scale(ending_img, (SCREEN_WIDTH, SCREEN_HEIGHT + 200))
        end_rect = ending_img.get_rect()
        end_rect.topleft = (0, 0)
        screen.blit(scaled_ending_img, end_rect)
        screen_scroll = 0 
        if restart_button.draw(screen):
            start_game = False  # Go back to the main menu
            end = False  # Exit the end state
            level = 1  # Reset to the first level
            world_data = reset_level()
            with open(f'level{level}_data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)
            world = World()
            player, health_bar = world.process_data(world_data)
                            # Stop ending music and reset background music
            end_music.stop()
            pygame.mixer.music.play(-1)
    else:

        #Call on our background function
        draw_bg()
        #draw world map
        world.draw()
        #show health bar 
        health_bar.draw(player.health) 
        #Show ammo 
        draw_text('AMMO:', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        #Show ammo 
        draw_text('GRENADES:', font, WHITE, 10, 70)
        for x in range(player.grenades):
            screen.blit(grenade_img, (150 + (x * 15), 70))
        #show rockets 
        draw_text('ROCKETS:', font, WHITE, 10, 110)
        for x in range(player.rockets):
            screen.blit(rocket_img, (130 + (x * 50), 110))
        

    
        #Call our draw method 
        player.update()
        # Call our draw method 
        player.draw()

        #Instead of just having one enemy, we iterate through the amount of enemies we have added
        # and they get depending on the arguments we give them 
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #Update and draw groups 
        bullet_group.update()
        bullet_group.draw(screen)

        #Update rocket group
        rocket_group.update()
        rocket_group.draw(screen)

        #update grenade group
        grenade_group.update()
        grenade_group.draw(screen)

        #update explosion group 
        explosion_group.update()
        explosion_group.draw(screen)

        #update item box groups 
        item_box_group.update()
        item_box_group.draw(screen)

        #Update exit
        exit_group.update()
        exit_group.draw(screen)

        #Update water 
        water_group.update()
        water_group.draw(screen) 

        #Update decoration
        decoration_group.update()
        decoration_group.draw(screen)





        # Update plyaer actions only when the player is alive 
        if player.alive:

            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
            #shoot bullets 
            if shoot:
                player.shoot()
            #shoot rocket
            elif rocket:
                player.shoot_rocket()
            #Shoot grenade
            elif grenade and grenade_thrown == False and player.grenades > 0: 
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                            player.rect.top, player.direction)
                grenade_group.add(grenade)
                #Grenades reduced 
                player.grenades -= 1
                grenade_thrown = True 
            if player.in_air:
                player.update_action(2) #2: jumping animation
            elif moving_left or moving_right:
                player.update_action(1)# 1: running
            else:
                player.update_action(0)# 0: Idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # Check i level is completed 
            if level_complete:
                level+= 1
                bg_scroll = 0 
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    screen.fill(BG)
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row): 
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                else:
                    end = True 

        
        else:

            if not dying_sound:
                dying_fx.play()
                dying_sound = True
        
            if not pygame.mixer.music.get_busy():
                end_music.play()
                
            screen_scroll = 0 
            if restart_button.draw(screen):
                bg_scroll = 0 
                world_data = reset_level()
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row): 
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)
                # Restart the dying sound
                dying_sound = False



    # We add an event handler that checks when we exit the game
    for event in pygame.event.get():
        #quiting the game if the x on the screen is pressed
        if event.type == pygame.QUIT:
            run = False 

        # event for key pressed down. For ket a, d and escape 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True 
            if event.key == pygame.K_d:
                moving_right = True 
            if event.key == pygame.K_p:
                shoot = True 
            if event.key == pygame.K_w and player.alive:
                player.jump = True 
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False 
            if event.key == pygame.K_r:
                rocket = True 
            if event.key == pygame.K_q:
                grenade = True 

        # event for key released. For ket a, d and escape 
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False 
            if event.key == pygame.K_d:
                moving_right = False 
            if event.key == pygame.K_p:
                shoot = False  
            if event.key == pygame.K_r:
                rocket = False 
            if event.key == pygame.K_q:
                grenade = False 
                grenade_thrown = False 

    # We need to update our display and game 
    pygame.display.update()

#just to make sure
pygame.quit()
