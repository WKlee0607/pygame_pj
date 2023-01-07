import pygame
from settings import *
from pygame.image import load

class Menu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.create_data()
        self.create_buttons() # init 에서 실행해줌으로써 menu_rect를 만들어줌.

    def create_data(self):
        self.menu_surfs = {}
        for key, value in EDITOR_DATA.items():
            if value['menu']: # value에 menu칸이 있으면서, 
                if not value['menu'] in self.menu_surfs: # self.menu_surfs에 없다면
                    self.menu_surfs[value['menu']] = [(key,load(value['menu_surf']))] #  menu_surfs에 () 빈 tuple을 넣어라 (value['menu']가 같을 경우, 맨 초기 값만 기입됨.)-> menu_surfs : {'terrain': (), 'coin': (), 'enemy': (), 'palm fg': (), 'palm bg': ()}}
                else:
                    self.menu_surfs[value['menu']].append((key,load(value['menu_surf']))) # value['menu']가 있지만, 초기 값이 아닌 경우, 이렇게 별도로 list에 넣어줌
        # print(self.menu_surfs)

    def create_buttons(self): 
        
        # menu area general -> menu 칸 만들기
        size = 180
        margin = 6
        topleft = (WINDOW_WIDTH - (size+margin),WINDOW_HEIGHT - (size+margin))
        self.rect = pygame.Rect(topleft,(size,size)) # top, left, width, height

        # button areas 
        generic_button_rect = pygame.Rect(self.rect.topleft, (self.rect.width/2, self.rect.height/2))
        button_margin = 5
        self.tile_button_rect = generic_button_rect.copy().inflate(-button_margin,-button_margin) # pygame.Rect.inflate(x,y) : inflate => x,y만큼 Rect를 늘이거나 줄인다.
        self.coin_button_rect = generic_button_rect.move(self.rect.height/2, 0).inflate(-button_margin, -button_margin) # pygame.Rect.move(x,y) Rect를 x,y만큼 움직임.
        self.enemy_button_rect = generic_button_rect.move(self.rect.height/2, self.rect.width/2).inflate(-button_margin, -button_margin)
        self.palm_button_rect = generic_button_rect.move(0, self.rect.width/2).inflate(-button_margin, -button_margin)

        # create the buttons
        self.buttons = pygame.sprite.Group() # Group class obj -> Group에다가 obj넣는건 Buttton class를 이용.
        Button(self.tile_button_rect, self.buttons, self.menu_surfs['terrain']) # tile_btn_rect에 self.menu_surfs['terrian']에 해당하는 이미지들(data는 list에 담겨 있으며, 각 이미지는 key_idx & 이미지가 tuple형식으로 담김.)을 넣기 위함.
        Button(self.coin_button_rect, self.buttons, self.menu_surfs['coin'])
        Button(self.enemy_button_rect, self.buttons, self.menu_surfs['enemy'])
        Button(self.palm_button_rect, self.buttons, self.menu_surfs['palm fg'], self.menu_surfs['palm bg'])

    def click(self, mouse_pos, mouse_button): # 마우스 위치랑 pressed 유형 넘겨줌.
        for sprite in self.buttons:
            if sprite.rect.collidepoint(mouse_pos):
                if mouse_button[1]: # middle mouse click
                    if sprite.items['alt']:
                        sprite.main_active = not sprite.main_active  # 'alt'가 있는 아이템은 alt_item으로 변환
                if mouse_button[2]: # right click
                    sprite.switch()
                return sprite.get_id()

    def highlight_indicator(self, index):
        if EDITOR_DATA[index]['menu'] == 'terrain':
            pygame.draw.rect(self.display_surface, '#f5f1de',self.tile_button_rect.inflate(4,4),5,4)
        if EDITOR_DATA[index]['menu'] == 'coin':
            pygame.draw.rect(self.display_surface, '#f5f1de',self.coin_button_rect.inflate(4,4),5,4)
        if EDITOR_DATA[index]['menu'] == 'enemy':
            pygame.draw.rect(self.display_surface, '#f5f1de',self.enemy_button_rect.inflate(4,4),5,4)
        if EDITOR_DATA[index]['menu'] in ('palm bg', 'palm fg'):
            pygame.draw.rect(self.display_surface, '#f5f1de',self.palm_button_rect.inflate(4,4),5,4)

    def display(self, index):
        self.buttons.update()
        self.buttons.draw(self.display_surface)
        self.highlight_indicator(index)

class Button(pygame.sprite.Sprite):
    def __init__(self, rect, group, items, items_alt = None):
        super().__init__(group) # sprite.__init__(sprite group) : sprite group 는 *args형식의 arguments // self인 해당 객체가 arg로 받아온 self.buttons 그룹에 추가되도록 함.
        self.image = pygame.Surface(rect.size) # surface(표면)객체 -> 오른쪽 메뉴 칸 하나에 해당하는 rect img
        self.rect = rect # 밖에서 받아온 한 칸의 rect

        # items 
        self.items = {'main': items, 'alt': items_alt} # arg items는 list형식
        self.index = 0
        self.main_active = True
        # print(self.rect.center) -> (1138, 578)
        # print(self.rect.width, self.rect.height) -> 85, 85
    
    def get_id(self):
        return self.items['main' if self.main_active else 'alt'][self.index][0]

    def switch(self):
        self.index += 1
        self.index = 0 if self.index >= len(self.items['main' if self.main_active else 'alt']) else self.index

    def update(self): # self.buttons = pygame.sprite.Group() 여기에 
        self.image.fill('#33323d') # 메뉴 한 칸 배경 칠하기
        surf = self.items['main' if self.main_active else 'alt'][self.index][1] # pygame.img 형식
        rect = surf.get_rect(center = (self.rect.width/2, self.rect.height/2)) # surf(img)의 rect가져오기 // self.rect.center는 전체 화면 이미지에 대한 center값이 출력. 하지만 item img는 self.rect기준이므로 self.width & self.height로 구함.
        self.image.blit(surf, rect) # 배경 이미지에 item img넣기