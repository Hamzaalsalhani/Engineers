

import os
import random
# import math
import pygame

# To Auto import from the files, so no need to call the file every time
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Jump Saga")

WIDTH, HEIGHT = 1300, 650
FPS = 60

# THE PLAYERS SPEED 
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

#Indicate the direction to flip in
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

#Sprites make it easy to do pixel perfect collision
def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(272, 64, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def get_blocke(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(273, 129, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)



def get_blockee(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(320, 65, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)



class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Main Characters", "Emilia" , 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0 #Tracks the number of times character is hit

        #load Sounds
        self.jump_sound = pygame.mixer.Sound("assets/audio/attack.wav")
        self.hit_sound = pygame.mixer.Sound("assets/audio/damage.wav")
        pygame.mixer.music.load("assets/audio/starlight_city.mp3")


    def start_background_music(self):
        pygame.mixer.music.set_volume(0.5) #Adjust volume sound
        pygame.mixer.music.play(-1) #loop forever

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        self.jump_sound.play()
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_sound.play()

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

#Move the character
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)



class Blocke(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_blocke(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)



class Blockee(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_blockee(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)




class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Saw(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "saw")
        self.saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.image = self.saw["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Off"

    def on(self):
        self.animation_name = "On (38x38)"

    def Off(self):
        self.animation_name = "Off"

    def loop(self):
        sprites = self.saw[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fly(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fly")
        self.fly = load_sprite_sheets("Traps", "Falling Platforms", width, height)
        self.image = self.fly["Off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Off"

    def on(self):
        self.animation_name = "On (32x10)"

    def Off(self):
        self.animation_name = "Off"

    def loop(self):
        sprites = self.fly[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0



class End(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "end")
        self.end = load_sprite_sheets("Items", "End", width, height)
          # Assume the sprite sheet is named "Flying"
        self.sprites = self.end["end"]
          # Assuming "Flying" is the key in the loaded sprite sheet
        self.image = self.sprites[0]
          # Start with the first frame
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def loop(self):
        sprite_index = (self.animation_count //
                         self.ANIMATION_DELAY) % len(self.sprites)
        self.image = self.sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(self.sprites):
            self.animation_count = 0



#To call the backgrounds and to fill the background it self

blue_background = pygame.image.load("assets/Background/Brown.png")

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


#This function is about drawing in the platform
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def reset_game():
    main(window)  # Restart the game by calling the main function again.

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    # Track the different traps
    if not hasattr(player, "traps_hit"):
        player.traps_hit = set()

    for obj in to_check:
        if obj and obj.name in {"fire", "saw"}:  #Trap types
            if obj not in player.traps_hit:  # Avoid counting the same trap multiple times
                player.traps_hit.add(obj)
                player.make_hit()

            if len(player.traps_hit) >= 3:
                display_message(
                    window,
                    "Game Over! Restarting...",
                    font_size=60,
                    duration=2000,
                    color=(0, 0, 0),
                )
                reset_game()

def display_message(window, text, font_size, duration, color=(255, 255, 255), bg_color=None):
    # Create the font object
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    
    # Center the text on the screen
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Draw the text on the screen
    window.blit(text_surface, text_rect)
    pygame.display.update()
    
    # Wait for the specified duration
    pygame.time.delay(duration)


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96


    player = Player(100, 100, 50, 50)

    #Start the background Music
    player.start_background_music()


    saws = [
    Saw(5.9*100 , HEIGHT - block_size  - 90*2, 38, 38)
    ,Saw(9.77*100 , HEIGHT - block_size  - 90*3, 38, 38)
    ,Saw(11.57*100 , HEIGHT - block_size  - 90*3, 38, 38)
    ,Saw(6.8*100  , HEIGHT - block_size  - 90*2, 38, 38)
    ,Saw(19.3*100  , HEIGHT - block_size  - 80, 38, 38)
    ,Saw(20.3*100  , HEIGHT - block_size  - 80, 38, 38)
    ,Saw(21.3*100  , HEIGHT - block_size - 80, 38, 38)
    ,Saw(26.9*100  , HEIGHT - block_size- 120 - 64, 38, 38)
    ,Saw(30.9*100  , HEIGHT - block_size - 95*2, 38, 38)
    ,Saw(33.8*100  , HEIGHT - block_size - 80, 38, 38)
    ,Saw(41.5*100  , HEIGHT - block_size - 95*3, 38, 38)
    ,Saw(42.5*100  , HEIGHT - block_size - 95*3, 38, 38)
    ,Saw(42.5*100  , HEIGHT - block_size - 95*2, 38, 38)
    ,Saw(44.7*100  , HEIGHT - block_size - 85*4, 38, 38)
    ,Saw(47.5*100  , HEIGHT - block_size - 95*6, 38, 38)
    ,Saw(50.6*100  , HEIGHT - block_size - 85*4, 38, 38)
    ,Saw(52.8*100  , HEIGHT - block_size - 95*2, 38, 38)
    ,Saw(52.8*100  , HEIGHT - block_size - 95*3, 38, 38)
    ,Saw(53.8*100  , HEIGHT - block_size - 95*3, 38, 38)
    ,Saw(56.8*100  , HEIGHT - block_size - 90*2, 38, 38)
    ,Saw(57.5*100  , HEIGHT - block_size - 90*1, 38, 38)
    ,Saw(20.3*100  , HEIGHT - block_size - 95*5, 38, 38)
    ,Saw(19.3*100  , HEIGHT - block_size - 95*4, 38, 38)
    ,Saw(21.3*100  , HEIGHT - block_size - 95*4, 38, 38)]
    for saw in saws:
        saw.on()

    fires = [Fire(400  , HEIGHT - block_size  - 64, 16, 32) 
            , Fire(600 , HEIGHT - block_size - 96*3 - 64, 16, 32)
            ,Fire(14.7*100, HEIGHT - block_size- 96*3  - 64, 16, 32)
            , Fire(24.3*100, HEIGHT - block_size - 64, 16, 32)
            ,Fire(28.2*100, HEIGHT - block_size - 96*3 - 64, 16, 32)
            ,Fire(32*100, HEIGHT - block_size - 96*3 - 64, 16, 32)
            ,Fire(35.7*100, HEIGHT - block_size - 96*3 - 64, 16, 32)
            ,Fire(50.7*100, HEIGHT - block_size - 96*4 - 64, 16, 32)
            ,Fire(45*100, HEIGHT - block_size - 96*4 - 64, 16, 32)
            ,Fire(48.7*100, HEIGHT - block_size  - 64, 16, 32)
            ,Fire(46.8*100, HEIGHT - block_size  - 64, 16, 32)
            ,Fire(54*100, HEIGHT - block_size  - 64, 16, 32)
            ,Fire(57*100, HEIGHT - block_size  - 64, 16, 32)
            ,Fire(41.7*100, HEIGHT - block_size  - 64, 16, 32)]
    for fire in fires:
        fire.on()


     
    flys= [Fly(43.9*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(44.6*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(45.3*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(46*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(44.4*100  , HEIGHT - block_size  - 64*2, 32, 10)
    ,Fly(45.1*100  , HEIGHT - block_size  - 64*2, 32, 10)
    ,Fly(47.2*100  , HEIGHT - block_size  - 64, 32, 10)
    ,Fly(48*100  , HEIGHT - block_size  - 64, 32, 10)
    ,Fly(50.8*100  , HEIGHT - block_size  - 64*2, 32, 10)
    ,Fly(50.1*100  , HEIGHT - block_size  - 64*2, 32, 10)
    ,Fly(49.5*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(50.2*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(50.9*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(51.7*100  , HEIGHT - block_size  - 64*6, 32, 10)
    ,Fly(47.2*100  , HEIGHT - block_size  - 64*4, 32, 10)
    ,Fly(48*100  , HEIGHT - block_size  - 64*4, 32, 10)]
    for fly in flys:
        fly.on()

    ends = [End(100*68.9 , HEIGHT - block_size  - 105*3, 64, 64)]





    bloke = [Blocke(block_size * 67, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 67, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 68, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 69, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 70, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 71, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 72, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 73, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 74, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 75, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 76, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 77, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 78, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 79, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 80, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 81, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 81, HEIGHT - block_size*2 , block_size)
    ,Blocke(block_size * 82, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 82, HEIGHT - block_size*2 , block_size)
    ,Blocke(block_size * 82, HEIGHT - block_size*3 , block_size)
    ,Blocke(block_size * 83, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 83, HEIGHT - block_size*2 , block_size)
    ,Blocke(block_size * 83, HEIGHT - block_size*3 , block_size)
    ,Blocke(block_size * 83, HEIGHT - block_size*4 , block_size)
    ,Blocke(block_size * 84, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 84, HEIGHT - block_size*2 , block_size)
    ,Blocke(block_size * 84, HEIGHT - block_size*3 , block_size)
    ,Blocke(block_size * 84, HEIGHT - block_size*4 , block_size)
    ,Blocke(block_size * 84, HEIGHT - block_size*5 , block_size)
    ,Blocke(block_size * 85, HEIGHT - block_size , block_size)
    ,Blocke(block_size * 85, HEIGHT - block_size*2 , block_size)
    ,Blocke(block_size * 85, HEIGHT - block_size*3 , block_size)
    ,Blocke(block_size * 85, HEIGHT - block_size*4 , block_size)
    ,Blocke(block_size * 85, HEIGHT - block_size*5 , block_size)
    ,Blocke(block_size * 85, HEIGHT - block_size*6 , block_size)
    ,Blocke(block_size * 85, HEIGHT - block_size*7 , block_size)
    ,Blocke(block_size * 72, HEIGHT - block_size*2 , block_size)
    ,Blocke(block_size * 72, HEIGHT - block_size*3 , block_size)
    ,Blocke(block_size * 73, HEIGHT - block_size*3 , block_size)
    ,Blocke(block_size * 71, HEIGHT - block_size*3 , block_size)
    ,Blocke(block_size * 70, HEIGHT - block_size*2 , block_size)
    ,Blocke(block_size * 74, HEIGHT - block_size*2 , block_size)]



    blokee = [Blockee(block_size * 74.5, HEIGHT - block_size*6.5 , block_size)
    ,Blockee(block_size * 75, HEIGHT - block_size*6 , block_size)
    ,Blockee(block_size * 76, HEIGHT - block_size*6 , block_size)
    ,Blockee(block_size * 75.5, HEIGHT - block_size*5.5 , block_size)
    ,Blockee(block_size * 75.5, HEIGHT - block_size*5 , block_size)
    ,Blockee(block_size * 76.5, HEIGHT - block_size*6.5 , block_size)
    ,Blockee(block_size * 78, HEIGHT - block_size*6.5 , block_size)
    ,Blockee(block_size * 78.5, HEIGHT - block_size*6.5 , block_size)
    ,Blockee(block_size * 79, HEIGHT - block_size*6 , block_size)
    ,Blockee(block_size * 79, HEIGHT - block_size*5.5 , block_size)
    ,Blockee(block_size * 78.5, HEIGHT - block_size*5 , block_size)
    ,Blockee(block_size * 78, HEIGHT - block_size*5 , block_size)
    ,Blockee(block_size * 77.5, HEIGHT - block_size*6 , block_size)
    ,Blockee(block_size * 77.5, HEIGHT - block_size*5.5 , block_size)
    ,Blockee(block_size * 80, HEIGHT - block_size*6 , block_size)
    ,Blockee(block_size * 80, HEIGHT - block_size*5.5 , block_size)
    ,Blockee(block_size * 80.5, HEIGHT - block_size*5 , block_size)
    ,Blockee(block_size * 81, HEIGHT - block_size*6 , block_size)
    ,Blockee(block_size * 81, HEIGHT - block_size*5.5 , block_size)
    ,Blockee(block_size * 75, HEIGHT - block_size*3.5 , block_size)
    ,Blockee(block_size * 75, HEIGHT - block_size*3 , block_size)
    ,Blockee(block_size * 75.5, HEIGHT - block_size*2.5 , block_size)
    ,Blockee(block_size * 76, HEIGHT - block_size*3.5 , block_size)
    ,Blockee(block_size * 76, HEIGHT - block_size*3 , block_size)
    ,Blockee(block_size * 76.5, HEIGHT - block_size*2.5 , block_size)
    ,Blockee(block_size * 77, HEIGHT - block_size*3 , block_size)
    ,Blockee(block_size * 77, HEIGHT - block_size*3.5 , block_size)
    ,Blockee(block_size * 78, HEIGHT - block_size*2.5 , block_size)
    ,Blockee(block_size * 78, HEIGHT - block_size*3 , block_size)
    ,Blockee(block_size * 78, HEIGHT - block_size*4 , block_size)
    ,Blockee(block_size * 79, HEIGHT - block_size*2.5 , block_size)
    ,Blockee(block_size * 79, HEIGHT - block_size*3 , block_size)
    ,Blockee(block_size * 79, HEIGHT - block_size*3.5 , block_size)
    ,Blockee(block_size * 79.5, HEIGHT - block_size*3 , block_size)
    ,Blockee(block_size * 80, HEIGHT - block_size*3 , block_size)
    ,Blockee(block_size * 80, HEIGHT - block_size*2.5 , block_size)]




    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 5) // block_size)]

    objects = [*floor , *fires , *saws , *flys , *ends ,*bloke , *blokee,Block(0, HEIGHT - block_size *2 , block_size),Block(0, HEIGHT - block_size *3 , block_size),Block(0, HEIGHT - block_size *4 , block_size),Block(0, HEIGHT - block_size *5 , block_size),Block(0, HEIGHT - block_size *6 , block_size),Block(0, HEIGHT - block_size *7 , block_size),
                Block(block_size * 1, HEIGHT - block_size * 4, block_size),Block(block_size * 2, HEIGHT - block_size * 4, block_size),Block(block_size * 2, HEIGHT - block_size * 3, block_size)
                  ,Block(block_size * 7, HEIGHT - block_size * 4, block_size),Block(block_size * 5, HEIGHT - block_size * 4, block_size),Block(block_size * 6, HEIGHT - block_size * 4, block_size),Block(block_size * 9, HEIGHT - block_size * 2, block_size)
                  ,Block(block_size * 11, HEIGHT - block_size * 4, block_size)
                  ,Block(block_size * 14, HEIGHT - block_size * 4, block_size),Block(block_size * 14, HEIGHT - block_size * 3, block_size),Block(block_size * 13, HEIGHT - block_size * 3, block_size),Block(block_size * 15, HEIGHT - block_size * 4, block_size),Block(block_size * 16, HEIGHT - block_size * 4, block_size),Block(block_size * 16, HEIGHT - block_size * 3, block_size),Block(block_size * 16, HEIGHT - block_size * 2, block_size),Block(block_size * 17, HEIGHT - block_size * 3, block_size),Block(block_size * 19, HEIGHT - block_size * 2, block_size)
                  ,Block(block_size * 23, HEIGHT - block_size * 2, block_size),Block(block_size * 25, HEIGHT - block_size * 4, block_size),Block(block_size * 27, HEIGHT - block_size * 6, block_size),Block(block_size * 27, HEIGHT - block_size * 4, block_size),Block(block_size * 27, HEIGHT - block_size * 3, block_size),Block(block_size * 27, HEIGHT - block_size * 2, block_size),Block(block_size * 28, HEIGHT - block_size * 4, block_size),Block(block_size * 29, HEIGHT - block_size * 4, block_size)
                  ,Block(block_size * 30, HEIGHT - block_size * 4, block_size),Block(block_size * 30, HEIGHT - block_size * 2, block_size)
                  ,Block(block_size * 33, HEIGHT - block_size * 4, block_size),Block(block_size * 32, HEIGHT - block_size * 4, block_size),Block(block_size * 33, HEIGHT - block_size * 3, block_size),Block(block_size * 33, HEIGHT - block_size * 2, block_size),Block(block_size * 38, HEIGHT - block_size * 4, block_size),Block(block_size * 39, HEIGHT - block_size * 4, block_size),Block(block_size * 37, HEIGHT - block_size * 3, block_size),Block(block_size * 37, HEIGHT - block_size * 2, block_size),Block(block_size * 37, HEIGHT - block_size * 4, block_size),Block(block_size * 35, HEIGHT - block_size * 3, block_size)
                  ,Block(block_size * 40, HEIGHT - block_size * 2, block_size)
                  ,Block(block_size * 41, HEIGHT - block_size * 2, block_size),Block(block_size * 41, HEIGHT - block_size * 3, block_size),Block(block_size * 41, HEIGHT - block_size * 4, block_size),Block(block_size * 41, HEIGHT - block_size * 5, block_size)
                  ,Block(block_size * 42, HEIGHT - block_size * 2, block_size),Block(block_size * 42, HEIGHT - block_size * 3, block_size),Block(block_size * 42, HEIGHT - block_size * 4, block_size),Block(block_size * 42, HEIGHT - block_size * 4, block_size)



                  ,Block(block_size * 57, HEIGHT - block_size * 3, block_size),Block(block_size * 57, HEIGHT - block_size * 2, block_size),Block(block_size * 57, HEIGHT - block_size * 4, block_size)
                  ,Block(block_size * 58, HEIGHT - block_size * 3, block_size),Block(block_size * 58, HEIGHT - block_size * 2, block_size),Block(block_size * 58, HEIGHT - block_size * 4, block_size),Block(block_size * 58, HEIGHT - block_size * 5, block_size)
                  ,Block(block_size * 61, HEIGHT - block_size * 2, block_size),Block(block_size * 60, HEIGHT - block_size * 3, block_size),Block(block_size * 59, HEIGHT - block_size * 4, block_size)
                  ,Block(block_size * 21, HEIGHT - block_size * 5, block_size)]

    offset_x = 0
    scroll_area_width = 200

# Show the message before the game begins and the duration it appears
    display_message(window, "Welcome to Jump Saga!", 64, 3000, color=(255, 255, 255), bg_color=(0, 0, 0))

    run = True

    #To manage the FPS(Frames per Second) from one device to another 
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        for fire in fires:
            fire.loop()
        
        for saw in saws:
            saw.loop()
        
        for fly in flys:
            fly.loop()

        for end in ends:
            end.loop()


    
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)