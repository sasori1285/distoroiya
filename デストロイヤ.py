from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
from multiprocessing.connection import wait
from operator import truediv
from os import kill
from re import T
from turtle import width
from xmlrpc.client import TRANSPORT_ERROR
import pygame
from pygame import image
from pygame import transform
from pygame.constants import K_UP
import random
import os

FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255,0,0)
WIDTH = 500
HEIGHT = 600

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("デストロイヤbeta")
clock = pygame.time.Clock()

#image
player_img = pygame.image.load(os.path.join('kimage/1.PNG')).convert()
player2_img = pygame.image.load(os.path.join("kimage/2.PNG")).convert()
bullet_img = pygame.image.load(os.path.join("kimage/3.png")).convert()
rock_imgs = []
for i in range(4):
    rock_imgs.append(pygame.image.load(os.path.join(f"kimage/a{i}.png")).convert())
expl_anim = {}
expl_anim['sm'] = []
expl_anim['pl'] = []
for i in range (3):
    expl_img = (pygame.image.load(os.path.join(f"kimage/exp{i}.PNG")).convert())
    expl_img.set_colorkey(BLACK)
    expl_anim["sm"].append(pygame.transform.scale(expl_img, (30, 30)))
    expl_anim["pl"].append(pygame.transform.scale(expl_img, (50, 50)))
power_img = pygame.image.load(os.path.join("kimage/pow.PNG")).convert()
mnpower_img = pygame.transform.scale(power_img, (25, 19))
mnpower_img.set_colorkey(WHITE)
pygame.display.set_icon(mnpower_img)

#ingamesound
shoot_sound = pygame.mixer.Sound(os.path.join("sound/shoot.wav"))
pwshoot_sound = pygame.mixer.Sound(os.path.join("sound/Music by JuliusH from Pixabay.mp3"))
die_sound = pygame.mixer.Sound(os.path.join("sound/rumble.ogg"))
expl_sounds = [   
    pygame.mixer.Sound(os.path.join("sound/expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound/expl1.wav"))
]
ROLL = pygame.mixer.Sound(os.path.join("kimage/RRoll.mp3"))

#text
font_name = os.path.join("REDENSEK.TTF")
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)
def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, WHITE, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_init():
    screen.fill(BLACK)
    draw_text(screen,'PRESS ANY BOTTON', 22, WIDTH/2, 400)
    draw_text(screen,'player1 move [AWSD] shoot [SPACE]', 22, WIDTH/2, 150)
    draw_text(screen,'player2 move [ARROW KEY] shoot [R_CTRL]', 22, WIDTH/2, 200)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False

#player one
class Player (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (40, 33))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 15
        #hitbox test
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = 220
        self.rect.bottom = HEIGHT - 10 
        self.speedx = 8
        self.health = 100
        self.gun = 1
        self.gun_time = 0
        self.hidden = False

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 3000:
            self.gun -= 1
            self.gun_time = now

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx
        if key_pressed[pygame.K_w]:
            self.rect.y -= self.speedx
        if key_pressed[pygame.K_s]:
            self.rect.y += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        if not (self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)  
                bullets.add(bullet)     
                shoot_sound.play()
            elif self.gun >= 2:
                bullet12 = Powbullet(self.rect.right, self.rect.centery)
                bullet22 = Powbullet(self.rect.left, self.rect.centery)
                all_sprites.add(bullet12)
                all_sprites.add(bullet22)
                bullets12.add(bullet12)  
                bullets12.add(bullet22)
                pwshoot_sound.play()

    def hide(self):
        self.hidden = True
        self.rect.center = (WIDTH/2, HEIGHT+500)
    
    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

