import pygame
import os
import logging

from datetime import datetime
from game_witcher.utils import pygame_load_image
from enum import Enum
from typing import List, Dict
from copy import deepcopy


pygame.init()

ASSET_DIRECTORY = os.path.dirname(__file__) + "/../assets/"
ASSET_DIRECTORY_CHARACTER = os.path.dirname(__file__) + "/../assets/character/"
ASSET_DIRECTORY_ENEMY = os.path.dirname(__file__) + "/../assets/enemy/"
ASSET_DIRECTORY_KEIR = os.path.dirname(__file__) + "/../assets/keir/"
ASSET_DIRECTORY_KING = os.path.dirname(__file__) + "/../assets/king/"
print("ASSET_DIRECTORY", ASSET_DIRECTORY)


class CharacterState(Enum):
    idle = 0
    walk = 1
    attack = 2
    attack2 = 3
    attack3 = 4
    dead = 5


class CharacterDirection(Enum):
    left = 0
    right = 1


class EnemyDirection(Enum):
    left = 0
    right = 1


class EnemyState(Enum):
    idle = 0
    dead = 1
    walk = 2
    attack = 3


class MirrorAnimation:
    left: List[pygame.Surface]
    right: List[pygame.Surface]

    def __init__(self, animation: List[pygame.Surface]):
        self.right = animation
        self.left = list(map(lambda i: pygame.transform.flip(i, True, False), animation))


class CounterAnimation:
    def __init__(self, max_frame_cnt, max_animation_cnt, animation_end_function=None, whitelist_reset=None, freeze_on_end=False):
        self._whitelist_reset = whitelist_reset
        self._max_frame_cnt = max_frame_cnt
        self._max_animation_cnt = max_animation_cnt
        self._frame_cnt = 0
        self._animation_cnt = 0
        self._animation_end_function = animation_end_function
        self.freeze_on_end = freeze_on_end

    def access_reset(self, state):
        return self._whitelist_reset is None or state in self._whitelist_reset

    @property
    def animation_cnt(self):
        return self._animation_cnt

    @property
    def frame_cnt(self):
        return self._frame_cnt

    def duplicate(self):
        new = deepcopy(self)
        new._frame_cnt = 0
        new._animation_cnt = 0

        return new

    def tick(self):
        self._frame_cnt += 1
        if self._frame_cnt >= self._max_frame_cnt:
            self._frame_cnt = 0

            if not self.freeze_on_end or self._animation_cnt != self._max_animation_cnt -1 :
                self._animation_cnt += 1

            if self._animation_cnt >= self._max_animation_cnt:
                if self._animation_end_function is None:
                    self._animation_cnt = 0
                else:
                    self._animation_end_function()


class RotateAnimation:
    def __init__(self, eagle, steps):
        self._eagle = eagle
        self.steps = steps
        self.cur_eagle = 0

    @property
    def eagle(self):
        return self._eagle

    def rotate(self):
        self.cur_eagle = self._eagle

    def tick(self):
        self.cur_eagle -= 0.1 + self._eagle / self.steps
        if self.cur_eagle <= 0:
            self.cur_eagle = 0


class StrictRotate:
    def __init__(self, eagle):
        self.cur_eagle = eagle

    def rotate(self):
        pass

    def tick(self):
        pass


