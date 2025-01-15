import pygame
from sys import exit

class Character(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.walking_right_frames = [
            pygame.transform.scale(pygame.image.load("graphics/player/wizard.png").convert_alpha(), (70, 80)),
            pygame.transform.scale(pygame.image.load("graphics/player/wizard_walking0.png").convert_alpha(), (70, 80)),
            pygame.transform.scale(pygame.image.load("graphics/player/wizard_walking1.png").convert_alpha(), (70, 80)),
            pygame.transform.scale(pygame.image.load("graphics/player/wizard_walking2.png").convert_alpha(), (70, 80))
        ]
        self.jumping_frame = pygame.transform.scale(pygame.image.load("graphics/player/wizard_jumping.png").convert_alpha(), (70, 80))
        self.shooting = pygame.transform.scale(pygame.image.load("graphics/player/wizard_shooting.png").convert_alpha(), (130, 80))
        
        # Initial image
        self.x = 50
        self.y = 315
        self.image = self.walking_right_frames[0]
        self.rect = self.image.get_rect(midbottom = (self.x, self.y))
        self.facing_right = True
        self.character_gravity = 0
        self.frame_index = 0
        self.animation_speed = 0.18  # Speed of animation
        self.is_jumping = False
        self.is_walking = False
        self.is_shooting = False
        self.shooting_duration = 15
        self.shooting_timer = 0
        self.speed = 4

    def walking(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.rect.right += self.speed
            self.is_walking = True
            self.facing_right = True  # Mark facing direction
        elif keys[pygame.K_LEFT]:
            self.rect.left -= self.speed
            self.is_walking = True
            self.facing_right = False  # Mark facing direction
        else:
            self.is_walking = False  # Character is not walking if no key is pressed 

    def animate(self):
        if self.is_jumping and not self.is_shooting:
            # Show jumping frame if the character is in the air
            if self.facing_right:
                self.image = self.jumping_frame
            else:
                self.image = pygame.transform.flip(self.jumping_frame, True, False)
        elif self.is_walking and not self.is_shooting:
            # Update frame index and animate walking
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.walking_right_frames):
                self.frame_index = 0

            current_frame = self.walking_right_frames[int(self.frame_index)]
            if self.facing_right:
                self.image = current_frame
            else:
                self.image = pygame.transform.flip(current_frame, True, False)
        elif self.is_shooting:
            if self.facing_right:
                self.image = self.shooting
            else:
                self.image = pygame.transform.flip(self.shooting, True, False)
        else:
            # Reset to idle frame when not moving
            if self.facing_right:
                self.image = self.walking_right_frames[0]
            else:
                self.image = pygame.transform.flip(self.walking_right_frames[0], True, False)

    def shoot(self):
        if self.is_shooting:
                self.shooting_timer += 1
                if self.shooting_timer >= self.shooting_duration:
                    self.is_shooting = False
                    self.shooting_timer = 0

    def gravity(self):
        self.character_gravity += 1
        self.rect.bottom += self.character_gravity
        if self.rect.bottom >= 315:
            self.rect.bottom = 315
            self.is_jumping = False
        else:
            self.is_jumping = True

    def jump(self):
        if self.rect.bottom == 315:
            self.character_gravity = -20

    def loop_player(self):
        if self.rect.left > 800 : 
            self.rect.right = 0
        elif self.rect.right < 0 :
            self.rect.left = 800
    
    def update(self):
        self.walking()
        self.animate()
        self.gravity()
        self.loop_player()
        self.shoot()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos,  facing_right):
        super().__init__()
        self.image = pygame.image.load("graphics/fire.png")
        self.image = pygame.transform.scale(self.image, (60, 30))
        self.rect = self.image.get_rect(midtop = pos)
        self.speed = 8 if facing_right else -8

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > 800:
            self.kill()

