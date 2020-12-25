import os
import pygame
import sys

pygame.init()

FPS = 50
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


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
    '''
    Класс врага
    '''

    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
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


def terminate():
    '''
    Прерывание игры
    :return:
    '''
    pygame.quit()
    sys.exit()


def start_screen():
    '''
    Начальная заставка с кнопками
    :return:
    '''
    font = pygame.font.Font('./data/Amatic-Bold.ttf', 36)
    screen.fill(pygame.Color("black"))
    button = load_image('button.png')
    screen.blit(button, (300, 200))
    string_rendered = font.render('START GAME', True, pygame.Color('black'))
    intro_rect = string_rendered.get_rect().move(350, 200)
    screen.blit(string_rendered, intro_rect)
    screen.blit(button, (300, 250))
    string_rendered = font.render('RECORDS', True, pygame.Color('black'))
    intro_rect = string_rendered.get_rect().move(360, 250)
    screen.blit(string_rendered, intro_rect)
    screen.blit(button, (300, 300))
    string_rendered = font.render('EXIT', True, pygame.Color('black'))
    intro_rect = string_rendered.get_rect().move(380, 300)
    screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 300 <= event.pos[0] <= 500 and 200 <= event.pos[1] <= 245:
                    game()
                    return
                if 300 <= event.pos[0] <= 500 and 250 <= event.pos[1] <= 295:
                    new_record()
                if 300 <= event.pos[0] <= 500 and 300 <= event.pos[1] <= 345:
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


def new_record():
    '''
    Добавление рекорда
    :return:
    '''
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
                    name = 'RECORDED!'
                    recorded = True
        screen.fill(pygame.Color("black"))
        font = pygame.font.Font('./data/Amatic-Bold.ttf', 36)
        button = load_image('button.png')
        screen.blit(button, (300, 200))
        string_rendered = font.render('Enter your name:', 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(320, 100)
        screen.blit(string_rendered, intro_rect)
        string_rendered = font.render('OK', 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect().move(390, 200)
        screen.blit(string_rendered, intro_rect)
        string_rendered = font.render(name, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(320, 150)
        screen.blit(string_rendered, intro_rect)
        pygame.display.flip()
        clock.tick(FPS)
        if recorded:
            pygame.time.delay(2000)
            start_screen()
            return


def game():
    '''
    Основной игровой цикл
    :return:
    '''
    ship = Ship(load_image("ship.gif"), 8, 1, 350, 500)
    for y in range(20, 300, 50):
        for x in range(100, 700, 75):
            enemy = Enemy(load_image('enemy.png'), 2, 1, x, y)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
    pygame.quit()


all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

start_screen()