class Keir:
    def __init__(self, x, y, screen, weight, height, asset_directory):
        self.keir_sprite = pygame.transform.scale(pygame.image.load(asset_directory + 'barkeep_00.png'), (weight, height))
        self.rect = self.keir_sprite.get_rect(topleft=(-1000, -1000))
        self.win = screen
        self.x = x
        self.y = y
        self.bg = None
        self.default = 'tavern.png'
        self.show_text = False
        self.showed = False
        self.n_text = 0
        self.text = ['Приветствую тебя ведьмак. Какими судьбами ты здесь?',
                     'Очень высокий и сильный, однако медлительный.',
                     'Удачи!']

        self.animation_by_state = MirrorAnimation(pygame_load_image
                                                  (0, 5, os.path.join(asset_directory, "barkeep_{}.png"),
                                                   (weight, height), max_number_len=2)),
        self.counter_animation_by_state = CounterAnimation(10, 5)

        self.counter_animation = self.counter_animation_by_state.duplicate()

    def redraw_screen(self):
        if self.default == self.bg:
            self.rect = self.keir_sprite.get_rect(topleft=(self.x, self.y))
            anim = self.animation_by_state[0].right[self.counter_animation.animation_cnt]
            self.win.blit(anim, (self.x, self.y))

            self.counter_animation.tick()
        else:
            self.rect = self.keir_sprite.get_rect(topleft=(-1000, -1000))


class King:
    def __init__(self, x, y, screen, weight, height, asset_directory):
        self.king_sprite = pygame.transform.scale(pygame.image.load(asset_directory + 'king_00.png'), (weight, height))
        self.rect = self.king_sprite.get_rect(topleft=(x, y))
        self.win = screen
        self.x = x
        self.y = y
        self.bg = None
        self.default = 'Castle_5.png'
        self.show_text = False
        self.showed = False
        self.n_text = 0
        self.text = ['Геральт у меня к тебе есть задание.',
                     'С демоном, последнее время он нападает на людей.',
                     'Зайди в бар к Кейру он может знать о демоне.']

        self.animation_by_state = MirrorAnimation(pygame_load_image
                                                  (0, 17, os.path.join(asset_directory, "king_{}.png"),
                                                   (weight, height), max_number_len=2)),
        self.counter_animation_by_state = CounterAnimation(5, 17)

        self.counter_animation = self.counter_animation_by_state.duplicate()

    def redraw_screen(self):
        if self.default == self.bg:
            anim = self.animation_by_state[0].right[self.counter_animation.animation_cnt]
            self.win.blit(anim, (self.x, self.y))

            self.counter_animation.tick()


