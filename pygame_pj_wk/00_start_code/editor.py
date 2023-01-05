import pygame, sys
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_btns
from pygame.mouse import get_pos as mouse_pos
from settings import *

class Editor:
    def __init__(self):
        # main set_up
        self.screen = pygame.display.get_surface() # Get a reference to the currently set display surface(현재 설정된 화면 표시면에 대한 참조 가져오기)

        # navigation
        self.origin = vector() # 2D Vector (2차원 벡터)
        self.pan_active = False
        self.pan_offset = vector()

        # support lines
        self.support_line_surf = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT)) # 이 surface에다가 lines를 그림(보조 배경 같은 느낌)
        self.support_line_surf.set_colorkey('green') # 해당 surface에서 color_key에 해당하는 색만 지움.
        self.support_line_surf.set_alpha(30) # 0~255의 값 중, 해당 surface의 명도(?) opacity정해주는 것인듯 -> lines grid가 연하게 보이도록 함.
 
    # input
    def event_loop(self): # editor와 settings에서만 loop를 돌려줄 것임. main제외.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.pan_input(event)
 
    def pan_input(self,event):
        # middle mouse btn pressed / released
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_btns()[1]: # mouse_btns()[1] : middle mouse btn(wheel)만 고려 // mac touch pad에서는 지원 X
            # mouse_btns()[0] : 왼쪽 마우스 btn
            self.pan_active = True
            self.pan_offset = vector(mouse_pos()) - self.origin # 마우스와 붉은 원(pan)의 거리 차

        if not mouse_btns()[1]:
            self.pan_active = False
            
        # panning update
        if self.pan_active:
            self.origin = vector(mouse_pos()) - self.pan_offset # 현재 마우스 위치에서, MouseBtnDown했을 때의 마우스와 pan의 거리(정확히는 벡터 차이만큼) 차이만큼을 유지하며 pan이 이동함. -> pan이 한 번에 점프하는 걸 방지

        # mouse_wheel
        if event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LCTRL]: # 키보드의 왼쪽 ctrl 키 누를 때
            # print(event.y) mouse wheel을 위 or 아래로 이동했는지 알려줌 -> 위 : 1, 아래  : -1
                self.origin.y -= event.y * 50
            else:
                self.origin.x -= event.y * 50

    def draw_tile_lines(self): # grid tile lines
        cols = WINDOW_WIDTH//TILE_SIZE # // : 몫만 남기는 operator
        rows = WINDOW_HEIGHT//TILE_SIZE

        origin_offset = vector(
            x = self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE, # 항상 (0,0)이 됨
            y = self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE
        )

        self.support_line_surf.fill('green') # screen 위에 green screen그리고 여기다가 lines그림

        for col in range(cols + 1):
            x = origin_offset.x + col * TILE_SIZE # 두 선의 간격이 TILE_SIZE만큼 남 
            pygame.draw.line(self.support_line_surf, LINE_COLOR, start_pos=(x,0), end_pos=(x,WINDOW_HEIGHT)) # start_pos : 선을 어디서 시작할지, end_pos: 선을 어디까지 그을지 -> 마지막 화면에 걸치는 부분은 안 그림
            
        for row in range(rows+1):
            y = origin_offset.y + row * TILE_SIZE
            pygame.draw.line(self.support_line_surf, LINE_COLOR, start_pos=(0,y), end_pos=(WINDOW_WIDTH,y))

        self.screen.blit(self.support_line_surf,(0,0))

    def run(self,df):
        self.event_loop()

        # drawing
        self.screen.fill("white")
        self.draw_tile_lines()
        pygame.draw.circle(self.screen,'red', self.origin,10)