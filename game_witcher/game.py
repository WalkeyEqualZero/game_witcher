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
print("ASSET_DIRECTORY", ASSET_DIRECTORY)


class CharacterState(Enum):
    idle = 0
    walk = 1
    attack = 2
    attack2 = 3
    attack3 = 4


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

    def tick(self):
        pass


class Character:
    animation_by_state: Dict[CharacterState, MirrorAnimation]

    def __init__(self, x, y, screen, ch, back, weight, height, asset_directory):
        self.life = 15
        self.char = pygame.transform.scale(pygame.image.load(asset_directory + ch), (weight, height))
        self.count = 0
        self.delta = 0
        self.on = False
        self.rotate = RotateAnimation(15.0, 7)

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
        }

        self.mirror_char = pygame.transform.flip(self.char, True, False)
        self.x = x
        self.y = y
        self.last_key = "right"
        self.char_rect = self.char.get_rect(topleft=(x, y))
        self.win = screen
        self.attack_last = []
        self.vel = 5
        self.bg = back
        self.torf = False
        self.last_attack = None

        self.direction = CharacterDirection.right
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

        anim = pygame.transform.rotate(anim, self.rotate.cur_eagle)
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
        self.height = height
        self.win = screen
        self.directory = asset_directory
        self.last_side = "left"
        self.hp = 100
        self.bg = None
        self.vel = 2
        self.def_bg = 'instructions.png'
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
        if self.bg == self.def_bg:
            if self.direction == EnemyDirection.left:
                anim = self.animation_by_state[self.state].left[self.counter_animation.animation_cnt]
            else:
                anim = self.animation_by_state[self.state].right[self.counter_animation.animation_cnt]

            anim = pygame.transform.rotate(anim, self.rotate.cur_eagle)
            self.win.blit(anim, (self.x, self.y))

            self.counter_animation.tick()
            self.rotate.tick()
            self.rect = self.enemy.get_rect(topleft=(self.x, self.y))

        else:
            self.rect = self.enemy.get_rect(topleft=(-1000, -1000))


class World:
    def __init__(self, screen, char_x, char_y):
        self.last_tp = None
        self.char_x = char_x
        self.char_y = char_y
        self.screen = screen
        self.right_rect = pygame.Rect(1100, 315, 20, char_y)
        self.left_rect = pygame.Rect(-100, 315, 20, char_y)

    def is_collided(self, character):
        if self.last_tp == "right" and self.left_rect.colliderect(character.char_rect):
            return 0
        elif self.last_tp == "left" and self.right_rect.colliderect(character.char_rect):
            return 0
        else:
            self.last_tp = None
        if self.right_rect.colliderect(character.char_rect):
            self.last_tp = "right"
            return 1
        elif self.left_rect.colliderect(character.char_rect):
            self.last_tp = "left"
            return -1
        else:
            return 0


logging.basicConfig(level=logging.DEBUG)

win = pygame.display.set_mode((1012, 576))
pygame.display.set_caption("The Witcher 4 Flat World")
pygame.display.set_caption("The Witcher 4 Flat World")
bg = pygame.image.load(ASSET_DIRECTORY + 'instructions.png')
bg = pygame.transform.scale(bg, (1012, 576))
bgs_names = ['tamploin 2.0.png', 'menu.jpg', 'instructions.png']
bgs = [pygame.image.load(ASSET_DIRECTORY+'tamploin 2.0.png'), pygame.image.load(ASSET_DIRECTORY + 'menu.jpg'), pygame.image.load(
    ASSET_DIRECTORY + 'instructions.png')]
width = 0
clock = pygame.time.Clock()
last = 2
run = True

char = Character(500, 360, win, 'idle_00.png', bg, 210, 210, ASSET_DIRECTORY_CHARACTER)
enem = Enemy(500, 255, 350, 280, win, ASSET_DIRECTORY_ENEMY)
game = World(win, 210, 210)


while run:
    clock.tick(56)
    win.blit(bg, (0, 0))

    pressed_attack = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and event.unicode == 'u':
            pressed_attack = True

        logging.info(event)

    if char.life > 0:
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

    if not enem.dead:
        if abs(char.x - enem.x) <= 30 and enem.direction == EnemyDirection.left:
            enem.set_state(EnemyState.attack)
            if char.rotate.cur_eagle < 0.1:
                char.rotate.rotate()
                char.life -= 1

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

    enem.redraw_screen()
    char.redraw_screen()
    last_r = last + game.is_collided(char)
    bg = pygame.transform.scale(bgs[last_r], (1012, 576))
    enem.bg = bgs_names[last_r]
    last = last_r
    if game.is_collided(char) == 1:
        char.x = -60
    elif game.is_collided(char) == -1:
        char.x = 900
    else:
        game.right_rect = pygame.Rect(1100, 315, 20, game.char_y)
        game.left_rect = pygame.Rect(-100, 315, 20, game.char_y)

    if enem.hp <= 0:
        myfont = pygame.font.SysFont('Comic Sans MS', 100)
        textsurface = myfont.render('Вы выграли', False, (255, 255, 255))
        win.blit(textsurface, (400, 300))

    if char.life <= 0:
        char.rotate = StrictRotate(90)
        myfont = pygame.font.SysFont('Comic Sans MS', 100)
        textsurface = myfont.render('Вы проиграли', False, (255, 255, 255))
        win.blit(textsurface, (400, 300))

    pygame.display.update()

pygame.quit()