class Character:
    animation_by_state: Dict[CharacterState, MirrorAnimation]

    def __init__(self, x, y, screen, ch, back, weight, height, asset_directory):
        self.life = 15
        self.char = pygame.transform.scale(pygame.image.load(asset_directory + ch), (weight, height))
        self.count = 0
        self.delta = 0
        self.on = False
        self.quest = False
        self.quest_2 = False
        self.rotate = RotateAnimation(15.0, 7)
        self.n_text = 0
        self.text = ['С кем на этот раз надо разобраться?',
                     'У кого я могу получить больше информации о нём?',
                     'Помните, мои услуги не дешёвые.']

        self.text_2 = ['Здравствуй Кейр, мне нужно разузнать о демоне.',
                       'Спасибо тебе за помощь.']

        self.animation_by_state = {
            CharacterState.attack: MirrorAnimation(
                pygame_load_image(0, 7,  os.path.join(asset_directory, "attack_{}.png"), (weight, height),
                                  max_number_len=2)
            ),
            CharacterState.attack2: MirrorAnimation(
                pygame_load_image(8, 7, os.path.join(asset_directory, "attack_{}.png"), (weight, height),
                                  max_number_len=2)
            ),
            CharacterState.attack3: MirrorAnimation(
                pygame_load_image(14, 7, os.path.join(asset_directory, "attack_{}.png"), (weight, height))
            ),
            CharacterState.idle: MirrorAnimation(
                pygame_load_image(0, 15, os.path.join(asset_directory, "idle_{}.png"), (weight, height))
            ),
            CharacterState.walk: MirrorAnimation(
               pygame_load_image(0, 8, os.path.join(asset_directory, "run_{}.png"), (weight, height))
            ),
            CharacterState.dead: MirrorAnimation(
                pygame_load_image(0, 14, os.path.join(asset_directory, "death_{}.png"), (weight, height))
            ),

        }
        self.animation_screen_state = 0

        self.counter_animation_by_state = {
            CharacterState.attack: CounterAnimation(
                5, 7,
                animation_end_function=lambda: self.set_state_force(CharacterState.idle),
                whitelist_reset=(CharacterState.attack2,),
            ),
            CharacterState.attack2: CounterAnimation(
                5, 7,
                animation_end_function=lambda: self.set_state_force(CharacterState.idle),
                whitelist_reset=(CharacterState.attack3,),
            ),
            CharacterState.attack3: CounterAnimation(
                5, 7,
                animation_end_function=lambda: self.set_state_force(CharacterState.idle),
                whitelist_reset=(),
            ),
            CharacterState.idle: CounterAnimation(4, 15),
            CharacterState.walk: CounterAnimation(5, 8),
            CharacterState.dead: CounterAnimation(5, 14, freeze_on_end=True),
        }

        self.mirror_char = pygame.transform.flip(self.char, True, False)
        self.x = x
        self.y = y
        self.char_rect = self.char.get_rect(topleft=(x, y))
        self.win = screen
        self.attack_last = []
        self.vel = 5
        self.bg = back
        self.torf = False
        self.last_attack = None

        self.direction = CharacterDirection.left
        self.state = CharacterState.idle
        self.counter_animation = self.counter_animation_by_state[self.state].duplicate()

        self.time = 0.67

    def set_state_force(self, state):
        if self.state != state:
            self.state = state
            self.counter_animation = self.counter_animation_by_state[self.state].duplicate()

    def set_state(self, state):
        if self.counter_animation.access_reset(state):
            self.set_state_force(state)
            return True
        else:
            return False

    def attack(self, enemy):
        if self.char_rect.colliderect(enemy.rect):
            return True
        else:
            return False

    def redraw_screen(self):
        if self.direction == CharacterDirection.left:
            anim = self.animation_by_state[self.state].left[self.counter_animation.animation_cnt]
        else:
            anim = self.animation_by_state[self.state].right[self.counter_animation.animation_cnt]

        # anim = pygame.transform.rotate(anim, self.rotate.cur_eagle)
        self.win.blit(anim, (self.x, self.y))

        self.counter_animation.tick()
        self.rotate.tick()
        self.char_rect = self.char.get_rect(topleft=(self.x, self.y))


class Enemy:
    def __init__(self, x, y, weight, height, screen, asset_directory):
        self.enemy = pygame.transform.scale(pygame.image.load(asset_directory + 'idle_0.png'), (weight, height))
        self.x = x
        self.y = y
        self.weight = weight
        self.quest = False
        self.height = height
        self.win = screen
        self.directory = asset_directory
        self.last_side = "left"
        self.hp = 100
        self.bg = None
        self.vel = 2
        self.def_bg = 'tamploin 2.0.png'
        self.dead = False
        self.rect = self.enemy.get_rect(topleft=(self.x, self.y))
        self.rotate = RotateAnimation(15.0, 7)

        self.animation_by_state = {
            EnemyState.idle: MirrorAnimation(
                pygame_load_image(0, 6, os.path.join(asset_directory, "idle_{}.png"), (weight, height))
            ),
            EnemyState.dead: MirrorAnimation(
                pygame_load_image(0, 7, os.path.join(asset_directory, "dead_{}.png"), (weight, height))
            ),
            EnemyState.walk: MirrorAnimation(
                pygame_load_image(0, 6, os.path.join(asset_directory, "walk_{}.png"), (weight, height))
            ),
            EnemyState.attack: MirrorAnimation(
                pygame_load_image(0, 6, os.path.join(asset_directory, "attack_{}.png"), (weight, height))
            ),
        }

        self.counter_animation_by_state = {
            EnemyState.idle: CounterAnimation(9, 6),
            EnemyState.dead: CounterAnimation(6, 7, freeze_on_end=True),
            EnemyState.walk: CounterAnimation(12, 6),
            EnemyState.attack: CounterAnimation(
                5, 6,
                animation_end_function=lambda: self.set_state_force(EnemyState.idle),
                whitelist_reset=(EnemyState.attack,),
            ),
        }

        self.direction = EnemyDirection.right
        self.state = EnemyState.idle
        self.counter_animation = self.counter_animation_by_state[self.state].duplicate()

    def set_state_force(self, state):
        if self.state != state:
            self.state = state
            self.counter_animation = self.counter_animation_by_state[self.state].duplicate()

    def set_state(self, state):
        if self.counter_animation.access_reset(state):
            self.set_state_force(state)
            return True
        else:
            return False

    def redraw_screen(self):
        if self.bg == self.def_bg and self.quest:
            if self.direction == EnemyDirection.left:
                anim = self.animation_by_state[self.state].left[self.counter_animation.animation_cnt]
            else:
                anim = self.animation_by_state[self.state].right[self.counter_animation.animation_cnt]

            # anim = pygame.transform.rotate(anim, self.rotate.cur_eagle)
            self.win.blit(anim, (self.x, self.y))

            self.counter_animation.tick()
            # self.rotate.tick()
            self.rect = self.enemy.get_rect(topleft=(self.x, self.y))

        else:
            self.rect = self.enemy.get_rect(topleft=(-1000, -1000))


