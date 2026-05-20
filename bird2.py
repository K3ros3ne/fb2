import pygame
from pygame.locals import *
import random
import os

pygame.init()

hodinky = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#font = pygame.font.Font('img/Grand9K Pixel.ttf', 50)
font = pygame.font.SysFont('Grand9K Pixel', 50)
font.set_bold(True) 

white = (255, 255, 255)
outline_color = (84, 56, 71) 

# Игровые переменные
ground_scroll = 0
scroll_speed = 4
fliyng = False
game_over = False
main_menu = True  
show_highscore = False  
pipe_gap = 175
pipe_frequency = 1500 
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
current_skin = "classic"  

# Логика сохранения рекорда
highscore_file = "score.txt"
if os.path.exists(highscore_file):
    with open(highscore_file, "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0
else:
    high_score = 0
    with open(highscore_file, "w") as f:
        f.write("0")

# Загрузка базовых изображений
background = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')

# ==========================================
name_scale = 4       # Название игры
start_scale = 3      # Кнопка СТАРТ
restart_scale = 2    # Кнопка РЕСТАРТ
menu_scale = 3       # Кнопка МЕНЮ
change_scale = 3     # Кнопка Смены скина (change.png)
score_scale = 3      # Кнопка Рекордов (score.png)
back_scale = 3       # Кнопка Назад (back.png)
# ==========================================

name_original = pygame.image.load('img/name.png')
name_img = pygame.transform.scale(
    name_original, 
    (name_original.get_width() * name_scale, name_original.get_height() * name_scale)
)

button_original = pygame.image.load('img/restart.png')
button_img = pygame.transform.scale(
    button_original,
    (button_original.get_width() * restart_scale, button_original.get_height() * restart_scale)
)

start_original = pygame.image.load('img/start.png')
start_img = pygame.transform.scale(
    start_original,
    (start_original.get_width() * start_scale, start_original.get_height() * start_scale)
)

menu_original = pygame.image.load('img/menu.png')
menu_img = pygame.transform.scale(
    menu_original,
    (menu_original.get_width() * menu_scale, menu_original.get_height() * menu_scale)
)

change_original = pygame.image.load('img/change.png')
change_img = pygame.transform.scale(
    change_original,
    (change_original.get_width() * change_scale, change_original.get_height() * change_scale)
)

score_original = pygame.image.load('img/score.png')
score_img = pygame.transform.scale(
    score_original,
    (score_original.get_width() * score_scale, score_original.get_height() * score_scale)
)

back_original = pygame.image.load('img/back.png')
back_img = pygame.transform.scale(
    back_original,
    (back_original.get_width() * back_scale, back_original.get_height() * back_scale)
)

def draw_text_centered_outlined(text, font, text_col, outline_col, y):
    main_surface = font.render(text, True, text_col)
    outline_surface = font.render(text, True, outline_col)
    
    text_width = main_surface.get_width()
    x = (screen_width - text_width) // 2  
    
    thickness = 4
    
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx != 0 or dy != 0:
                screen.blit(outline_surface, (x + dx, y + dy))
                
    screen.blit(main_surface, (x, y))

def reset_game():
    global score, fliyng
    Pipe_group.empty()
    
    if main_menu:
        flappy.rect.x = -500
        flappy.rect.y = -500
    else:
        flappy.rect.x = 100
        flappy.rect.y = int(screen_height / 2)
        
    flappy.vel = 0  
    flappy.index = 0  
    flappy.image = flappy.images[flappy.index] 
    score = 0
    fliyng = False
    return score    

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        self.load_skins("classic")  
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
    
    def load_skins(self, skin_type):
        self.images.clear()
        for num in range(1, 4):
            if skin_type == "pink":
                img = pygame.image.load(f'img/pinkbird{num}.png')
            else:
                img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]

    def update(self):
        if fliyng == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
                
        if game_over == False and main_menu == False:
            if pygame.key.get_pressed()[pygame.K_SPACE] == 1 and self.clicked == False and fliyng == True:
                self.clicked = True
                self.vel = -7.5  
            if pygame.key.get_pressed()[pygame.K_SPACE] == 0:
                self.clicked = False

            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = pygame.transform.rotate(self.images[self.index], -self.vel * 3)
        
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
            
    def update(self): 
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

