import pygame
from settings import *

from editor import Editor

class Main:
    def __init__(self):
        # print("init") # 함수 호출시 자동으로 init()실행
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.editor = Editor()

    def run(self):
        while True:
            dt = self.clock.tick() / 1000

            self.editor.run(dt) # event_loop 등 담김.
            pygame.display.update()


if __name__ == '__main__': # 현재 스크립트 파일이 시작 프로그램 시작 파일일 경우. 즉, 여기서 파일을 실행할 경우.
    # 만약 여기서 실행 안하면 __name__ : main (파일 이름)
    # 여기서 실행하면 __name__ : __main__ (시작 파일이란 뜻)
    main = Main()
    main.run()
                    
        
