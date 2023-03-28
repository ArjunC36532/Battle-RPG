import math

import pygame
import self as self
from pygame.locals import *
import sys
import random

pygame.init()

# Declare Variables
# Declare variables
vec = pygame.math.Vector2
HEIGHT = 350
WIDTH = 700
ACC = 0.5
FRIC = -0.10
FPS = 30
FPS_CLOCK = pygame.time.Clock()
COUNT = 0

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First RPG")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

player_idle_sprite_sheet = pygame.image.load("Blue/Gunner_Blue_Idle.png").convert_alpha()
player_running_sprite_sheet = pygame.image.load('Blue/Gunner_Blue_Run.png').convert_alpha()

CAN_FIRE = True


def Get_Animation_List(sheet, width, height, scale, numFrames):
    frames = []
    frame = 0
    while frame < numFrames:
        image = pygame.Surface((width, height))

        image.blit(sheet, (0, 0), ((frame * width), 0, (width * (frame + 1)), height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(BLACK)
        frames.append(image)
        frame += 1

    return frames


player_idle_animation = Get_Animation_List(player_idle_sprite_sheet, 48, 48, 3, 5)
player_running_animation = Get_Animation_List(player_running_sprite_sheet, 48, 48, 3, 6)


class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bgImage = pygame.image.load("Background.png")
        self.bgX = 0
        self.bgY = 0

    def render(self):
        WINDOW.blit(self.bgImage, (self.bgX, self.bgY))


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Ground.png")
        self.rect = self.image.get_rect(center=(350, 350))

    def render(self):
        WINDOW.blit(self.image, (self.rect.x, self.rect.y))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.running = False
        self.idle_animation_frame = 0
        self.run_animation_frame = 0

        self.image = player_idle_animation[0]
        self.rect = self.image.get_rect()

        self.vx = 0
        self.pos = vec(100, 0)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"
        self.jumping = False

        # combat
        self.attacking = False
        self.attack_frame = 0

    def render(self):
        WINDOW.blit(self.image, self.rect)

    def move(self):
        # simulate gravity by keeping a constant acceleration of 0.5 in the downwards direction
        self.acc = vec(0, 1)

        # Determine whether player is running or not
        if abs(self.vel.x) > 1:
            self.running = True
        else:
            self.running = False

        pressed_keys = pygame.key.get_pressed()

        # Accelerate player in direction of key press
        if pressed_keys[K_a]:
            self.acc.x = -ACC
        if pressed_keys[K_d]:
            self.acc.x = ACC

        # Calculate position
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Keep player within the bounds of the screen
        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        if self.pos.x < 0:
            self.pos.x = 0

        # Update rect w new position
        self.rect.midbottom = self.pos

    def update(self):
        if self.idle_animation_frame > 4:
            self.idle_animation_frame = 0
        if self.run_animation_frame > 5:
            self.run_animation_frame = 0

        # move to next frame of idle sequence if conditions met
        if self.jumping == False and self.running == False:
            self.image = player_idle_animation[self.idle_animation_frame]
            self.idle_animation_frame += 1

        # move to next frame of running sequence if conditions met
        if self.jumping == False and self.running == True:
            self.image = player_running_animation[self.run_animation_frame]
            self.run_animation_frame += 1

        self.rect = self.image.get_rect()

        # check for collision between player bullet and enemy
        for bullet in bullets:
            if pygame.Rect.colliderect(bullet.rect, enemy.rect):
                enemyHealthBar.health -= 1

    def gravity_check(self):
        hits = pygame.sprite.spritecollide(player, ground_group, False)
        if self.vel.y > 0:
            if hits:
                lowest = hits[0]
                self.pos.y = 330
                self.vel.y = 0
                self.jumping = False

    def jump(self):
        self.rect.x += 1

        # Check if player is in contact with the ground
        hits = pygame.sprite.spritecollide(self, ground_group, False)

        self.rect.x -= 1

        # if touching the ground and not jumping, player can run
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -20


class EnemyHealthBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = vec(enemy.rect.x - 30, enemy.rect.y - 150)
        self.color = GREEN
        self.health = 60
        self.alive = True

    def update(self):
        print(self.health)
        self.rect = vec(enemy.rect.x + 5, enemy.rect.y - 20)
        # update color
        if 40 < self.health < 60:
            self.color = GREEN
        if 20 < self.health < 40:
            self.color = YELLOW
        if self.health < 20:
            self.color = RED

        if self.health <= 0:
            self.alive = False

    def render(self):
        pygame.draw.rect(WINDOW, BLACK, pygame.Rect(self.rect.x, self.rect.y, 60, 10), width=3)
        pygame.draw.rect(WINDOW, self.color, pygame.Rect(self.rect.x, self.rect.y, self.health, 10))


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect((player.rect.x + 70, player.rect.y + 65, 30, 5))

    def move(self):
        self.rect.x += 20

    def update(self):
        if self.rect.x > WINDOW.get_width():
            self.kill()

    def render(self):
        pygame.draw.rect(WINDOW, RED, self.rect)


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect(enemy.rect.x, enemy.rect.y + 30, 30, 5)

    def move(self):
        self.rect.x -= 20

    def update(self):
        if self.rect.x < 0:
            self.kill()

    def render(self):
        pygame.draw.rect(WINDOW, BLUE, self.rect)


def BulletManager():
    for bullet in bullets:
        if bullet.rect.x > WINDOW.get_width():
            index = bullets.index(bullet)
            bullets.pop(index)
    if len(bullets) > 3:
        CAN_FIRE = False
    else:
        CAN_FIRE = True

    return CAN_FIRE


def EnemyBulletManager():
    for bullet in enemyBullets:
        if bullet.rect.x < 0:
            index = enemyBullets.index(bullet)
            enemyBullets.pop(index)
    if len(enemyBullets) > 1:
        enemy.CAN_FIRE = False
    else:
        enemy.CAN_FIRE = True


class PlayerHealthBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = vec(player.pos.x - 30, player.pos.y - 150)
        self.color = GREEN
        self.health = 60
        self.alive = True

    def update(self):
        print(self.health)
        self.pos = vec(player.pos.x - 30, player.pos.y - 150)
        # update color
        if self.health > 40 and self.health < 60:
            self.color = GREEN
        if self.health > 20 and self.health < 40:
            self.color = YELLOW
        if (self.health < 20):
            self.color = RED

        if self.health <= 0:
            self.alive = False

    def render(self):
        pygame.draw.rect(WINDOW, BLACK, pygame.Rect(self.pos.x, self.pos.y, 60, 10), width=3)
        pygame.draw.rect(WINDOW, self.color, pygame.Rect(self.pos.x, self.pos.y, self.health, 10))


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.raw_image = pygame.image.load("spaceship_red.png")
        self.image = pygame.transform.scale(self.raw_image,
                                            (self.raw_image.get_width() / 6, self.raw_image.get_height() / 6))
        self.image = pygame.transform.rotate(self.image, 270)
        self.rect = self.image.get_rect()
        self.rect.x = 600
        self.rect.y = 200

        self.target_x = random.randint(400, 600)
        self.target_y = random.randint(10, 300)

        self.CAN_FIRE = False

    def update(self):
        # y between 50 and 200
        # x between 400 and 600
        if self.rect.x != self.target_x:
            if self.rect.x != self.target_x:
                if self.rect.x < self.target_x:
                    self.rect.x += 5
                if self.rect.x > self.target_x:
                    self.rect.x -= 5

        if self.rect.y != self.target_y - 10:
            if self.rect.y < self.target_y:
                self.rect.y += 5
            if self.rect.y > self.target_y:
                self.rect.y -= 5

        base = math.floor(self.target_x / 10)

        if self.target_x - 5 < self.rect.x < self.target_x + 5:
            self.fire()
            self.target_x = random.randint(300, 700)
            self.target_y = random.randint(50, 300)

        # check for collision between enemy bullet and player
        for bullet in enemyBullets:
            if pygame.Rect.colliderect(bullet.rect, player.rect):
                playerHealthBar.health -= 1

    def render(self):
        WINDOW.blit(self.image, self.rect)

    def fire(self):
        if (self.CAN_FIRE):
            bullet = EnemyBullet()
            enemyBullets.append(bullet)


backGround = Background()
ground = Ground()
ground_group = pygame.sprite.Group()
ground_group.add(ground)
enemy = Enemy()
enemy_group = pygame.sprite.Group()
enemy_group.add(enemy)
player = Player()
bullets = []
playerHealthBar = PlayerHealthBar()
enemyHealthBar = EnemyHealthBar()
enemyBullets = []

gameOn = True

while gameOn:
    player.gravity_check()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

        if event.type == MOUSEBUTTONDOWN:
            left_click, middle_click, right_click = pygame.mouse.get_pressed()
            if left_click and CAN_FIRE:
                bullet = Bullet()
                bullets.append(bullet)

    backGround.render()
    ground.render()

    player.update()
    player.move()
    player.render()

    enemy.update()
    enemy.render()

    playerHealthBar.update()
    playerHealthBar.render()

    enemyHealthBar.update()
    enemyHealthBar.render()

    CAN_FIRE = BulletManager()
    EnemyBulletManager()

    for bullet in bullets:
        bullet.move()
        bullet.update()
        bullet.render()

    for bullet in enemyBullets:
        bullet.move()
        bullet.update()
        bullet.render()

    pygame.display.update()
    FPS_CLOCK.tick(FPS)

    if not playerHealthBar.alive:
        print("Enemy Won!")
        gameOn = False

    if not enemyHealthBar.alive:
        print("Player Won!")
        gameOn = False
