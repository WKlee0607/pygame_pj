import pygame, sys
from pygame.math import Vector2 as vector

from settings import *
from support import *

from sprites import Generic, Player

class Level:
    def __init__(self, grid, switch, asset_dict): # switch :fn
        self.screen = pygame.display.get_surface()
        self.switch = switch

        # groups
        self.all_sprites = pygame.sprite.Group()

        self.build_level(grid, asset_dict)

    def build_level(self, grid, asset_dict):
        for layer_name, layer in grid.items():
            for pos, data in layer.items():
                if layer_name == 'terrain':
                    Generic(pos, asset_dict['land'][data], self.all_sprites)

                match data:
                    case 0 : self.player = Player(pos, self.all_sprites)
                    case 1 : pass # sky
                    case 4 : pass 

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("ESC")
                self.switch()

    def run(self, dt):
        self.event_loop()
        self.screen.fill(SKY_COLOR)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.screen)