import os
GRAPHICS_MENU_PATH = os.path.join(os.path.abspath(path="graphics"),'menu')
GRAPHICS_PATH = os.path.abspath(path="graphics")
AUDIO_PATH = os.path.abspath(path="audio")

# general setup
TILE_SIZE = 64
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ANIMATION_SPEED = 8

# editor graphics 
EDITOR_DATA = {
	0: {'style': 'player', 'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': os.path.join(GRAPHICS_PATH,'player/idle_right')},
	1: {'style': 'sky',    'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': None},
	
	2: {'style': 'terrain', 'type': 'tile', 'menu': 'terrain', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'land.png'),  'preview': os.path.join(GRAPHICS_PATH,'preview/land.png'),  'graphics': None},
	3: {'style': 'water',   'type': 'tile', 'menu': 'terrain', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'water.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/water.png'), 'graphics': os.path.join(GRAPHICS_PATH,'terrain/water/animation')},
	
	4: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'gold.png'),    'preview': os.path.join(GRAPHICS_PATH,'preview/gold.png'),    'graphics': os.path.join(GRAPHICS_PATH,'items/gold')},
	5: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'silver.png'),  'preview': os.path.join(GRAPHICS_PATH,'preview/silver.png'),  'graphics': os.path.join(GRAPHICS_PATH,'items/silver')},
	6: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'diamond.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/diamond.png'), 'graphics': os.path.join(GRAPHICS_PATH,'items/diamond')},

	7:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'spikes.png'),      'preview': os.path.join(GRAPHICS_PATH,'preview/spikes.png'),      'graphics': os.path.join(GRAPHICS_PATH,'enemies/spikes')},
	8:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'tooth.png'),       'preview': os.path.join(GRAPHICS_PATH,'preview/tooth.png'),       'graphics': os.path.join(GRAPHICS_PATH,'enemies/tooth/idle')},
	9:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'shell_left.png'),  'preview': os.path.join(GRAPHICS_PATH,'preview/shell_left.png'),  'graphics': os.path.join(GRAPHICS_PATH,'enemies/shell_left/idle')},
	10: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'shell_right.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/shell_right.png'), 'graphics': os.path.join(GRAPHICS_PATH,'enemies/shell_right/idle')},
	
	11: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'small_fg.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/small_fg.png'), 'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/small_fg')},
	12: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'large_fg.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/large_fg.png'), 'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/large_fg')},
	13: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'left_fg.png'),  'preview': os.path.join(GRAPHICS_PATH,'preview/left_fg.png'),  'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/left_fg')},
	14: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'right_fg.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/right_fg.png'), 'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/right_fg')},

	15: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'small_bg.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/small_bg.png'), 'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/small_bg')},
	16: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'large_bg.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/large_bg.png'), 'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/large_bg')},
	17: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'left_bg.png'),  'preview': os.path.join(GRAPHICS_PATH,'preview/left_bg.png'),  'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/left_bg')},
	18: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': os.path.join(GRAPHICS_MENU_PATH,'right_bg.png'), 'preview': os.path.join(GRAPHICS_PATH,'preview/right_bg.png'), 'graphics': os.path.join(GRAPHICS_PATH,'terrain/palm/right_bg')},
}

NEIGHBOR_DIRECTIONS = {
	'A': (0,-1), # (열, 행)
	'B': (1,-1), # 1행 3열
	'C': (1,0),
	'D': (1,1), # self
	'E': (0,1),
	'F': (-1,1),
	'G': (-1,0),
	'H': (-1,-1)
}

LEVEL_LAYERS = {
	'clouds': 1,
	'ocean': 2,
	'bg': 3,
	'water': 4,
	'main': 5
}

# colors 
SKY_COLOR = '#ddc6a1'
SEA_COLOR = '#92a9ce'
HORIZON_COLOR = '#f5f1de'
HORIZON_TOP_COLOR = '#d1aa9d'
LINE_COLOR = 'black'