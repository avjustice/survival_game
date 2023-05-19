import random
# import button

import pygame

FPS = 60
WIDTH = 1280
HEIGHT = 720
ENEMY_SIZE = 35
PLAYER_SIZE = 45
BOSS_SIZE = 60
ENEMY_TYPES = 11


class Circle:
    def __init__(self, x, y, radius):
        self.radius = radius
        self.x = x
        self.y = y

    def check_collision(self, other):
        return self.radius + other.radius >= ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** .5


class Enemy(Circle):
    def __init__(self, x, y, radius, easy=True):
        super().__init__(x, y, radius)
        if easy:
            self.speed = 120 + random.randint(-30, 30)
        else:
            self.speed = 150 + random.randint(-30, 30)
        self.type = random.randint(0, ENEMY_TYPES - 1)
        self.health = 1
        self.price = 1

    def enemy_move(self, player):
        dist = ((player.y - self.y) ** 2 + (player.x - self.x) ** 2) ** .5
        sin_pl = (player.x - self.x) / dist
        cos_pl = (player.y - self.y) / dist
        self.x += self.speed * dt * sin_pl * random.uniform(0.5, 1.5)
        self.y += self.speed * dt * cos_pl * random.uniform(0.5, 1.5)


class Boss(Enemy):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.speed = 280
        self.health = 2
        self.price = 5


class Player(Circle):
    def __init__(self, x, y, radius, image):
        super().__init__(x, y, radius)
        self.image = image
        self.speed = 320
        self.health = 5
        self.score = 0

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
        self.x = min(WIDTH - self.radius, max(self.radius, self.x + change_x))
        self.y = min(HEIGHT - self.radius, max(self.radius, self.y + change_y))

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
        Enemy(random.randint(WIDTH, WIDTH + 100), random.randint(0, HEIGHT), ENEMY_SIZE),
        Enemy(random.randint(-100, 0), random.randint(0, HEIGHT), ENEMY_SIZE),
        Enemy(random.randint(0, WIDTH), random.randint(HEIGHT, HEIGHT) + 100, ENEMY_SIZE),
        Enemy(random.randint(0, WIDTH), random.randint(-100, 0), ENEMY_SIZE)
    ])


def new_boss():
    return random.choice([
        Boss(random.randint(WIDTH, WIDTH + 100), random.randint(0, HEIGHT), ENEMY_SIZE),
        Boss(random.randint(-100, 0), random.randint(0, HEIGHT), ENEMY_SIZE),
    ])


