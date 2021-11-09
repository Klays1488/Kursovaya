import pygame
import random
from os import path
import time, threading

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')


WIDTH = 720
HEIGHT = 1280
FPS = 60
POWERUP_TIME = 5000

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Создаем игру и окно
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Игрушка!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

#Полоска здоровья
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 300
    BAR_HEIGHT = 50
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, BLUE, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = (x-120) + 70 * i
        img_rect.y = y
        surf.blit(img, img_rect)


#начальное окно
def show_go_screen():
    screen.blit(background, background_rect)
    #Кнопка старт
    button_img = pygame.image.load(path.join(img_dir, "START.png")).convert()
    button_img.set_colorkey((0,0,0))
    Rect = button_img.get_rect(bottomright=(605, 450))
    screen.blit (button_img, Rect)
    
    #Кнопка выход
    button2_img = pygame.image.load(path.join(img_dir, "EXIT.png")).convert()
    button2_img.set_colorkey((0,0,0))
    Rect2 = button2_img.get_rect(bottomright=(605, 650))
    screen.blit (button2_img, Rect2)

    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # получаем позицию мышки
                if Rect.collidepoint(mouse_pos):
                    waiting = False                    
                if Rect2.collidepoint(mouse_pos):
                    pygame.quit()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (90, 68))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    

    def update(self):
        # тайм-аут для бонусов
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # показать, если скрыто
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        self.speedy = 0
   

        keystate = pygame.key.get_pressed()
        
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8
        if keystate[pygame.K_w]:
            self.speedy = -8
        if keystate[pygame.K_s]:
            self.speedy = 8
        if keystate[pygame.K_a]:
            self.speedx = -8
        if keystate[pygame.K_d]:
            self.speedx = 8
        if keystate[pygame.K_ESCAPE]:
            pygame.quit
        if not keystate[pygame.K_SPACE]:
            self.shoot()
                   

        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        self.rect.y += self.speedy
        if self.rect.bottom  > HEIGHT :
            self.rect.bottom  = HEIGHT 
        if self.rect.top  < 0:
            self.rect.top  = 0
        #Координаты мышки на экране
        z,s = pygame.mouse.get_pos()
        #подстановка координа для сторон
        self.rect.left = z
        self.rect.right = z
        self.rect.top = s
        self.rect.bottom = s
        

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                fire = Fire(self.rect.centerx, self.rect.top)
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                all_sprites.add(fire)
                bullets.add(bullet)
                fires.add(fire)
                shoot_sound.play()
            if self.power == 2:
                fire = Fire(self.rect.left, self.rect.centery)
                fire1 = Fire(self.rect.right, self.rect.centery)
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(fire)
                all_sprites.add(fire1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                fires.add(fire)
                fires.add(fire1)
                shoot_sound.play()
            if self.power >= 3:
                fire = Fire(self.rect.left, self.rect.centery)
                fire1 = Fire(self.rect.right, self.rect.centery)
                bullet = Bullet(self.rect.centerx, self.rect.top)
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(fire)
                all_sprites.add(fire1)
                bullets.add(bullet)
                bullets.add(bullet1)
                bullets.add(bullet2)
                fires.add(fire)
                fires.add(fire1)
                shoot_sound.play()

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
    # вращение спрайтов
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -60)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        #self.image1 = efect_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        #self.rect = self.image1.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
        
    def update(self):
        self.rect.y += self.speedy
        # убить, если он сдвинется с нижней части экрана
        if self.rect.bottom < 0:
            self.kill()

class Fire(pygame.sprite.Sprite):
    def __init__(self, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = efect_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x

    def update(self):
        self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun', 'boom'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
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
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

# Загрузка всей игровой графики
background = pygame.image.load(path.join(img_dir, "fon.jpg")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip1_blue.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (65, 39))
player_mini_img.set_colorkey(BLACK)
pause_img = pygame.image.load(path.join(img_dir, "pause.png")).convert()
pause_img.set_colorkey(BLACK)
pause_img_rect = pause_img.get_rect(bottomright=(605, 110))

bullet_img = pygame.image.load(path.join(img_dir, "laserRed07.png")).convert()
efect_img = pygame.image.load(path.join(img_dir, "fire17.png")).convert()
meteor_images = []
#случайные размеры астероидов
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorGrey_med1.png',
               'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',
               'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())
#анимированный взрыв
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (155, 155))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (232, 52))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_bronze.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_bronze.png')).convert()
booms = pygame.image.load(path.join(img_dir, 'boom.png')).convert()
booms.set_colorkey(WHITE)
powerup_images['boom'] = booms


#Загрузка мелодий игры
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'flip.mp3'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'flip.mp3'))
boom_sound = pygame.mixer.Sound(path.join(snd_dir, 'flip.mp3'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
    pygame.mixer.music.load(path.join(snd_dir, 'music.mp3'))
pygame.mixer.music.set_volume(0.4)
score = 0
pygame.mixer.music.play(loops=-1)
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
fires = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(20):
    newmob()
score = 0

# Цикл игры
game_over = True
running = True
level = 0
levelup =0
while running: 
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(35):
            newmob()
        score = 0
        # усложнение игры (увеличение скорости метеорита)
        level = 0
        levelup = 0
        FPS = 60
    if score >= level:
        level = level + random.randint(1000,3000)
        FPS = FPS+1
        levelup = levelup+1
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
           mouse_pos = event.pos  # получаем позицию мышки
           if pause_img_rect.collidepoint(mouse_pos):
              running = False
               
    
       
            
    # Обновление
    all_sprites.update()

    # проверка, попала ли пуля в моб(метеорит)
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    # Проверка, не ударил ли моб(метеорит) игрока
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    # Проверка столкновений игрока и улучшения
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield': # щит
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun': # улчшение оружия
            player.powerup()
            power_sound.play()
        if hit.type == 'boom': # уничтожение всех Mob на экране
            score = score + random.randrange(1000, 5000)
            for sprite in mobs:
             if isinstance(sprite, Mob):
              random.choice(expl_sounds).play()
              expl = Explosion(sprite.rect.center, 'lg')
              all_sprites.add(expl)
              sprite.kill()
            for i in range(35): # после уничтожения всех Mob, необходимо возобновить их генерацию
                newmob()      
     
    #Если игрок умер, игра окончена
    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    screen.blit(pause_img,pause_img_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 28, WIDTH / 2, 10)
    draw_text(screen, str(levelup), 18, WIDTH / 4, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives,
               player_mini_img)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()


pygame.quit()
