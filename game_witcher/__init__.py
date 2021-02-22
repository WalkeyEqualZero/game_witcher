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


class MirrorAnimation:
    left: List[pygame.Surface]
    right: List[pygame.Surface]

    def __init__(self, animation: List[pygame.Surface]):
        self.right = animation
        self.left = list(map(lambda i: pygame.transform.flip(i, True, False), animation))


class CounterAnimation:
    def __init__(self, max_frame_cnt, max_animation_cnt, animation_end_function=None, whitelist_reset=None):
        self._whitelist_reset = whitelist_reset
        self._max_frame_cnt = max_frame_cnt
        self._max_animation_cnt = max_animation_cnt
        self._frame_cnt = 0
        self._animation_cnt = 0
        self._animation_end_function = animation_end_function

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
            self._animation_cnt += 1

            if self._animation_cnt >= self._max_animation_cnt:
                if self._animation_end_function is None:
                    self._animation_cnt = 0
                else:
                    self._animation_end_function()


class Character:
    animation_by_state: Dict[CharacterState, MirrorAnimation]

    def __init__(self, x, y, screen, ch, back, weight, height, asset_directory):
        self.char = pygame.transform.scale(pygame.image.load(asset_directory + ch), (weight, height))
        self.count = 0
        self.delta = 0
        self.on = False

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

    def redraw_screen(self):
        self.win.blit(self.bg, (0, 0))

        self.win.blit(
            getattr(self.animation_by_state[self.state], self.direction.name)[self.counter_animation.animation_cnt],
            (self.x, self.y)
        )
        self.counter_animation.tick()
        self.char_rect = self.char.get_rect(topleft=(self.x, self.y))

        pygame.display.update()


class Enemy:
    def __init__(self, x, y, weight, height, animi, anima, animw, animd, fpsi, fpsa, fpsw, fpsd, screen):
        self.x = x
        self.y = y
        self.weight = weight
        self.height = height
        self.win = screen
        self.last_side = "left"
        self.walk = False
        self.attack = False
        self.death = False
        self.hp = 100
        self.idle_animation = list(map(lambda i: pygame.transform.scale(pygame.image.load(i), (weight, height)), animi))
        self.attack_animation = list(map(lambda a: pygame.transform.scale(pygame.image.load(a), (weight, height)), anima))
        self.walk_animation = list(map(lambda w: pygame.transform.scale(pygame.image.load(w), (weight, height)), animw))
        self.death_animation = list(map(lambda d: pygame.transform.scale(pygame.image.load(d), (weight, height)), animd))
        self.idle_count = 0
        self.attack_count = 0
        self.walk_count = 0
        self.death_count = 0
        self.idle_fps = fpsi
        self.attack_fps = fpsa
        self.walk_fps = fpsw
        self.death_fps = fpsd
        self.idle_right = self.idle_animation
        self.idle_left = list(map(lambda i: pygame.transform.flip(i, True, False), self.idle_animation))
        self.attack_right = self.attack_animation
        self.attack_left = list(map(lambda a: pygame.transform.flip(a, True, False), self.attack_animation))
        self.walk_right = self.walk_animation
        self.walk_left = list(map(lambda w: pygame.transform.flip(w, True, False), self.walk_animation))
        self.death_right = self.death_animation
        self.death_left = list(map(lambda d: pygame.transform.flip(d, True, False), self.death_animation))
        self.col = pygame.Rect(0, 0, width, height)
        self.col.topleft = (x, y)

    def animation(self):
        if self.idle_count + 1 >= self.idle_fps:
            self.idle_count = 0
        if self.death_count + 1 >= self.death_fps:
            self.death_count = 0

        if self.death:
            if self.last_side == "right":
                self.win.blit(self.death_right[self.death_count // (self.death_fps // len(self.death_animation))], (self.x, self.y))
                self.walk_count = 0
                self.idle_count = 0
                self.death_count += 1
                self.attack_count = 0
            elif self.last_side == "left":
                self.win.blit(self.death_left[self.death_count // (self.death_fps // len(self.death_animation))], (self.x, self.y))
                self.walk_count = 0
                self.idle_count = 0
                self.death_count += 1
                self.attack_count = 0
        else:
            if self.last_side == "right":
                self.win.blit(self.idle_right[self.idle_count // (self.idle_fps // len(self.idle_animation))], (self.x, self.y))
                self.walk_count = 0
                self.idle_count += 1
                self.attack_count = 0
            elif self.last_side == "left":
                self.win.blit(self.idle_left[self.idle_count // (self.idle_fps // len(self.idle_animation))], (self.x, self.y))
                self.walk_count = 0
                self.idle_count += 1
                self.attack_count = 0
        self.col.topleft = (self.x, self.y)


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
bg = pygame.image.load(ASSET_DIRECTORY + 'tamploin 2.0.png')
bg = pygame.transform.scale(bg, (1012, 576))
bgs = [pygame.image.load(ASSET_DIRECTORY+'tamploin 2.0.png'), pygame.image.load(ASSET_DIRECTORY + 'menu.jpg'), pygame.image.load(
    ASSET_DIRECTORY + 'instructions.png')]
width = 0
clock = pygame.time.Clock()
last = 2
run = True

char = Character(500, 360, win, 'idle_00.png', bg, 210, 210, ASSET_DIRECTORY)
game = World(win, 210, 210)


while run:
    clock.tick(56)


    pressed_attack = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and event.unicode == 'u':
            pressed_attack = True

        logging.info(event)

    if pressed_attack:
        logging.info("key pressed attack.")

        if len(char.attack_last) < 3 and char.on is False:
            char.attack_last.append(datetime.now())
        char.on = True
        if char.state == CharacterState.idle:
            char.set_state(CharacterState.attack)
        elif char.state == CharacterState.attack:
            char.set_state(CharacterState.attack2)
        elif char.state == CharacterState.attack2:
            char.set_state(CharacterState.attack3)
    else:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and char.x > char.vel - 200:
            logging.info("key pressed walk left.")

            if char.set_state(CharacterState.walk):
                char.direction = CharacterDirection.left
                char.x -= char.vel
                char.on = False

        elif keys[pygame.K_d] and char.x < 1100 - char.vel:
            logging.info("key pressed walk right.")

            if char.set_state(CharacterState.walk):
                char.x += char.vel
                char.on = False
                char.direction = CharacterDirection.right

        else:
            if char.set_state(CharacterState.idle):
                char.walk_count = 0

    char.redraw_screen()
    last_r = last + game.is_collided(char)
    char.bg = pygame.transform.scale(bgs[last_r], (1012, 576))
    last = last_r
    if game.is_collided(char) == 1:
        char.x = -60
    elif game.is_collided(char) == -1:
        char.x = 1000
    else:
        game.right_rect = pygame.Rect(1100, 315, 20, game.char_y)
        game.left_rect = pygame.Rect(-100, 315, 20, game.char_y)


pygame.quit()
