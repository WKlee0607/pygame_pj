import os
import pygame
import random


pygame.init()

screen_width = 480
screen_height = 640
screen = pygame.display.set_mode((screen_width,screen_height))
images_path = os.path.dirname(__file__) + "/images"

background = pygame.image.load(os.path.join(images_path,"background.jpg"))

pygame.display.set_caption("Avoid Poop Game")


# Yes, No, Start
yes = pygame.image.load(os.path.join(images_path,"continue.png"))
yes_size = yes.get_rect().size
yes_width = yes_size[0]
yes_height = yes_size[1]
yes_rect = yes.get_rect()
yes_rect.left = (screen_width-yes_width)/2
yes_rect.top = (screen_height-yes_height)/3

no = pygame.image.load(os.path.join(images_path,"exit.png"))
no_size = no.get_rect().size
no_width = no_size[0]
no_height = no_size[1]
no_rect = no.get_rect()
no_rect.left = (screen_width-no_width)/2
no_rect.top = 2*(screen_height-no_height)/3

start = pygame.image.load(os.path.join(images_path,"start.png"))
start_size = start.get_rect().size
start_width = start_size[0]
start_height = start_size[1]
start_rect = start.get_rect()
start_rect.left = (screen_width-start_width)/2
start_rect.top = (screen_height-start_height)/2


# FPS
clock = pygame.time.Clock()

# character 
character = pygame.image.load(os.path.join(images_path,"dog.png"))
character_size = character.get_rect().size
character_width = character_size[0]
character_height = character_size[1]
character_x_pos = (screen_width-character_width)/2
character_y_pos = screen_height-character_height

to_x = 0

speed = 0.6

# enemy
class the_dropped:
    def __init__(self,url = os.path.join(images_path,"poop.png")):
        self.e = pygame.image.load(url)
        self.size = self.e.get_rect().size
        self.width = self.size[0]
        self.height = self.size[1]
        self.x_pos = random.randint(0, screen_width - self.width)
        self.y_pos = random.randint(-2*screen_height,-screen_height)
        self.speed = random.random()
        self.a = 0

enemy_count = 6
enemy_list = [the_dropped() for i in range(enemy_count)] # enemy 객체 7개 들음

# zem
zem_count = 5
zem_list = [the_dropped(os.path.join(images_path,"zem.png")) for i in range(zem_count)]


# font 
game_font = pygame.font.Font(None,40)
count = 0

# loop bool
running = True
start_y = True

gaming = False
continue_running = False
            
# event loop
while running:
    dt = clock.tick(30)

    # event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # character
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                to_x -= speed
            elif event.key == pygame.K_RIGHT:
                to_x += speed
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                to_x = 0
        # MouseBtnClick - MouseBtnDown
        if event.type == pygame.MOUSEBUTTONDOWN:
            # continue일 때,
            if continue_running:
                # continue 버튼 눌렀을 때
                if yes_rect.collidepoint(pygame.mouse.get_pos()) and event.button == 1:
                    print("Continue")
                    # enemy 초기화
                    for enemy in enemy_list:
                        enemy.y_pos = random.randint(-3*screen_height, -2*screen_height)
                    # zem 초기화
                    for zem in zem_list:
                        zem.y_pos = random.randint(-3*screen_height, -2*screen_height)
                    # character 초기화
                    to_x = 0
                    character_x_pos = (screen_width-character_width)/2
                    # 초기화
                    count = 0
                    continue_running = False
                    gaming = True

                # 나가기 버튼 눌렀을 때
                if no_rect.collidepoint(pygame.mouse.get_pos()) and event.button == 1:
                    print("Exit")
                    running = False
            if start_y:
                # start 여부
                if start_rect.collidepoint(pygame.mouse.get_pos()) and event.button == 1:
                    # start 버튼 눌렀을 때
                    print("Start")
                    start_y = False
                    gaming = True

    # gaming 일 때  처리
    if gaming:
        
        # 캐릭터 움직이기
        character_x_pos += to_x * dt

        if character_x_pos < 0:
            character_x_pos = 0
        elif character_x_pos > screen_width-character_width:
            character_x_pos = screen_width-character_width


        # 충돌 시 화면 처리 - enemy
        character_rect = character.get_rect()
        character_rect.left = character_x_pos
        character_rect.top = character_y_pos

        # enemy(똥) y_pos바꾸기 & 충돌처리
        for enemy in enemy_list:
            enemy.a += 0.001
            enemy.y_pos += (enemy.speed+ enemy.a) * dt 
            enemy_rect = enemy.e.get_rect()
            enemy_rect.left = enemy.x_pos
            enemy_rect.top = enemy.y_pos
            if enemy.y_pos > screen_height:
                enemy.a = 0
                enemy.x_pos = random.randint(0, screen_width - enemy.width)
                enemy.y_pos = random.randint(-screen_height,0)
                enemy.speed = random.random()
                #count += 1
            if character_rect.colliderect(enemy_rect):
                print("Collision !")
                gaming = False
                continue_running = True
            

        # zem y_pos바꾸기 & 충돌처리
        for zem in zem_list:
            # zem y_pos바꾸기
            zem.a += 0.001
            zem.y_pos += (zem.speed+ zem.a) * dt 
            if zem.y_pos > screen_height:
                zem.a = 0
                zem.x_pos = random.randint(0, screen_width - zem.width)
                zem.y_pos = random.randint(-screen_height,0)
                zem.speed = random.random()
            # 충돌 처리
            zem_rect = zem.e.get_rect()
            zem_rect.left = zem.x_pos
            zem_rect.top = zem.y_pos
            if character_rect.colliderect(zem_rect):
                zem.y_pos = screen_height + 100
                count += 1
    
    # 그리기   
    screen.blit(background,(0,0))
    
    if gaming:
        screen.blit(character,(character_x_pos,character_y_pos))
        screen.blit(game_font.render("score:" + str(count),True,(0,0,0)), (10,10)) # score 그리기
        for enemy in enemy_list:
            screen.blit(enemy.e,(enemy.x_pos,enemy.y_pos)) 
        for zem in zem_list:
            screen.blit(zem.e,(zem.x_pos,zem.y_pos)) 

    if continue_running:
        # continue_running 그리기
        score = game_font.render("score:" + str(count),True,(0,0,0))
        screen.blit(yes,(yes_rect.left,yes_rect.top))
        screen.blit(no,(no_rect.left,no_rect.top))
        screen.blit(score, ((screen_width-score.get_rect().size[0])/2,screen_height/5)) # score 그리기
    
    if start_y:
        # start 그리기
        screen.blit(start,(start_rect.left,start_rect.top))
    
    pygame.display.update()        

pygame.time.delay(1000)

pygame.quit()