#player two
class Player2 (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player2_img, (40, 33))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 15
        #hitbox test
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = 280
        self.rect.bottom = HEIGHT - 10 
        self.speedx = 8
        self.health = 100
        self.gun = 1
        self.gun_time = 0
        self.hidden = False

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 3000:
            self.gun -= 1
            self.gun_time = now

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        if key_pressed[pygame.K_UP]:
            self.rect.y -= self.speedx
        if key_pressed[pygame.K_DOWN]:
            self.rect.y += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        if not (self.hidden):
            if self.gun == 1:
                bullet2 = Bullet2(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet2)
                bullets2.add(bullet2)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet22 = Powbullet2(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet22)
                bullets22.add(bullet22)  
                pwshoot_sound.play()         

    def hide(self):
        self.hidden = True
        self.rect.center = (WIDTH/2, HEIGHT+500)


    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()
#hostile
class Rock (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(random.choice(rock_imgs), (20, 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 10
        #hitbox test
        #pygame.draw.circle(random.choice(rock_imgs), RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 15)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 15)
            self.speedx = random.randrange(-3, 5)

#lazer
class Bullet (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (5, 15))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 1
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

#lazer2
class Bullet2 (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (5, 15))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 1
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
#pow lazer
class Powbullet (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (10, 610))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 1
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -50

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

#pow lazer2
class Powbullet2 (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (40, 610))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 1
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -50

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

#explotion
class Explotion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else: 
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

#pow
class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(power_img, (15, 15))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 1
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

show_init = True
running = True
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        bullets2 = pygame.sprite.Group()
        bullets12 = pygame.sprite.Group()
        bullets22 = pygame.sprite.Group()
        powers = pygame.sprite.Group() 
        player = Player()
        player2 = Player2()
        all_sprites.add(player)
        all_sprites.add(player2)
        for i in range(8):
            new_rock()
        score = 0
        score2 = 0

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
            if event.key == pygame.K_RCTRL:
                player2.shoot()    

#game update
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explotion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()
    hits2 = pygame.sprite.groupcollide(rocks, bullets2, True, True)
    for hit in hits2:
        random.choice(expl_sounds).play()
        score2 += hit.radius
        expl = Explotion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()
    hits12 = pygame.sprite.groupcollide(rocks, bullets12, True, False)
    for hit in hits12:
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explotion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        new_rock()
    hits22 = pygame.sprite.groupcollide(rocks, bullets22, True, False)
    for hit in hits22:
        random.choice(expl_sounds).play()
        score2 += hit.radius
        expl = Explotion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        new_rock()
    #gun update
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        player.gunup()
    hits2 = pygame.sprite.spritecollide(player2, powers, True)
    for hit in hits2:
        player2.gunup()


    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    hits2 = pygame.sprite.spritecollide(player2, rocks, True, pygame.sprite.collide_circle)
    
    for hit in hits:
        new_rock()
        player.health -= 40
        expl = Explotion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            die = Explotion(player.rect.center, 'pl')
            all_sprites.add(die)
            die_sound.play()
            player.hide()
            player.kill()
            
    for hit in hits2:
        new_rock()
        player2.health -= 40
        expl = Explotion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player2.health <= 0:
            die = Explotion(player2.rect.center, 'pl')
            all_sprites.add(die)
            die_sound.play()
            player2.hide()
            player2.kill()

    if player.hidden == True and player2.hidden == True and not(die.alive()):
        show_init = True  
        '''
        ROLL.play()
        cap = cv2.VideoCapture("kimage/Rroll001.ogv")
        while(cap.isOpened()):
            ret, frame = cap.read()
            frame = cv2.resize(frame, (500, 500))
            cv2.imshow("YOU DIED press q to quit", frame)
         # rr 500, 500 38fps, long press q to quit
            if cv2.waitKey(38) & 0Xff == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()
        running = False 
        ''' 
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 25, 200, 5)
    draw_text(screen, str(score2), 25, 300, 5)
    draw_health(screen, player.health, 5, 15)
    draw_health(screen, player2.health, 390, 15)
    pygame.display.update()  

pygame.quit()
