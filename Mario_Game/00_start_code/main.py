import pygame
import os
from pygame.math import Vector2 as vector

from settings import *
from support import *

from pygame.image import load

from editor import Editor
from level import Level


class Main:
    def __init__(self):
        # print("init") # 함수 호출시 자동으로 init()실행
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.imports()

        self.editor_active = True
        self.transition = Transition(self.toggle)
        self.editor = Editor(self.land_tiles, self.switch)

        # cursor // 1. cursor이미지 불러오기 2. cursor 설정(clickable area, img) 3. pygame cursor설정
        surf = load(os.path.join(GRAPHICS_PATH,"cursors/mouse.png")).convert_alpha() # convert_alpha : 이미지 로드 후, 픽셀당 투명도를 갖게 만듦.
        cursor = pygame.cursors.Cursor((0,0), surf) # clickable area: cursor의 왼쪽 상단 끝 , mouse surf 
        pygame.mouse.set_cursor(cursor)

    def imports(self):
        self.land_tiles = import_folder_dict(os.path.join(GRAPHICS_PATH,"terrain/land")) # surface list return받음 -> 모든 land이미지에 대한 img_surf

    def toggle(self):
        self.editor_active = not self.editor_active

    def switch(self, grid = None):
        self.transition.active = True
        if grid:
            self.level = Level(grid, self.switch)

    def run(self):
        while True:
            dt = self.clock.tick() / 1000

            if self.editor_active:
                self.editor.run(dt) # event_loop 등 담김.
            else:
                self.level.run(dt)
            self.transition.display(dt)
            pygame.display.update()

class Transition:
    def __init__(self, toggle):
        self.screen = pygame.display.get_surface()
        self.toggle = toggle # Fn
        self.active = False

        self.border_width = 0
        self.direction = 1
        self.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.radius = vector(self.center).magnitude() # magnitude: 크기 반환
        self.threshold = self.radius + 100 # threshold : 문턱, 한계점
    
    def display(self, dt):
        if self.active:
            self.border_width += 1000 * dt * self.direction
            if self.border_width >= self.threshold:
                self.direction = -1
                self.toggle() # editor mode on/off -> off: level.run , on: editor.run
            if self.border_width < 0:
                self.active = False
                self.border_width = 0
                self.direction = 1
            pygame.draw.circle(self.screen, 'black', self.center, self.radius, int(self.border_width))

if __name__ == '__main__': # 현재 스크립트 파일이 시작 프로그램 시작 파일일 경우. 즉, 여기서 파일을 실행할 경우.
    # 만약 여기서 실행 안하면 __name__ : main (파일 이름)
    # 여기서 실행하면 __name__ : __main__ (시작 파일이란 뜻)
    main = Main()
    main.run()
                    
        
