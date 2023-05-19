import random
import button

import pygame

FPS = 60
WIDTH = 1440
HEIGHT = 840
ENEMY_SIZE = 35
PLAYER_SIZE = 50
BOSS_SIZE = 80
ENEMY_TYPES = 11
RAGE_TIME = 3000


class Circle:
    def __init__(self, x, y, radius):
        self.radius = radius
        self.x = x
        self.y = y

    def check_collision(self, other):
        return self.radius + other.radius >= ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** .5


class Enemy(Circle):
    health = 1
    price = 1

    def __init__(self, x, y, radius, easy=True):
        super().__init__(x, y, radius)
        if easy:
            self.speed = 120 + random.randint(-30, 30)
        else:
            self.speed = 160 + random.randint(-40, 40)
        self.type = random.randint(0, ENEMY_TYPES - 1)

    def enemy_move(self, player, dt):
        dist = ((player.y - self.y) ** 2 + (player.x - self.x) ** 2) ** .5
        sin_pl = (player.x - self.x) / dist
        cos_pl = (player.y - self.y) / dist
        self.x += self.speed * dt * sin_pl * random.uniform(0.5, 1.5)
        self.y += self.speed * dt * cos_pl * random.uniform(0.5, 1.5)


class Boss(Enemy):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.speed = 70 + random.randint(-10, 10)
        self.health = 5
        self.price = 5


class Player(Circle):
    def __init__(self, x, y, radius, image):
        super().__init__(x, y, radius)
        self.image = image
        self.speed = 320
        self.health = 5
        self.score = 0

    def player_movement(self, keys, dt):
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
        bullets.append(Bullet('blue', self.x, self.y, 5, *pygame.mouse.get_pos()))


