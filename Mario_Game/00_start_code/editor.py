import pygame, sys
from pygame.math import Vector2 as vector
from pygame.mouse import get_pressed as mouse_btns
from pygame.mouse import get_pos as mouse_pos
from pygame.image import load

from settings import *
from support import *

from menu import Menu
from timer import Timer

from random import choice, randint

class Editor:
    def __init__(self, land_tiles):
        # main set_up
        self.screen = pygame.display.get_surface() # Get a reference to the currently set display surface(현재 설정된 화면 표시면에 대한 참조 가져오기)
        self.canvas_data = {}

        # imports 
        self.land_tiles = land_tiles # dict or list형식
        self.imprt()

        # clouds
        self.current_clouds = []
        self.cloud_surf = import_folder(GRAPHICS_PATH + '/clouds')
        self.cloud_timer = pygame.USEREVENT + 1 
        pygame.time.set_timer(self.cloud_timer, 2000) # 2초마다 cloud_timer event에 signal을 보냄. -> 2초마다 create_clouds 실행
        self.startup_clouds()

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

        # objects
        self.canvas_objects = pygame.sprite.Group()
        self.object_drag_active = False
        self.object_timer = Timer(400)

        # Player
        CanvasObject(
            pos = (200, WINDOW_HEIGHT/2), 
            frames = self.animations[0]['frames'], 
            tile_id = 0, 
            origin = self.origin, 
            group = self.canvas_objects
        )

        # sky
        # pos = middle of window
        self.sky_handle = CanvasObject(
            pos = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2),
            frames = [self.sky_handle_surf],
            tile_id= 1,
            origin=self.origin,
            group=self.canvas_objects
        )

    # support
    def get_current_cell(self, obj = None):
        distance_to_origin = vector(mouse_pos()) - self.origin if not obj else vector(obj.distance_to_origin) - self.origin
        
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
        self.water_bottom = load(os.path.join(GRAPHICS_PATH, 'terrain/water/water_bottom.png')).convert_alpha()
        self.sky_handle_surf = load(os.path.join(GRAPHICS_PATH, 'cursors/handle.png')).convert_alpha()

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
        
        # preview
        self.preview_surfs = {key : load(value['preview']) for key, value in EDITOR_DATA.items() if value['preview']}


    def animation_update(self, dt):
        for value in self.animations.values():
            value['frame index'] += ANIMATION_SPEED * dt # 0.2, 0.4, ... 실수 형태임
            if value['frame index'] >= value['length']:
                value['frame index'] = 0

    def mouse_on_object(self):
        for sprite in self.canvas_objects:
            if sprite.rect.collidepoint(mouse_pos()):
                return sprite

    def create_grid(self):

        # add objects to the tiles
        for tile in self.canvas_data.values():
            tile.objects = []
        for obj in self.canvas_objects:
            current_cell = self.get_current_cell(obj)
            offset = obj.distance_to_origin - (vector(current_cell) * TILE_SIZE)
            
            if current_cell in self.canvas_data: # tile exists already
                self.canvas_data[current_cell].add_id(obj.tile_id, offset)
            else: # no tiles exists yet
                self.canvas_data[current_cell] = CanvasTile(obj.tile_id, offset)

        # create an empty grid
        layers = {
            'water': {},
            'bg palms' : {},
            'terrain' : {},
            'enemies' : {},
            'coins' : {},
            'fg objects' : {},
        }

        # create a grid - character & level controller
        # lefttop - grid offset
        left = sorted(self.canvas_data.keys(), key = lambda tile: tile[0])[0][0]  # x 값들을 모아놓음
        top = sorted(self.canvas_data.keys(), key = lambda tile: tile[1])[0][1] 

        # fill the grid
        for tile_pos, tile in self.canvas_data.items():
            row_adjusted = tile_pos[1] - top
            col_adjusted = tile_pos[0] - left
            x = col_adjusted * TILE_SIZE
            y = row_adjusted * TILE_SIZE

            if tile.has_water:
                layers['water'][(x,y)] = tile.get_water()

            if tile.has_terrain:
                layers['terrain'][(x,y)] = tile.get_terrain() if tile.get_terrain() in self.land_tiles else 'X'

            if tile.coin:
                layers['coins'][(x + TILE_SIZE//2 , y + TILE_SIZE//2)] = tile.coin

            if tile.enemy:
                layers['enemies'][(x,y)] = tile.enemy

            if tile.objects: # (obj, offset)
                for obj, offset in tile.objects:
                    if obj in [key for key, value in EDITOR_DATA.items() if value['style'] == 'palm_bg']: # bg palm
                        layers['bg palms'][(int(x + offset.x),int(y + offset.y))] = obj
                    else: # fg objects
                        layers['fg objects'][(int(x + offset.x),int(y + offset.y))] = obj
        
        return layers

    # input
    def event_loop(self): # editor와 settings에서만 loop를 돌려줄 것임. main제외.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: # K_RETURN : 엔터키
                print(self.create_grid())
            
            self.pan_input(event)
            self.selection_hotkeys(event)
            self.menu_click(event)
            
            self.object_drag(event)

            self.canvas_add()
            self.canvas_remove()

            self.create_clouds(event)
 
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

            for sprite in self.canvas_objects:
                sprite.pan_pos(self.origin)

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
        if mouse_btns()[0] and not self.menu.rect.collidepoint(mouse_pos()) and not self.object_drag_active:
            current_cell = self.get_current_cell() # return col_idx, row_idx 
            if EDITOR_DATA[self.selection_index]['type'] == 'tile':
            
                if current_cell != self.last_selected_cell:

                    if current_cell in self.canvas_data:
                        self.canvas_data[current_cell].add_id(self.selection_index) # 이건 이후에 블럭 삭제할 때 쓰일 듯?
                    else:
                        self.canvas_data[current_cell] = CanvasTile(self.selection_index) # canvas_data에 없으면 추가해줌.
                    self.check_neighbors(current_cell)
                    self.last_selected_cell = current_cell
            else: # object -> type: object인 것들은 canvas에 그릴 때, CanvasObject 객체로 그려줘서 위치를 이동시킬 수 있음.
                if not self.object_timer.active:
                    CanvasObject(
                        pos = mouse_pos(),
                        frames = self.animations[self.selection_index]['frames'],
                        tile_id = self.selection_index,
                        origin = self.origin,
                        group = self.canvas_objects
                    )
                    self.object_timer.activate() # 0.4초 딜레이


    def canvas_remove(self):
        if mouse_btns()[2] and not self.menu.rect.collidepoint(mouse_pos()):
            
            # delete object
            selected_object = self.mouse_on_object() # sprite(object) return
            if selected_object:
                if EDITOR_DATA[selected_object.tile_id]['style'] not in ('player', 'sky'):
                    selected_object.kill() # sprite(pygame Sprite객체)


            # delete tiles
            if self.canvas_data:
                current_cell = self.get_current_cell()
                if current_cell in self.canvas_data:
                    self.canvas_data[current_cell].remove_id(self.selection_index)

                if self.canvas_data[current_cell].is_empty:
                    del self.canvas_data[current_cell]
                self.check_neighbors(current_cell)
    
    def object_drag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and mouse_btns()[0]:
            for sprite in self.canvas_objects:
                if sprite.rect.collidepoint(mouse_pos()):
                    sprite.start_drag()
                    self.object_drag_active = True

        if event.type == pygame.MOUSEBUTTONUP and self.object_drag_active:
            for sprite in self.canvas_objects:
                if sprite.selected:
                    sprite.drag_end(self.origin) 
                    self.object_drag_active = False

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
                frames = self.animations[tile.coin]['frames']
                index = int(self.animations[tile.coin]['frame index'])
                surf = frames[index]
                rect = surf.get_rect(center = (pos.x + (TILE_SIZE)//2, pos.y + (TILE_SIZE)//2))
                self.screen.blit(surf, rect)

            # enemies
            if tile.enemy:
                frames = self.animations[tile.enemy]['frames']
                index = int(self.animations[tile.enemy]['frame index'])
                surf = frames[index]
                rect = surf.get_rect(midbottom = (pos.x + TILE_SIZE//2, pos.y + TILE_SIZE))
                self.screen.blit(surf, rect)
        self.canvas_objects.draw(self.screen) # Group에 속한 sprite는 image, rect를 가지고 있어서 바로 그려짐
        
    def preview(self):
        selected_object = self.mouse_on_object() # 마우스가 object위에 있을 때.
        if not self.menu.rect.collidepoint(mouse_pos()): # mouse가 menu에 있지 않으면서
            if selected_object:
                rect = selected_object.rect.inflate(10,10) # 10, 10만큼 늘림. New Rect return.
                color = 'black'
                width = 3
                size = 15
                
                # topleft
                pygame.draw.lines(self.screen, color, False, [(rect.left, rect.top+size), rect.topleft, (rect.left + size,rect.top)], width)
                # topright
                pygame.draw.lines(self.screen, color, False, [(rect.right-size, rect.top), rect.topright, (rect.right ,rect.top+size)], width)
                # bottomleft
                pygame.draw.lines(self.screen, color, False, [(rect.left, rect.bottom-size), rect.bottomleft, (rect.left + size,rect.bottom)], width)
                # bottomright
                pygame.draw.lines(self.screen, color, False, [(rect.right-size, rect.bottom), rect.bottomright, (rect.right,rect.bottom-size)], width)
                # draws lines around objects when hovered over
            else:
                type_dict = {key: value['type'] for key, value in EDITOR_DATA.items()}
                surf = self.preview_surfs[self.selection_index].copy()
                surf.set_alpha(200)

                # preview of the tiles 
                if type_dict[self.selection_index] == 'tile':
                    current_cell = self.get_current_cell()
                    rect = surf.get_rect(topleft = self.origin + vector(current_cell) * TILE_SIZE)

                # preview of the object
                else:
                    rect = surf.get_rect(center = mouse_pos())
                    
                self.screen.blit(surf, rect)

    def display_sky(self,dt):
        self.screen.fill(SKY_COLOR)
        y = self.sky_handle.rect.centery

        # horizon lines
        if y > 0:
            horizon_rect1 = pygame.Rect(0,y-10,WINDOW_WIDTH,10)
            horizon_rect2 = pygame.Rect(0,y-16,WINDOW_WIDTH,4)
            horizon_rect3 = pygame.Rect(0,y-20,WINDOW_WIDTH,2)
            pygame.draw.rect(self.screen, HORIZON_TOP_COLOR, horizon_rect1)
            pygame.draw.rect(self.screen, HORIZON_TOP_COLOR, horizon_rect2)
            pygame.draw.rect(self.screen, HORIZON_TOP_COLOR, horizon_rect3)
            
            self.display_clouds(dt, y)

        # sea
        # if horizon is on the screen:
        if 0 < y < WINDOW_HEIGHT:
            sea_rect = pygame.Rect(0,y,WINDOW_WIDTH,WINDOW_HEIGHT)
            pygame.draw.rect(self.screen, SEA_COLOR,sea_rect)
            pygame.draw.line(self.screen, HORIZON_COLOR, (0,y), (WINDOW_WIDTH,y), 3)
        # else: fill the entire surface with water
        if y < 0:
            self.screen.fill(SEA_COLOR)
        
    def display_clouds(self, dt, horizon_y):
        for cloud in self.current_clouds: # [{surf, pos, speed}]
            cloud['pos'][0] -= cloud['speed'] * dt
            x = cloud['pos'][0]
            y = horizon_y - cloud['pos'][1]
            self.screen.blit(cloud['surf'], (x,y))

    def create_clouds(self, event):
        if event.type == self.cloud_timer: # 공부하기
            surf = choice(self.cloud_surf)
            surf = pygame.transform.scale2x(surf) if randint(0,4) < 2 else surf

            pos = [WINDOW_WIDTH + randint(50,100),randint(0,WINDOW_HEIGHT)]
            self.current_clouds.append({'surf': surf , 'pos': pos, 'speed': randint(20,50)})

            # x pos가 -400미만이면 삭제해주도록 업데이트
            self.current_clouds = [cloud for cloud in self.current_clouds if cloud['pos'][0] > -400]

    def startup_clouds(self):
        for i in range(20):
            surf = pygame.transform.scale2x(choice(self.cloud_surf)) if randint(0,4) < 2 else choice(self.cloud_surf)
            pos = [randint(0,WINDOW_WIDTH), randint(0,WINDOW_HEIGHT)]
            self.current_clouds.append({'surf': surf , 'pos': pos, 'speed': randint(20,50)})

    # update
    def run(self,dt):
        self.event_loop()

        # updating
        self.animation_update(dt)
        self.canvas_objects.update(dt) # sprite.Group에서 함수 실행해주면 Group안에 있는 각각의 sprite에 대하여 동일한 함수 실행
        self.object_timer.update()

        # drawing
        self.screen.fill("gray")
        self.display_sky(dt)
        self.draw_tile_lines()
        self.draw_level()
        # pygame.draw.circle(self.screen,'red', self.origin,10)
        self.preview()
        self.menu.display(self.selection_index)
        
class CanvasTile:
    def __init__(self, tile_id, offset = vector()):
        
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

        self.add_id(tile_id, offset= offset)
        self.is_empty = False

    def add_id(self, tile_id, offset = vector()):
        options = {key : value['style'] for key, value in EDITOR_DATA.items()} # key = self.selection_index , value = coin 등
        match options [tile_id]:
            case 'terrain': self.has_terrain = True
            case 'water' : self.has_water = True
            case 'coin' : self.coin = tile_id
            case 'enemy' : self.enemy = tile_id
            case _ : # objects
                if (tile_id, offset) not in self.objects:
                    self.objects.append((tile_id, offset))

    def remove_id(self, tile_id):
        options = {key : value['style'] for key, value in EDITOR_DATA.items()} # key = self.selection_index , value = coin 등
        match options [tile_id]:
            case 'terrain': self.has_terrain = False
            case 'water' : self.has_water = False
            case 'coin' : self.coin = None
            case 'enemy' : self.enemy = None
        self.check_contents()

    def check_contents(self):
        if not self.has_terrain and not self.has_water and not self.coin and not self.enemy:
            self.is_empty = True

    def get_water(self):
        return 'bottom' if self.water_on_top else 'top'

    def get_terrain(self):
        return ''.join(self.terrain_neighbors)

class CanvasObject(pygame.sprite.Sprite):
    def __init__(self, pos, frames, tile_id, origin, group): # tile_id : 0,1
        super().__init__(group)
        self.tile_id = tile_id

        # animation
        self.frames = frames
        self.frame_index = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)

        # movement
        self.distance_to_origin = vector(self.rect.topleft) - origin
        self.selected = False
        self.mouse_offset = vector()

    def start_drag(self):
        self.selected = True
        self.mouse_offset = vector(mouse_pos()) - vector(self.rect.topleft)

    def drag(self):
        if self.selected:
            self.rect.topleft = mouse_pos() - self.mouse_offset

    def drag_end(self, origin):
        self.selected = False
        self.distance_to_origin = vector(self.rect.topleft) - origin # 캐릭터 움직이고, L_ctrl로 origin움직이고, pressed[1]로 움직이면 에러 발생 -> 순간이동함.


    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.frame_index = 0 if self.frame_index >= len(self.frames) else self.frame_index
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

    def pan_pos(self, origin):
        self.rect.topleft = origin + self.distance_to_origin

    def update(self, dt):
        self.animate(dt)
        self.drag()