import pygame
from datetime import datetime
pygame.init()


class Character:
    def __init__(self, x, y, screen, ch, back, weight, height):
        self.char = pygame.transform.scale(pygame.image.load(ch), (weight, height))
        self.count = 0
        self.delta = 0
        self.on = False
        a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21 = \
            pygame.transform.scale(pygame.image.load('attack_00.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_01.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_02.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_03.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_04.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_05.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_06.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_07.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_08.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_09.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_10.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_11.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_12.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_13.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_14.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_15.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_16.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_17.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_18.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_19.png'), (weight, height)), \
            pygame.transform.scale(pygame.image.load('attack_20.png'), (weight, height))
        attack_animation = [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21]
        self.attack_right = attack_animation
        self.attack_left = list(map(lambda a: pygame.transform.flip(a, True, False), attack_animation))
        i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15 =\
            pygame.transform.scale(pygame.image.load('idle_00.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_01.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_02.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_03.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_04.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_05.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_06.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_07.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_08.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_09.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_10.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_11.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_12.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_13.png'), (weight, height)),\
        pygame.transform.scale(pygame.image.load('idle_14.png'), (weight, height)),
        idle_animation = [i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15]
        self.idle_right = idle_animation
        self.idle_left = list(map(lambda i: pygame.transform.flip(i, True, False), idle_animation))
        self.mirror_char = pygame.transform.flip(self.char, True, False)
        self.x = x
        self.y = y
        self.walk_count = 0
        self.second = False
        self.third = False
        self.idle_count = 0
        self.last_key = "right"
        self.char_rect = self.char.get_rect(topleft=(x, y))
        self.win = screen
        self.left = False
        self.right = False
        self.attack = False
        self.attack_last = []
        self.attack_count = 0
        self.vel = 5
        self.bg = back
        self.torf = False
        self.last_attack = None
        r1, r2, r3, r4, r5, r6, r7, r8 = pygame.transform.scale(pygame.image.load('run_0.png'),
                                                                (weight, height)), pygame.transform.scale(
            pygame.image.load('run_1.png'), (weight, height)), \
                                         pygame.transform.scale(pygame.image.load('run_2.png'),
                                                                (weight, height)), pygame.transform.scale(
            pygame.image.load('run_3.png'), (weight, height)), \
                                         pygame.transform.scale(pygame.image.load('run_4.png'),
                                                                (weight, height)), pygame.transform.scale(
            pygame.image.load('run_5.png'), (weight, height)), \
                                         pygame.transform.scale(pygame.image.load('run_6.png'),
                                                                (weight, height)), pygame.transform.scale(
            pygame.image.load('run_7.png'), (weight, height))
        run_animation = [r1, r2, r3, r4, r5, r6, r7, r8]
        self.walk_right = run_animation
        self.time = 0.67
        self.walk_left = list(map(lambda r: pygame.transform.flip(r, True, False), run_animation))

    def redraw_screen(self):
        self.win.blit(self.bg, (0, 0))
        if self.walk_count + 1 >= 40:
            self.walk_count = 0
        if self.idle_count + 1 >= 60:
            self.idle_count = 0
        if self.attack_count + 1 >= 105:
            self.attack_last = []
            self.count = 0
            self.attack_count = 0
            self.attack = False
            self.vel = 5

        if self.attack:
            if len(self.attack_last) == 1:
                self.time = 0.67
                self.vel = 0
                self.last_attack = self.attack_last[0]
            elif len(self.attack_last) == 2:
                self.last_attack = self.attack_last[1]
                self.time = 0.916
                self.second = True
            elif len(self.attack_last) == 3:
                self.time = 1.5
                self.last_attack = self.attack_last[2]
                self.third = True
            if (datetime.now() - self.last_attack).seconds + (datetime.now() - self.last_attack).microseconds / 1000000 < self.time:
                if self.attack_count < 45:
                    if self.last_key == "right":
                        self.win.blit(self.attack_right[self.attack_count // 5], (self.x, self.y))
                        self.attack_count += 1
                        self.idle_count = 0
                        self.walk_count = 0
                    elif self.last_key == "left":
                        self.win.blit(self.attack_left[self.attack_count // 5], (self.x, self.y))
                        self.attack_count += 1
                        self.idle_count = 0
                        self.walk_count = 0
                elif self.second is True and self.attack_count < 65:
                    if self.last_key == "right":
                        self.win.blit(self.attack_right[self.attack_count // 5], (self.x, self.y))
                        self.attack_count += 1
                        self.idle_count = 0
                        self.walk_count = 0
                    elif self.last_key == "left":
                        self.win.blit(self.attack_left[self.attack_count // 5], (self.x, self.y))
                        self.attack_count += 1
                        self.idle_count = 0
                        self.walk_count = 0
                elif self.third is True:
                    if self.last_key == "right":
                        self.win.blit(self.attack_right[self.attack_count // 5], (self.x, self.y))
                        self.attack_count += 1
                        self.idle_count = 0
                        self.walk_count = 0
                    elif self.last_key == "left":
                        self.win.blit(self.attack_left[self.attack_count // 5], (self.x, self.y))
                        self.attack_count += 1
                        self.idle_count = 0
                        self.walk_count = 0
            else:
                self.vel = 5
                self.attack_last = []
                self.count = 0
                self.attack_count = 0
                self.attack = False

        elif self.left:
            self.win.blit(self.walk_left[self.walk_count // 5], (self.x, self.y))
            self.walk_count += 1
            self.idle_count = 0
            self.last_key = "left"
            self.attack_count = 0
        elif self.right:
            self.win.blit(self.walk_right[self.walk_count // 5], (self.x, self.y))
            self.walk_count += 1
            self.last_key = "right"
            self.idle_count = 0
            self.attack_count = 0
        else:
            if self.last_key == "right":
                self.win.blit(self.idle_right[self.idle_count // 4], (self.x, self.y))
                self.walk_count = 0
                self.idle_count += 1
                self.attack_count = 0
            elif self.last_key == "left":
                self.win.blit(self.idle_left[self.idle_count // 4], (self.x, self.y))
                self.walk_count = 0
                self.idle_count += 1
                self.attack_count = 0
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


win = pygame.display.set_mode((1012, 576))
pygame.display.set_caption("The Witcher 4 Flat World")
pygame.display.set_caption("The Witcher 4 Flat World")
bg = pygame.image.load('tamploin 2.0.png')
bg = pygame.transform.scale(bg, (1012, 576))
bgs = [pygame.image.load('tamploin 2.0.png'), pygame.image.load('menu.jpg'), pygame.image.load('instructions.png')]
width = 0
clock = pygame.time.Clock()
last = 2
run = True

char = Character(500, 360, win, 'idle_00.png', bg, 210, 210)
game = World(win, 210, 210)

while run:
    clock.tick(56)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_u]:
        if len(char.attack_last) < 3 and char.on is False:
            char.attack_last.append(datetime.now())
        char.on = True
        char.attack = True
        char.right = False
        char.left = False
    elif keys[pygame.K_a] and char.x > char.vel - 200:
        char.x -= char.vel
        char.on = False
        char.left = True
        char.right = False

    elif keys[pygame.K_d] and char.x < 1100 - char.vel:
        char.x += char.vel
        char.on = False
        char.left = False
        char.right = True

    else:
        char.on = False
        char.left = False
        char.right = False
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
