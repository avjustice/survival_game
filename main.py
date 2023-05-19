import random

import pygame

pygame.init()
FPS = 60
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)


class Circle:
    def __init__(self, color, x, y, radius):
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y

    def check_collision(self, other):
        return self.radius + other.radius > ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** .5

    def circle_move(self, player):
        sin_pl = abs(player.x - self.x) / ((player.y - self.y) ** 2 + (player.x - self.x) ** 2) ** .5
        cos_pl = (1 - sin_pl ** 2) ** .5
        speed = 200
        if player.x > self.x:
            self.x += speed * dt * sin_pl
        else:
            self.x -= speed * dt * sin_pl
        if player.y > self.y:
            self.y += speed * dt * cos_pl
        else:
            self.y -= speed * dt * cos_pl

    def draw_circle(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Player(Circle):
    def player_movement(self, keys):
        if keys[pygame.K_w]:
            self.y -= int(300 * dt)
        if keys[pygame.K_s]:
            self.y += int(300 * dt)
        if keys[pygame.K_a]:
            self.x -= int(300 * dt)
        if keys[pygame.K_d]:
            self.x += int(300 * dt)

    def player_shooting(self, bullets):
        bullets.append(Bullet('red', self.x, self.y, 5, *pygame.mouse.get_pos()))


class Bullet(Circle):

    def __init__(self, color, x, y, radius, mouse_x, mouse_y):
        super().__init__(color, x, y, radius)
        self.sin = (mouse_x - self.x) / ((mouse_y - self.y) ** 2 + (mouse_x - self.x) ** 2) ** .5
        self.cos = (mouse_y - self.y) / ((mouse_y - self.y) ** 2 + (mouse_x - self.x) ** 2) ** .5

    def bullet_move(self):
        self.x += 500 * self.sin * dt
        self.y += 500 * self.cos * dt


player = Player("red", *player_pos, 40)
green_circles = [Circle("green", random.randint(0, screen.get_width()), random.randint(0, screen.get_height()), 10) for
                 _ in range(10)]
bullets = []
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.player_shooting(bullets)
    screen.fill("white")
    player.draw_circle()
    to_remove_enemies = set()
    to_remove_bullets = set()
    for green_circle in green_circles:
        green_circle.circle_move(player)
        green_circle.draw_circle()
        for bullet in bullets:
            if bullet.check_collision(green_circle):
                to_remove_enemies.add(green_circle)
                to_remove_bullets.add(bullet)
    for bullet in to_remove_bullets:
        bullets.remove(bullet)
    for green_circle in to_remove_enemies:
        green_circles.remove(green_circle)
        green_circles.append(random.choice([
            Circle("green", random.randint(screen.get_width(), screen.get_width() + 100),
                   random.randint(0, screen.get_height()), 10),
            Circle("green", random.randint(-100, 0),
                   random.randint(0, screen.get_height()), 10),
            Circle("green", random.randint(0, screen.get_width()),
                   random.randint(screen.get_height(), screen.get_height()) + 100, 10),
            Circle("green", random.randint(0, screen.get_width()),
                   random.randint(-100, 0), 10)
        ]))
    for bullet in bullets:
        bullet.draw_circle()
        bullet.bullet_move()
    keys = pygame.key.get_pressed()
    player.player_movement(keys)
    pygame.display.update()
    dt = clock.tick(FPS) / 1000
pygame.quit()