bird_group = pygame.sprite.Group()
Pipe_group = pygame.sprite.Group()

flappy = Bird(-500, -500)
bird_group.add(flappy)

restart_y = screen_height // 2 + 10
vertical_spacing = 20 
menu_y = restart_y + button_img.get_height() + vertical_spacing

start_x = (screen_width - start_img.get_width()) // 2
restart_x = (screen_width - button_img.get_width()) // 2
menu_x = (screen_width - menu_img.get_width()) // 2

start_button = Button(start_x, restart_y, start_img)  
restart_button = Button(restart_x, restart_y, button_img)
menu_button = Button(menu_x, menu_y, menu_img)

total_width = change_img.get_width() + score_img.get_width() + 50 
change_x = (screen_width - total_width) // 2
score_x = change_x + change_img.get_width() + 50
change_y = restart_y + start_img.get_height() + 30
score_y = change_y

change_button = Button(change_x, change_y, change_img)
score_button = Button(score_x, score_y, score_img)

back_x = (screen_width - back_img.get_width()) // 2
back_button = Button(back_x, restart_y + 100, back_img)

button_clicked = False

run = True
while run:
    hodinky.tick(fps)

    screen.blit(background, (0, 0))
    Pipe_group.draw(screen)

    if main_menu == False:
        bird_group.draw(screen)
        bird_group.update()

    screen.blit(ground_img, (ground_scroll, 768))

    if main_menu == True:
        if show_highscore == True:
            draw_text_centered_outlined("HIGHSCORE", font, white, outline_color, screen_height // 2 - 200)
            draw_text_centered_outlined(f"BEST SCORE: {high_score}", font, white, outline_color, screen_height // 2 - 50)
            
            if back_button.draw():
                if not button_clicked:
                    button_clicked = True
                    show_highscore = False 
            
            if pygame.mouse.get_pressed()[0] == 0:
                button_clicked = False
        else:
            name_x = (screen_width - name_img.get_width()) // 2
            name_y = screen_height // 2 - 200  
            screen.blit(name_img, (name_x, name_y))
            
            draw_text_centered_outlined(f"SKIN: {current_skin.upper()}", font, white, outline_color, change_y + max(change_img.get_height(), score_img.get_height()) + 15)
            
            if start_button.draw():
                main_menu = False
                flappy.rect.x = 100
                flappy.rect.y = int(screen_height / 2)
                
            if change_button.draw():
                if not button_clicked:
                    button_clicked = True
                    if current_skin == "classic":
                        current_skin = "pink"
                    else:
                        current_skin = "classic"
                    flappy.load_skins(current_skin) 

            if score_button.draw():
                if not button_clicked:
                    button_clicked = True
                    show_highscore = True 
                    
            if pygame.mouse.get_pressed()[0] == 0:
                button_clicked = False
            
    else:
        if len(Pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > Pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < Pipe_group.sprites()[0].rect.right and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > Pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False
                    if score > high_score:
                        high_score = score
                        with open(highscore_file, "w") as f:
                            f.write(str(high_score))

        draw_text_centered_outlined(str(score), font, white, outline_color, 20)

        if pygame.sprite.groupcollide(bird_group, Pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True

        if flappy.rect.bottom >= 768:
            fliyng = False
            game_over = True    

        if game_over == False and fliyng == True:
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                bottom_pipe = Pipe(screen_width, int(screen_height / 2 + pipe_height), -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2 + pipe_height), 1)
                Pipe_group.add(bottom_pipe)
                Pipe_group.add(top_pipe)
                last_pipe = time_now

            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
               ground_scroll = 0
            Pipe_group.update()

        if main_menu == False and game_over == False and fliyng == False:
            draw_text_centered_outlined("PRESS SPACE", font, white, outline_color, screen_height // 2 - 80) 

        if game_over == True:
            if restart_button.draw():
                game_over = False
                score = reset_game()
            
            if menu_button.draw():
                game_over = False
                main_menu = True 
                reset_game()  
                button_clicked = True 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if main_menu == False and game_over == False and fliyng == False:
                fliyng = True
                flappy.vel = -7.5  

    pygame.display.update()

pygame.quit()
