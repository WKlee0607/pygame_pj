import pygame, sys
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_btns
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load
from settings import *

from support import *
from menu import Menu

class Editor:
    def __init__(self, land_tiles):
        # main set_up
        self.screen = pygame.display.get_surface() # Get a reference to the currently set display surface(현재 설정된 화면 표시면에 대한 참조 가져오기)
        self.canvas_data = {}

        # imports 
        self.land_tiles = land_tiles # dict or list형식
        self.imprt()

        # navigation
        self.origin = vector() # 2D Vector (2차원 벡터)
        self.pan_active = False
        self.pan_offset = vector()

        # support lines
        self.support_line_surf = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT)) # 이 surface에다가 lines를 그림(보조 배경 같은 느낌)
        self.support_line_surf.set_colorkey('green') # 해당 surface에서 color_key에 해당하는 색만 지움.
        self.support_line_surf.set_alpha(30) # 0~255의 값 중, 해당 surface의 명도(?) opacity정해주는 것인듯 -> lines grid가 연하게 보이도록 함.

        # selection
        self.selection_index = 2 # selection_index : settings의 2~18번까지의 수 ,default : 2
        self.last_selected_cell = None

        # menu
        self.menu = Menu()

    # support
    def get_current_cell(self):
        distance_to_origin = vector(mouse_pos()) - self.origin
        
        if distance_to_origin.x > 0:
            col = int(distance_to_origin.x/TILE_SIZE)
        else:
            col = int(distance_to_origin.x/TILE_SIZE) - 1

        if distance_to_origin.y > 0:
            row = int(distance_to_origin.y/TILE_SIZE)
        else:
            row = int(distance_to_origin.y/TILE_SIZE) - 1

        return col, row

    def check_neighbors(self, cell_pos):

        # create a local cluster
        cluster_size = 3
        local_cluster = [(cell_pos[0] + col - int(cluster_size/2), cell_pos[1] + row - int(cluster_size/2))
            for col in range(cluster_size) 
            for row in range(cluster_size)
        ]

        # check_neighbors
        for cell in local_cluster:
            if cell in self.canvas_data:
                self.canvas_data[cell].terrain_neighbors = [] # 한 개 설치할 때마다 업데이트.
                self.canvas_data[cell].water_on_top = False
                for name, side in NEIGHBOR_DIRECTIONS.items():
                    neighbor_cell = (cell[0] + side[0], cell[1] + side[1]) # local cluster(설치 블럭 포함, 중심 9개 블럭)에 대한 주변 블럭 체크 후 추가. -> 총 16개 블럭에 대한 조사를 하는 것임.

                    if neighbor_cell in self.canvas_data:
                    # water top neighbor -> water on top
                    # water in the current tile
                    # and another water tile on top
                        if self.canvas_data[neighbor_cell].has_water and self.canvas_data[cell].has_water and name == 'A': # cell이 물 type이면서 neighbor water가 A위치(cell 바로 위)에 위치할 경우
                            self.canvas_data[cell].water_on_top = True

                    # terrain neighbors 
                        if self.canvas_data[neighbor_cell].has_terrain: # 그 주위 블럭이 has_terrain일 경우.
                            self.canvas_data[cell].terrain_neighbors.append(name) # 어차피 그림은 terrain_neighbors를 참조하여 draw level에서 그려짐. 추가만 하면됨.
                            # neighbors에도 terrain_neighbors 리스트 추가해야 되는 거 아닌가? -> 아, 어차피 neighbors 바로 옆에 블럭 그리면 그 블럭도 이 함수에 의해 업데이트 됨.

    def imprt(self):
        self.water_bottom = load(os.path.join(GRAPHICS_PATH, 'terrain/water/water_bottom.png'))

        # animations
        self.animations = {3 : {'frame index' : 0, 'frames' : ['surfaces'], 'length': 3}}
        for key, value in EDITOR_DATA.items():
            if value['graphics']:
                graphics = import_folder(value['graphics'])
                self.animations[key] = {
                    'frame index' : 0,
                    'frames' : graphics, # 사진들 총 집함. list형식
                    'length' : len(graphics)
                }
        print(self.animations)

    def animation_update(self, dt):
        for value in self.animations.values():
            value['frame index'] += ANIMATION_SPEED * dt # 0.2, 0.4, ... 실수 형태임
            if value['frame index'] >= value['length']:
                value['frame index'] = 0

    # input
    def event_loop(self): # editor와 settings에서만 loop를 돌려줄 것임. main제외.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)
            self.canvas_add()
 
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

    def selection_hotkeys(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.selection_index += 1
            if event.key == pygame.K_LEFT:
                self.selection_index -= 1
        self.selection_index = max(2, min(self.selection_index , 18)) # selection idx의 범위 2~18로 정해주기

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_pos()):
            self.selection_index = self.menu.click(mouse_pos(), mouse_btns()) # 위치랑 누른 유형 넘겨줌.

    def canvas_add(self):
        # pressed Left
        if mouse_btns()[0] and not self.menu.rect.collidepoint(mouse_pos()):
            current_cell = self.get_current_cell() # return col_idx, row_idx 
            
            if current_cell != self.last_selected_cell:

                if current_cell in self.canvas_data:
                    self.canvas_data[current_cell].add_id(self.selection_index) # 이건 이후에 블럭 삭제할 때 쓰일 듯?
                else:
                    self.canvas_data[current_cell] = CanvasTile(self.selection_index) # canvas_data에 없으면 추가해줌.
                self.check_neighbors(current_cell)
                self.last_selected_cell = current_cell

    # drawing
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

    def draw_level(self):
        for cell_pos, tile in self.canvas_data.items():
            pos = self.origin + vector(cell_pos) * TILE_SIZE
            
            # water
            if tile.has_water:
                if tile.water_on_top:
                    self.screen.blit(self.water_bottom, pos)
                else:
                    frames = self.animations[3]['frames'] # animation
                    index = int(self.animations[3]['frame index'])
                    surf = frames[index]
                    self.screen.blit(surf, pos)

            if tile.has_terrain:
                terrain_string = ''.join(tile.terrain_neighbors)
                terrain_style = terrain_string if terrain_string in self.land_tiles else 'X'
                self.screen.blit(self.land_tiles[terrain_style], pos)

            # coins 
            if tile.coin:
                test_surf = pygame.Surface((TILE_SIZE,TILE_SIZE))
                test_surf.fill("yellow")
                self.screen.blit(test_surf, pos)

            # enemies
            if tile.enemy:
                test_surf = pygame.Surface((TILE_SIZE,TILE_SIZE))
                test_surf.fill("black")
                self.screen.blit(test_surf, pos)

    # update
    def run(self,dt):
        self.event_loop()

        # updating
        self.animation_update(dt)

        # drawing
        self.screen.fill("gray")
        self.draw_tile_lines()
        self.draw_level()
        pygame.draw.circle(self.screen,'red', self.origin,10)
        self.menu.display(self.selection_index)
        
class CanvasTile:
    def __init__(self, tile_id):
        
        # terrain
        self.has_terrain = False
        self.terrain_neighbors = [] # 지형 주변을 알아내어 모양을 정해주려고

        # water
        self.has_water = False
        self.water_on_top = False

        # coin
        self.coin = None # 4,5,6

        # enemy 
        self.enemy = None

        # objects 
        self.objects = []

        self.add_id(tile_id)

    def add_id(self, tile_id):
        options = {key : value['style'] for key, value in EDITOR_DATA.items()} # key = self.selection_index , value = coin 등
        match options [tile_id]:
            case 'terrain': self.has_terrain = True
            case 'water' : self.has_water = True
            case 'coin' : self.coin = tile_id
            case 'enemy' : self.enemy = tile_id
