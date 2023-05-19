import random

import pygame

pygame.init()
FPS = 60
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
ENEMY_SIZE = 25
PLAYER_SIZE = 40


class Circle:
    def __init__(self, x, y, radius):
        self.radius = radius
        self.x = x
        self.y = y

    def check_collision(self, other):
        return self.radius + other.radius >= ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** .5


class Enemy(Circle):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.speed = 120 + random.randint(-30, 30)
        self.type = random.randint(0, 3)

    def enemy_move(self, player):
        dist = ((player.y - self.y) ** 2 + (player.x - self.x) ** 2) ** .5
        sin_pl = (player.x - self.x) / dist
        cos_pl = (player.y - self.y) / dist
        self.x += self.speed * dt * sin_pl * random.uniform(0.5, 1.5) + random.randint(-1, 1)
        self.y += self.speed * dt * cos_pl * random.uniform(0.5, 1.5) + random.randint(-1, 1)


class Player(Circle):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.speed = 300
        self.health = 10
        self.killed = 0

    def player_movement(self, keys):
        change_x, change_y = 0, 0
        if keys[pygame.K_w]:
            change_y = -self.speed * dt
        if keys[pygame.K_s]:
            change_y = self.speed * dt
        if keys[pygame.K_a]:
            change_x = -self.speed * dt
        if keys[pygame.K_d]:
            change_x = self.speed * dt
        if change_x != 0 and change_y != 0:
            change_x, change_y = change_x / 2 ** .5, change_y / 2 ** .5
        change_x, change_y = int(change_x), int(change_y)
        self.x += change_x
        self.y += change_y

    def player_shooting(self, bullets):
        bullets.append(Bullet('red', self.x, self.y, 5, *pygame.mouse.get_pos()))


class Bullet(Circle):

    def __init__(self, color, x, y, radius, mouse_x, mouse_y):
        super().__init__(x, y, radius)
        self.color = color
        self.sin = (mouse_x - self.x) / ((mouse_y - self.y) ** 2 + (mouse_x - self.x) ** 2) ** .5
        self.cos = (mouse_y - self.y) / ((mouse_y - self.y) ** 2 + (mouse_x - self.x) ** 2) ** .5
        self.speed = 600

    def draw_circle(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def bullet_move(self):
        self.x += self.speed * self.sin * dt
        self.y += self.speed * self.cos * dt


def new_enemy():
    return random.choice([
        Enemy(random.randint(screen.get_width(), screen.get_width() + 100),
              random.randint(0, screen.get_height()), ENEMY_SIZE),
        Enemy(random.randint(-100, 0),
              random.randint(0, screen.get_height()), ENEMY_SIZE),
        Enemy(random.randint(0, screen.get_width()),
              random.randint(screen.get_height(), screen.get_height()) + 100, ENEMY_SIZE),
        Enemy(random.randint(0, screen.get_width()),
              random.randint(-100, 0), ENEMY_SIZE)
    ])


player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player = Player(*player_pos, PLAYER_SIZE)
dara_image = pygame.image.load('Assets/dara_game.png')
dara = pygame.transform.scale(dara_image, (PLAYER_SIZE * 2, PLAYER_SIZE * 2))
zombie_images = [pygame.image.load(f'Assets/zombie{i}.png') for i in range(1, 5)]
zombies = [pygame.transform.scale(zombie, (ENEMY_SIZE * 2, ENEMY_SIZE * 2)) for zombie in zombie_images]
background_image = pygame.image.load('Assets/background_green.png')
background = pygame.transform.scale(background_image, (screen.get_width(), screen.get_width()))

green_circles = [new_enemy() for _ in range(8)]
bullets = []
NEW_BULLET, bullet_time = pygame.USEREVENT + 1, 250
NEW_ENEMY, enemy_time = pygame.USEREVENT + 2, 800

pygame.time.set_timer(NEW_BULLET, bullet_time)
pygame.time.set_timer(NEW_ENEMY, enemy_time)

FONT = pygame.font.SysFont('comicsans', 40)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == NEW_BULLET:
            player.player_shooting(bullets)
        if event.type == NEW_ENEMY:
            green_circles.append(new_enemy())
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     player.player_shooting(bullets)
    screen.blit(background, (0, 0))
    screen.blit(dara, (player.x - PLAYER_SIZE, player.y - PLAYER_SIZE))
    to_remove_enemies = set()
    to_remove_bullets = set()

    for green_circle in green_circles:
        screen.blit(zombies[green_circle.type], (green_circle.x - ENEMY_SIZE, green_circle.y - ENEMY_SIZE))
        green_circle.enemy_move(player)
        if player.check_collision(green_circle):
            player.health -= 1
            to_remove_enemies.add(green_circle)
        for bullet in bullets:
            if bullet.check_collision(green_circle):
                to_remove_enemies.add(green_circle)
                to_remove_bullets.add(bullet)
    player.killed += len(to_remove_enemies)
    for bullet in bullets:
        if (bullet.x > screen.get_width() + bullet.radius or bullet.x < -bullet.radius
                or bullet.y > screen.get_height() + bullet.radius or bullet.y < -bullet.radius):
            to_remove_bullets.add(bullet)
    for bullet in to_remove_bullets:
        bullets.remove(bullet)
    for green_circle in to_remove_enemies:
        green_circles.remove(green_circle)
    for bullet in bullets:
        bullet.draw_circle()
        bullet.bullet_move()
    keys = pygame.key.get_pressed()
    player.player_movement(keys)

    health_text = FONT.render(f"Health: {player.health}", True, 'white')
    screen.blit(health_text, (10, 10))
    kills_text = FONT.render(f"Kills: {player.killed}", True, 'red')
    screen.blit(kills_text, (10, 60))
    pygame.display.update()
    dt = clock.tick(FPS) / 1000
pygame.quit()