class World:
    def __init__(self, screen, char_x, char_y, bg):
        self.last_tp = None
        self.bg = bg
        self.def_bg = 'tamploin 2.0.png'
        self.char_x = char_x
        self.char_y = char_y
        self.screen = screen
        self.tavern_rect = pygame.Rect(900, 315, 20, char_y)
        self.right_rect = pygame.Rect(1100, 315, 20, char_y)
        self.left_rect = pygame.Rect(-100, 315, 20, char_y)
        self.in_tavern = False

    def is_collided(self, character, last):
        if not self.in_tavern:
            if self.last_tp == "right" and self.left_rect.colliderect(character.char_rect):
                return 0
            elif self.last_tp == "left" and self.right_rect.colliderect(character.char_rect):
                return 0
            else:
                self.last_tp = None
            if self.right_rect.colliderect(character.char_rect) and last < 2:
                self.last_tp = "right"
                character.x = -60
                return 1
            elif self.left_rect.colliderect(character.char_rect) and last != 0:
                self.last_tp = "left"
                character.x = 900
                return -1
            else:
                self.right_rect = pygame.Rect(1100, 315, 20, game.char_y)
                self.left_rect = pygame.Rect(-100, 315, 20, game.char_y)
                return 0
        else:
            return 0

    def tavern(self, character):
        if self.tavern_rect.colliderect(character.char_rect) and self.bg == self.def_bg and not self.in_tavern:
            logging.info('tavern')
            self.in_tavern = True
            character.y = 290
            return 3
        elif self.tavern_rect.colliderect(character.char_rect) and self.bg == 'tavern.png' and self.in_tavern:
            logging.info('tavern')
            self.in_tavern = False
            character.y = 360
            character.x = 720
            return 2
        else:
            self.in_tavern = False
            character.y = 360
            character.x = 720
            return 2


logging.basicConfig(level=logging.DEBUG)

win = pygame.display.set_mode((1012, 576))
pygame.display.set_caption("The Witcher 4 Flat World")
pygame.display.set_caption("The Witcher 4 Flat World")
bg = pygame.image.load(ASSET_DIRECTORY + 'Castle_5.png')
bg = pygame.transform.scale(bg, (1012, 576))
bgs_names = ['Castle_5.png', 'menu.jpg', 'tamploin 2.0.png', 'tavern.png']
bgs = [pygame.image.load(ASSET_DIRECTORY + 'Castle_5.png'), pygame.image.load(
    ASSET_DIRECTORY + 'Forest.png'), pygame.transform.scale(pygame.image.load(ASSET_DIRECTORY+'tamploin 2.0.png'), (1012, 576)), pygame.image.load(ASSET_DIRECTORY + 'tavern_3.png')]
