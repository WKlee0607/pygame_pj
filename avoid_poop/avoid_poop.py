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

# FPS
clock = pygame.time.Clock()

# btn class
class Btn: 
    def __init__(self,x,y,width,height,txt, onclick_fn):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.txt = txt
        self.onclick_fn = onclick_fn
        self.fill_color = {
            'normal': (255,250,200),
            'hover' : '#666666',
            'pressed' : '#333333'
        }
        self.btnSurface = pygame.Surface((self.width,self.height))
        self.btnRect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.btnSurf = pygame.font.Font(None,40).render(self.txt, True, (20,20,20))

    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.btnSurface.fill(self.fill_color['normal'])
        if self.btnRect.collidepoint(mousePos): # hover
            self.btnSurface.fill(self.fill_color['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]: # pressed
                self.btnSurface.fill(self.fill_color['pressed'])
                self.onclick_fn()
        
        self.btnSurface.blit(self.btnSurf, (
            self.btnRect.width/2 - self.btnSurf.get_rect().width/2,
            self.btnRect.height/2 - self.btnSurf.get_rect().height/2
        ))
        screen.blit(self.btnSurface, self.btnRect)

# onclick_fns
def ext_fn():
    global running
    running = False

def start_fn():
    global start_y, gaming
    start_y = False
    gaming = True

def yes_fn():
    global enemy_list, zem_list, to_x, character_x_pos, count, continue_running, gaming
    for enemy in enemy_list:
        enemy.y_pos = random.randint(-3*screen_height, -2*screen_height)
    for zem in zem_list:
        zem.y_pos = random.randint(-3*screen_height, -2*screen_height)
    to_x = 0
    character_x_pos = (screen_width-character_width)/2
    # 초기화
    count = 0
    continue_running = False
    gaming = True
    
# btn objects
start = Btn((screen_width-400)/2,(screen_height-100)/3,400,100,'Start',start_fn)
ext = Btn((screen_width-400)/2,2*(screen_height-100)/3,400,100,'Exit', ext_fn)
yes = Btn((screen_width-400)/2,(screen_height-100)/3,400,100,'Continue',yes_fn)


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
        yes.process()
        ext.process()
        screen.blit(score, ((screen_width-score.get_rect().size[0])/2,screen_height/5)) # score 그리기
    
    if start_y:
        # start 그리기
        start.process()
        ext.process()
    
    pygame.display.update()        

pygame.time.delay(1000)

pygame.quit()