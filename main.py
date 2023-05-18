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

    def draw_circle(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Player(Circle):
    def player_movement(self, keys):
        if keys[pygame.K_w]:
            self.y -= 300 * dt
        if keys[pygame.K_s]:
            self.y += 300 * dt
        if keys[pygame.K_a]:
            self.x -= 300 * dt
        if keys[pygame.K_d]:
            self.x += 300 * dt


player = Player("red", *player_pos, 40)
green_circles = [Circle("green", random.randint(0, screen.get_width()), random.randint(0, screen.get_height()), 10)
                 for i in range(10)]
# screen.fill("white")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")
    player.draw_circle()
    to_remove = None
    for green_circle in green_circles:
        green_circle.draw_circle()
        if player.check_collision(green_circle):
            to_remove = green_circle
    if to_remove:
        green_circles.remove(to_remove)
    keys = pygame.key.get_pressed()
    player.player_movement(keys)

    pygame.display.update()
    dt = clock.tick(FPS) / 1000
pygame.quit()