width = 0
clock = pygame.time.Clock()
last = 0
run = True
last_r = 0
end = False
king = King(100, 285, win, 370, 370, ASSET_DIRECTORY_KING)
char = Character(450, 360, win, 'idle_00.png', bg, 210, 210, ASSET_DIRECTORY_CHARACTER)
enem = Enemy(500, 255, 350, 280, win, ASSET_DIRECTORY_ENEMY)
keir = Keir(400, 310, win, 128, 128, ASSET_DIRECTORY_KEIR)
game = World(win, 210, 210, bg)
n_text = 2
pygame.mixer.music.load(ASSET_DIRECTORY + 'Kaer Morhen.mp3')
pygame.mixer.music.play()

while run:
    clock.tick(56)
    win.blit(bg, (0, 0))
    king.redraw_screen()
    pressed_attack = False
    space = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and event.unicode == 'u':
            pressed_attack = True

        if event.type == pygame.KEYDOWN and event.unicode == 'q':
            if bgs_names[last] == 'tamploin 2.0.png' or bgs_names[last] == 'tavern.png':
                last = game.tavern(char)

        if event.type == pygame.KEYDOWN and event.unicode == ' ':
            if char.quest:
                if n_text % 2 == 0:
                    king.n_text += 1
                if n_text % 2 != 0:
                    char.n_text += 1
                n_text += 1
            elif char.quest_2:
                if n_text % 2 == 0:
                    char.n_text += 1
                if n_text % 2 != 0:
                    keir.n_text += 1
                n_text += 1
        logging.info(event)

    if end:
        char.set_state(CharacterState.idle)
    elif char.quest and char.life > 0:
        king.win.blit(pygame.transform.scale(pygame.image.load(ASSET_DIRECTORY + 'panel.png'), (900, 300)), (56, -50))
        char.set_state(CharacterState.idle)
        keys = pygame.key.get_pressed()
        if n_text == 7:
            n_text = 1
            char.n_text = 0
            king.showed = True
            char.quest = False
        if n_text % 2 == 0:
            myfont = pygame.font.Font(ASSET_DIRECTORY + 'pixel.ttf', 20)
            textsurface = myfont.render(king.text[king.n_text], False, (0, 0, 0))
            textsurface_2 = myfont.render('Король:', False, (0, 0, 0))
            win.blit(textsurface, (150, 85))
            win.blit(textsurface_2, (150, 35))
        elif n_text % 2 != 0:
            myfont = pygame.font.Font(ASSET_DIRECTORY + 'pixel.ttf', 20)
            textsurface = myfont.render(char.text[char.n_text], False, (0, 0, 0))
            textsurface_2 = myfont.render('Геральт:', False, (0, 0, 0))
            win.blit(textsurface, (150, 85))
            win.blit(textsurface_2, (150, 35))

    elif char.quest_2 and char.life > 0:
        keir.win.blit(pygame.transform.scale(pygame.image.load(ASSET_DIRECTORY + 'panel.png'), (900, 300)), (56, -50))
        char.set_state(CharacterState.idle)
        keys = pygame.key.get_pressed()
        print(n_text)
        if n_text == 5:
            keir.showed = True
            char.quest_2 = False
            enem.quest = True
        if n_text % 2 == 0:
            myfont = pygame.font.Font(ASSET_DIRECTORY + 'pixel.ttf', 20)
            textsurface = myfont.render(char.text_2[char.n_text], False, (0, 0, 0))
            textsurface_2 = myfont.render('Геральт:', False, (0, 0, 0))
            win.blit(textsurface, (150, 85))
            win.blit(textsurface_2, (150, 35))
        elif n_text % 2 != 0:
            myfont = pygame.font.Font(ASSET_DIRECTORY + 'pixel.ttf', 20)
            textsurface = myfont.render(keir.text[keir.n_text], False, (0, 0, 0))
            textsurface_2 = myfont.render('Кейр:', False, (0, 0, 0))
            win.blit(textsurface, (150, 85))
            win.blit(textsurface_2, (150, 35))

    elif char.life > 0:
        if pressed_attack:
            logging.info("key pressed attack.")
            if char.state == CharacterState.idle:
                if char.attack(enem):
                    enem.hp -= 35
                    enem.rotate.rotate()
                    if enem.hp <= 0:
                        enem.set_state(EnemyState.dead)
                        enem.dead = True
                        logging.info("Death")
                char.set_state(CharacterState.attack)
            elif char.state == CharacterState.attack:
                if char.attack(enem):
                    enem.hp -= 35
                    enem.rotate.rotate()
                    if enem.hp <= 0:
                        enem.set_state(EnemyState.dead)
                        enem.dead = True
                        logging.info("Death")
                char.set_state(CharacterState.attack2)
            elif char.state == CharacterState.attack2:
                if char.attack(enem):
                    enem.hp -= 35
                    enem.rotate.rotate()
                    if enem.hp <= 0:
                        enem.set_state(EnemyState.dead)
                        enem.dead = True
                        logging.info("Death")
                char.set_state(CharacterState.attack3)
        else:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_a] and char.x > char.vel - 200:
                logging.info("key pressed walk left.")

                if char.set_state(CharacterState.walk):
                    char.direction = CharacterDirection.left
                    char.x -= char.vel

            elif keys[pygame.K_d] and char.x < 1100 - char.vel:
                logging.info("key pressed walk right.")

                if char.set_state(CharacterState.walk):
                    char.x += char.vel
                    char.direction = CharacterDirection.right

            else:
                char.set_state(CharacterState.idle)

    if enem.dead:
        enem.set_state(EnemyState.dead)
    elif enem.bg == enem.def_bg and enem.quest:
        if abs(char.x - enem.x) <= 30 and enem.direction == EnemyDirection.left:
            if char.life > 0:
                enem.set_state(EnemyState.attack)
                if char.rotate.cur_eagle < 0.1:
                    char.rotate.rotate()
                    char.life -= 1
            else:
                enem.set_state(EnemyState.idle)

        # elif char.x - enem.x >= 30 and enem.direction == EnemyDirection.right:
        #     enem.set_state(EnemyState.attack)

        elif enem.rect.colliderect(char.char_rect) and enem.state != 1:
            if char.x < enem.x:
                logging.info("enemy walk left.")

                if enem.set_state(EnemyState.walk):
                    enem.direction = EnemyDirection.left
                    enem.x -= enem.vel

            elif char.x > enem.x:
                logging.info("enemy walk right.")

                if enem.set_state(EnemyState.walk):
                    enem.x += enem.vel
                    enem.direction = EnemyDirection.right

        else:
            enem.set_state(EnemyState.idle)

    if king.rect.colliderect(char.char_rect) and not king.showed:
        char.quest = True

    if keir.rect.colliderect(char.char_rect) and not keir.showed:
        char.quest_2 = True

    enem.redraw_screen()
    keir.redraw_screen()
    char.redraw_screen()
    last_r = last + game.is_collided(char, last_r)
    bg = bgs[last_r]
    enem.bg = bgs_names[last_r]
    king.bg = bgs_names[last_r]
    game.bg = bgs_names[last_r]
    keir.bg = bgs_names[last_r]
    # if game.in_tavern:
    #     win.blit(pygame.image.load(ASSET_DIRECTORY + 'tavern_tree.png'), (0, 0))
    last = last_r

    if enem.hp <= 0:
        myfont = pygame.font.Font(ASSET_DIRECTORY + 'pixel.ttf', 100)
        textsurface = myfont.render('Конец', False, (255, 255, 255))
        win.blit(textsurface, (350, 200))
        end = True

    if char.life <= 0:
        char.set_state_force(CharacterState.dead)
        char.rotate = StrictRotate(0)
        myfont = pygame.font.Font(ASSET_DIRECTORY + 'pixel.ttf', 100)
        textsurface = myfont.render('Вы проиграли', False, (255, 255, 255))
        win.blit(textsurface, (150, 200))

    pygame.display.update()

pygame.quit()