class Vampire(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = [
            pygame.transform.scale(pygame.image.load("graphics/enemy/enemy_pos1.png").convert_alpha(), (120, 150)),
            pygame.transform.scale(pygame.image.load("graphics/enemy/enemy_pos1.png").convert_alpha(), (120, 150)),
            pygame.transform.scale(pygame.image.load("graphics/enemy/enemy_pos1.png").convert_alpha(), (120, 150)),
            pygame.transform.scale(pygame.image.load("graphics/enemy/enemy_pos1.png").convert_alpha(), (120, 150)),
            pygame.transform.scale(pygame.image.load("graphics/enemy/enemy_pos2.png").convert_alpha(), (140, 160)),
            pygame.transform.scale(pygame.image.load("graphics/enemy/enemy_pos3.png").convert_alpha(), (140, 160))
        ]
        self.image = self.frames[0]  # Set the initial frame to the first image
        self.rect = self.image.get_rect(midbottom = (700, 310))
        self.health = 10
        self.frame_index = 0
        self.animation_speed = 0.1

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        
    def update(self):
        self.animate()

#function to check coin collision and add score to scoreboard
def collect_coins(character, coins):
    global score
    for coin_rect in coins[:]:  
        if character.sprite.rect.colliderect(coin_rect): #check collision
            coins.remove(coin_rect) #remove coin rect
            score += 1
            #coin sound effects
            coin_sound = pygame.mixer.Sound("music/coin_collected.mp3")
            coin_sound.play(loops=0)
            coin_sound.set_volume(0.2)

#function to kill vampire
def kill_vampire():
    collisions = pygame.sprite.groupcollide(bullets, enemy, True, False)  # Destroy the bullet but keep the vampire
    for vampire in collisions.values():  # Iterate through each vampire hit
        for vamp in vampire: 
            vamp.take_damage()

#pygame window initialization / dimensions / fps / etc.
pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption("Vampire")
clock = pygame.time.Clock()

#music
pygame.mixer.init()
pygame.mixer.music.load("music/background.mp3")
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.2)

#Title
font = pygame.font.Font("fonts/Bloodthirsty-3j0p.ttf", 60)
text_surface = font.render("Vampire", True, "white")
text_rect = text_surface.get_rect(center=(400, 50))

#sky surface
background_surface = pygame.image.load("graphics/background.jpg").convert()
background_surface = pygame.transform.scale(background_surface, (800,370))

#ground surface
ground_surface = pygame.image.load("graphics/ground.png").convert_alpha()
ground_surface = pygame.transform.scale(ground_surface, (800,100))

#character surface and rectangle
character = pygame.sprite.GroupSingle()
character.add(Character())

enemy = pygame.sprite.Group()
enemy.add(Vampire())

#coin surface and rectangles list
coin = pygame.image.load("graphics/coin.png").convert_alpha()
coin = pygame.transform.scale(coin, (25, 45))
coins = [coin.get_rect(center=(300,280)), coin.get_rect(center=(500, 280)),]
score = 0

bullets = pygame.sprite.Group()

#MAIN GAME LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                character.sprite.jump()
            if event.key == pygame.K_c:  # Shoot bullet when 'c' is pressed
                bullet_pos = character.sprite.rect.midright if character.sprite.facing_right else character.sprite.rect.midleft
                bullets.add(Bullet(bullet_pos, character.sprite.facing_right))
                character.sprite.is_shooting = True

    screen.blit(background_surface, (0,-10))
    screen.blit(ground_surface, (0,300))
    screen.blit(text_surface, text_rect)

    collect_coins(character, coins)
    for coin_rect in coins:            #blit each coin on the screen
        screen.blit(coin, coin_rect)

    bullets.update()  # Update bullet positions
    bullets.draw(screen)

    character.draw(screen)
    character.update()
     
    enemy.draw(screen)
    enemy.update()

    kill_vampire()

    font2 = pygame.font.Font("fonts/CfMidnightRegular-MJ8B.ttf", 30)
    score_surface = font2.render("Crystals: " + str(score), True, "white")
    score_rect = score_surface.get_rect(midleft = (10,30))
    screen.blit(score_surface, score_rect)

    pygame.display.update()
    clock.tick(60)