class Bullet(Circle):

    def __init__(self, color, x, y, radius, mouse_x, mouse_y):
        super().__init__(x, y, radius)
        self.color = color
        self.sin = (mouse_x - self.x) / ((mouse_y - self.y) ** 2 + (mouse_x - self.x) ** 2) ** .5
        self.cos = (mouse_y - self.y) / ((mouse_y - self.y) ** 2 + (mouse_x - self.x) ** 2) ** .5
        self.speed = 600

    def draw_circle(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def bullet_move(self, dt):
        self.x += self.speed * self.sin * dt
        self.y += self.speed * self.cos * dt


def new_enemy(easy=True):
    return random.choice([
        Enemy(random.randint(WIDTH, WIDTH + 100), random.randint(0, HEIGHT), ENEMY_SIZE, easy),
        Enemy(random.randint(-100, 0), random.randint(0, HEIGHT), ENEMY_SIZE, easy),
        Enemy(random.randint(0, WIDTH), random.randint(HEIGHT, HEIGHT) + 100, ENEMY_SIZE, easy),
        Enemy(random.randint(0, WIDTH), random.randint(-100, 0), ENEMY_SIZE, easy)
    ])


def new_boss():
    return random.choice([
        Boss(random.randint(WIDTH, WIDTH + 100), random.randint(0, HEIGHT), BOSS_SIZE),
        Boss(random.randint(-100, 0), random.randint(0, HEIGHT), BOSS_SIZE),
    ])


def game_over(player, screen, record):
    screen.fill((202, 228, 241))
    game_over_font = pygame.font.SysFont('comicsans', 60)
    game_over_text = game_over_font.render(f'Вас догнало пиво!', False, 'black')
    pass
    screen.blit(game_over_text, (WIDTH // 2 - 300, HEIGHT // 2 - 200))
    draw_text = game_over_font.render(f'Ваш результат: {player.score}', False, 'black')
    screen.blit(draw_text, (WIDTH // 2 - 300, HEIGHT // 2 - 120))
    if player.score > record:
        record_text = game_over_font.render(f'Вы установили новый рекорд!', False, 'yellow')
        with open('record.txt', 'w') as f:
            f.write(str(player.score))
    else:
        record_text = game_over_font.render(f'Рекорд: {record}', False, 'yellow')
    screen.blit(record_text, (WIDTH // 2 - 300, HEIGHT // 2 - 40))
    pygame.display.update()
    pygame.time.delay(3000)


def text_render(player, record):
    health_text = DEFAULT_FONT.render(f"Здоровье: {player.health}", True, 'red')
    screen.blit(health_text, (10, 10))
    kills_text = DEFAULT_FONT.render(f"Очки: {player.score}", True, 'red')
    screen.blit(kills_text, (10, 60))
    record = max(record, player.score)
    record_text = DEFAULT_FONT.render(f"Рекорд: {record}", True, 'white')
    screen.blit(record_text, (10, 110))


def draw_game(player_to_draw, enemies_to_draw, bullets_to_draw, record):
    screen.blit(background, (0, 0))
    text_render(player=player_to_draw, record=record)
    screen.blit(player_to_draw.image, (player_to_draw.x - PLAYER_SIZE, player_to_draw.y - PLAYER_SIZE))
    for enemy_to_draw in enemies_to_draw:
        if isinstance(enemy_to_draw, Boss):
            screen.blit(boss, (enemy_to_draw.x - BOSS_SIZE, enemy_to_draw.y - BOSS_SIZE))
        else:
            screen.blit(zombies[enemy_to_draw.type], (enemy_to_draw.x - ENEMY_SIZE, enemy_to_draw.y - ENEMY_SIZE))
    for bullet_to_draw in bullets_to_draw:
        bullet_to_draw.draw_circle()
    pygame.display.update()


def remove_dead_elements(player_check, enemies_check, bullets_check):
    dead_enemies = set()
    dead_bullets = set()
    for enemy_check in enemies_check:
        if player_check.check_collision(enemy_check):
            player_check.health = max(player_check.health - 1, 0)
            dead_enemies.add(enemy_check)
        for bullet_check in bullets_check:
            if bullet_check.check_collision(enemy_check):
                enemy_check.health -= 1
                if enemy_check.health == 0:
                    dead_enemies.add(enemy_check)
                    if isinstance(enemy_check, Boss):
                        player_check.score += 5
                    else:
                        player_check.score += 1
                dead_bullets.add(bullet_check)
    for bullet_check in bullets_check:
        if (bullet_check.x > WIDTH + bullet_check.radius or bullet_check.x < -bullet_check.radius
                or bullet_check.y > HEIGHT + bullet_check.radius or bullet_check.y < -bullet_check.radius):
            dead_bullets.add(bullet_check)
    return dead_enemies, dead_bullets


def gaming_loop():
    player = Player(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, leha)
    enemies = [new_enemy() for _ in range(6)]
    bullets = []
    boss_killed_time = None
    running = True
    dt = 0
    with open('record.txt', 'r') as f:
        data = f.read()
        record = int(data) if data else 0
    while running:
        for event in pygame.event.get():
            boss_lately_killed = boss_killed_time and pygame.time.get_ticks() - boss_killed_time < RAGE_TIME
            if event.type == pygame.QUIT:
                running = False
            if event.type == NEW_BULLET and not boss_lately_killed:
                player.player_shooting(bullets)
            if event.type == NEW_BULLET_FAST and boss_lately_killed:
                player.player_shooting(bullets)
            if event.type == NEW_ENEMY:
                enemies.append(new_enemy())
            if event.type == NEW_FAST_ENEMY and player.score >= 50:
                enemies.append(new_enemy(False))
                if player.score >= 100:
                    enemies.append(new_enemy())
            if event.type == NEW_BOSS:
                enemies.append(new_boss())

        to_remove_enemies, to_remove_bullets = remove_dead_elements(player, enemies, bullets)
        for bullet in to_remove_bullets:
            bullets.remove(bullet)
        for enemy in to_remove_enemies:
            if isinstance(enemy, Boss):
                boss_killed_time = pygame.time.get_ticks()
            enemies.remove(enemy)
        draw_game(player, enemies, bullets, record)
        if player.health == 0:
            game_over(player, screen, record)
            break
        for bullet in bullets:
            bullet.bullet_move(dt)
        for enemy in enemies:
            enemy.enemy_move(player, dt)
        keys = pygame.key.get_pressed()
        player.player_movement(keys, dt)
        dt = clock.tick(FPS) / 1000


def menu():
    start_img = pygame.image.load('Assets/start_btn.png').convert_alpha()
    exit_img = pygame.image.load('Assets/exit_btn.png').convert_alpha()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        screen.fill((202, 228, 241))
        start_button = button.Button(400, 300, start_img, 1)
        exit_button = button.Button(800, 300, exit_img, 1)
        if start_button.draw(screen):
            return True
        if exit_button.draw(screen):
            pygame.quit()
            return False
        pygame.display.update()
        clock.tick(30)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    leha_image = pygame.image.load('Assets/leha.png')
    leha = pygame.transform.scale(leha_image, (PLAYER_SIZE * 2, PLAYER_SIZE * 2))
    zombie_images = [pygame.image.load(f'Assets/pivo/beer{i}.png') for i in range(1, ENEMY_TYPES + 1)]
    zombies = [pygame.transform.scale(zombie, (ENEMY_SIZE * 2, ENEMY_SIZE * 2)) for zombie in zombie_images]
    boss_image = pygame.image.load('Assets/boss.png')
    boss = pygame.transform.scale(boss_image, (BOSS_SIZE * 2, BOSS_SIZE * 2))
    background_image = pygame.image.load('Assets/background_ya.png')
    background = pygame.transform.scale(background_image, (WIDTH, WIDTH))
    NEW_BULLET, bullet_time = pygame.USEREVENT + 1, 250
    NEW_ENEMY, enemy_time = pygame.USEREVENT + 2, 1000
    NEW_BOSS, boss_time = pygame.USEREVENT + 3, 12000
    NEW_FAST_ENEMY, fast_enemy_time = pygame.USEREVENT + 4, 1500
    NEW_BULLET_FAST, bullet_time_fast = pygame.USEREVENT + 5, 125
    pygame.time.set_timer(NEW_BULLET, bullet_time)
    pygame.time.set_timer(NEW_ENEMY, enemy_time)
    pygame.time.set_timer(NEW_BOSS, boss_time)
    pygame.time.set_timer(NEW_FAST_ENEMY, fast_enemy_time)
    pygame.time.set_timer(NEW_BULLET_FAST, bullet_time_fast)
    DEFAULT_FONT = pygame.font.SysFont('comicsans', 40)
    while True:
        a = menu()
        if a:
            gaming_loop()
        else:
            break