def game_over():
    game_over_font = pygame.font.SysFont('Arial', 50)
    game_over_text = game_over_font.render(f'Игра окончена!', False, 'yellow')
    screen.blit(game_over_text, (200, HEIGHT // 2 - 250))
    draw_text = game_over_font.render(f'Ваш результат: {player.score}', False, 'yellow')
    screen.blit(draw_text, (200, HEIGHT // 2 - 190))
    if player.score > RECORD:
        record_text = game_over_font.render(f'Вы установили новый рекорд!', False, 'yellow')
        with open('record.txt', 'w') as f:
            f.write(str(player.score))
    else:
        record_text = game_over_font.render(f'Рекорд: {RECORD}', False, 'yellow')
    screen.blit(record_text, (200, HEIGHT // 2 - 130))
    pygame.display.update()
    pygame.time.delay(5000)


def text_render():
    health_text = DEFAULT_FONT.render(f"Здоровье: {player.health}", True, 'red')
    screen.blit(health_text, (10, 10))
    kills_text = DEFAULT_FONT.render(f"Очки: {player.score}", True, 'red')
    screen.blit(kills_text, (10, 60))
    record = max(RECORD, player.score)
    record_text = DEFAULT_FONT.render(f"Рекорд: {record}", True, 'white')
    screen.blit(record_text, (10, 110))


def draw_game(player_to_draw, enemies_to_draw, bullets_to_draw):
    screen.blit(background, (0, 0))
    text_render()
    screen.blit(player_to_draw.image, (player.x - PLAYER_SIZE, player.y - PLAYER_SIZE))
    for enemy_to_draw in enemies_to_draw:
        if isinstance(enemy_to_draw, Boss):
            screen.blit(boss, (enemy_to_draw.x - BOSS_SIZE, enemy_to_draw.y - BOSS_SIZE))
        else:
            screen.blit(zombies[enemy_to_draw.type], (enemy_to_draw.x - ENEMY_SIZE, enemy_to_draw.y - ENEMY_SIZE))
    for bullet_to_draw in bullets_to_draw:
        bullet_to_draw.draw_circle()


def remove_dead_elements(player_check, enemies_check, bullets_check):
    dead_enemies = set()
    dead_bullets = set()
    for enemy_check in enemies_check:
        enemy_check.enemy_move(player_check)
        if player_check.check_collision(enemy_check):
            player_check.health = max(player_check.health - 1, 0)
            dead_enemies.add(enemy_check)
        for bullet_check in bullets_check:
            if bullet_check.check_collision(enemy_check):
                dead_enemies.add(enemy_check)
                dead_bullets.add(bullet_check)
    player.score += len(dead_enemies)
    for bullet_check in bullets_check:
        if (bullet_check.x > WIDTH + bullet_check.radius or bullet_check.x < -bullet_check.radius
                or bullet_check.y > HEIGHT + bullet_check.radius or bullet_check.y < -bullet_check.radius):
            dead_bullets.add(bullet_check)
    return dead_enemies, dead_bullets


if __name__ == '__main__':

    pygame.init()
    FPS = 60
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    with open('record.txt', 'r') as f:
        data = f.read()
        RECORD = int(data) if data else 0

    # dara_image = pygame.image.load('Assets/dara_game.png')
    # dara = pygame.transform.scale(dara_image, (PLAYER_SIZE * 2, PLAYER_SIZE * 2))

    leha_image = pygame.image.load('Assets/leha.png')
    leha = pygame.transform.scale(leha_image, (PLAYER_SIZE * 2, PLAYER_SIZE * 2))
    zombie_images = [pygame.image.load(f'Assets/pivo/beer{i}.png') for i in range(1, ENEMY_TYPES + 1)]
    zombies = [pygame.transform.scale(zombie, (ENEMY_SIZE * 2, ENEMY_SIZE * 2)) for zombie in zombie_images]
    boss_image = pygame.image.load('Assets/boss.png')
    boss = pygame.transform.scale(boss_image, (BOSS_SIZE * 2, BOSS_SIZE * 2))
    background_image = pygame.image.load('Assets/background_green.png')
    background = pygame.transform.scale(background_image, (WIDTH, WIDTH))

    # start_img = pygame.image.load('Assets/start_btn.png').convert_alpha()
    # start_button = button.Button(100, 200, start_img, 0.8)
    player = Player(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, leha)
    enemies = [new_enemy() for _ in range(8)]
    bullets = []

    NEW_BULLET, bullet_time = pygame.USEREVENT + 1, 250
    NEW_ENEMY, enemy_time = pygame.USEREVENT + 2, 800
    NEW_BOSS, boss_time = pygame.USEREVENT + 3, 10000
    pygame.time.set_timer(NEW_BULLET, bullet_time)
    pygame.time.set_timer(NEW_ENEMY, enemy_time)
    pygame.time.set_timer(NEW_BOSS, boss_time)
    DEFAULT_FONT = pygame.font.SysFont('comicsans', 40)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == NEW_BULLET:
                player.player_shooting(bullets)
            if event.type == NEW_ENEMY:
                enemies.append(new_enemy())
            if event.type == NEW_BOSS:
                enemies.append(new_boss())

        draw_game(player, enemies, bullets)

        to_remove_enemies, to_remove_bullets = remove_dead_elements(player, enemies, bullets)

        if player.health == 0:
            game_over()
            break

        for bullet in to_remove_bullets:
            bullets.remove(bullet)
        for enemy in to_remove_enemies:
            enemies.remove(enemy)

        for bullet in bullets:
            bullet.bullet_move()
        for enemy in enemies:
            enemy.enemy_move(player)
        keys = pygame.key.get_pressed()
        player.player_movement(keys)
        text_render()
        # start_button.draw(screen)
        pygame.display.update()
        dt = clock.tick(FPS) / 1000
    pygame.quit()
