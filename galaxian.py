import os
import pygame
import pygame_gui
import sys
import sqlite3

pygame.init()

FPS = 50
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
db = sqlite3.connect(os.path.join('data', 'records.sqlite'))
cursor = db.cursor()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)

    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Ship(pygame.sprite.Sprite):
    """
    Класс корабля
    """
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.speed = 5
        self.tick = 0
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_anim = 'straight'
        self.cur_frame = 4
        self.image = self.frames[4]
        self.animations = {'straight': 4, 'left': [5, 4, 3, 2, 1], 'right': [5, 6, 7, 8]}
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(pygame.transform.rotate(
                    sheet.subsurface(pygame.Rect(frame_location, self.rect.size)), 90))

    def update(self):
        if self.cur_anim == 'straight':
            self.cur_frame = self.animations['straight']
            self.tick = 0
        if self.cur_anim == 'left':
            if self.tick > 3 and self.cur_frame < 7:
                self.cur_frame += 1
                self.tick = 0
        if self.cur_anim == 'right':
            if self.tick > 3 and self.cur_frame > 1:
                self.cur_frame -= 1
                self.tick = 0
        self.image = self.frames[self.cur_frame]
        self.tick = self.tick + 1


class Enemy(pygame.sprite.Sprite):
    """
    Класс врага
    """

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites, enemies)
        self.speed = 5
        self.tick = 0
        self.frames = []
        self.cur_frame = 0
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[0]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.tick = (self.tick + 1) % 50
        if self.tick == 49:
            self.cur_frame = (self.cur_frame + 1) % 2
        self.image = self.frames[self.cur_frame]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, player_bullets)
        self.speed = 5
        self.image = pygame.Surface((3, 8))
        self.image.fill(pygame.Color('red'))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)

    def update(self):
        self.rect.y -= self.speed
        if pygame.sprite.spritecollideany(self, enemies):
            pygame.sprite.spritecollide(self, enemies, True)
            self.kill()
        if self.rect.y < -10:
            self.kill()


def terminate():
    """
    Прерывание игры
    """
    pygame.quit()
    sys.exit()


def start_screen():
    """
    Начальная заставка с кнопками
    """
    manager = pygame_gui.UIManager((WIDTH, HEIGHT), os.path.join('data', 'menu_theme.json'))
    # Кнопки
    start_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 75, HEIGHT // 3 - 25), (150, 50)),
        text='Начать игру',
        manager=manager
    )
    records_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 75, HEIGHT // 2 - 25), (150, 50)),
        text='Рекорды',
        manager=manager
    )
    exit_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 75, HEIGHT // 2 + 125), (150, 50)),
        text='Выход',
        manager=manager
    )
    back = load_image('start_fon.jpg')
    screen.blit(back, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_btn:
                        game()
                    if event.ui_element == records_btn:
                        show_records()
                    if event.ui_element == exit_btn:
                        terminate()
            manager.process_events(event)
        manager.update(FPS / 1000)
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)


def new_record(score):
    """
    Добавление рекорда
    """
    name = '|'
    recorded = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if 97 <= event.key <= 122:
                    name = name[:-1] + chr(event.key).upper() + '|'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 300 <= event.pos[0] <= 500 and 200 <= event.pos[1] <= 245:
                    cursor.execute(f'''insert into records(name, score) VALUES ('{name[:-1]}', {score})''')
                    db.commit()
                    name = 'RECORDED!'
                    recorded = True
        screen.fill(pygame.Color("black"))
        font = pygame.font.Font('./data/fonts/20219.ttf', 36)
        button = load_image('button.png')
        screen.blit(button, (300, 200))
        string_rendered = font.render('Enter your name:', True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(320, 100)
        screen.blit(string_rendered, intro_rect)
        string_rendered = font.render('OK', True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect().move(390, 200)
        screen.blit(string_rendered, intro_rect)
        string_rendered = font.render(name, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(320, 150)
        screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
        clock.tick(FPS)
        if recorded:
            pygame.time.delay(2000)
            start_screen()
            return


def show_records():
    manager = pygame_gui.UIManager((WIDTH, HEIGHT), os.path.join('data', 'menu_theme.json'))

    # Кнопки
    ok_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 75, HEIGHT - 75), (150, 50)),
        text='Назад',
        manager=manager
    )
    back = load_image('start_fon.jpg')
    screen.blit(back, (0, 0))
    y = 100
    for name, score in sorted(cursor.execute('''select name, score from records''').fetchall(), key=lambda x: -x[1])[:10]:
        font = pygame.font.Font('./data/fonts/20219.ttf', 36)
        string_rendered = font.render(f'{name}: {score}', True, pygame.Color('white'))
        rec_rect = string_rendered.get_rect().move(320, y)
        y += 50
        screen.blit(string_rendered, rec_rect)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == ok_btn:
                        start_screen()
            manager.process_events(event)
        manager.update(FPS / 1000)
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(FPS)


def game():
    """
    Основной игровой цикл
    """
    ship = Ship(load_image("ship.gif"), 8, 1, 350, 500)
    #for y in range(20, 300, 50):
    #    for x in range(100, 700, 75):
    #        enemy = Enemy(load_image('enemy.png'), 2, 1, x, y)
    enemy = Enemy(load_image('enemy.png'), 2, 1, 100, 400)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if len(player_bullets.sprites()) < 3:
                        Bullet(ship.rect.x + ship.rect.w, ship.rect.y)
        ship.cur_anim = 'straight'
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            ship.rect.x -= ship.speed
            ship.cur_anim = 'left'
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            ship.rect.x += ship.speed
            ship.cur_anim = 'right'
        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)
        score = 40 - len(enemies.sprites())
        if len(enemies.sprites()) == 0:
            new_record(score)
            return 0
    pygame.quit()


all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
start_screen()
