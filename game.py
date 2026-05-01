import pygame
from pygame import gfxdraw
import math

from config import CFG

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((CFG.screen_width, CFG.screen_height), pygame.SCALED, vsync=1)

        pygame.font.init()
        self.sped_font = pygame.font.SysFont("Futura", 32)

        self.px = 0
        self.py = 0
        self.vx = 0
        self.vy = 0
        self.rotation = 0

    car_data = [
        [[220, 50, 50], -.5, .5, -.5, .5], #main
        [[150, 150, 220], 0.2, .4, -.4, .4], #windshield
        [[200, 30, 30], -0.4, .1, -.4, .4], #top outline
        [[220, 50, 50], -0.35, .05, -.3, .3] #top inner
    ]

    rect_poly_map = [
        [0, 2],
        [1, 2],
        [1, 3],
        [0, 3]
    ]

    def rotate_point(self, tx, ty, theta, x, y):
        nx = x * math.cos(theta) - y * math.sin(theta) + tx
        ny = x * math.sin(theta) + y * math.cos(theta) + ty
        return nx, ny

    def rotate_rects(self, rects):
        polys = []
        for rect in rects:
            poly = [rect[0]]
            for map_point in self.rect_poly_map:
                poly.append(self.rotate_point(self.px, self.py, self.rotation, rect[map_point[0] + 1] * CFG.car_width, rect[map_point[1] + 1] * CFG.car_height))
            polys.append(poly)
        return polys

    def draw_rects(self, polys):
        for poly in polys:
            pygame.gfxdraw.filled_polygon(self.screen, poly[1:], poly[0])
            pygame.gfxdraw.aapolygon(self.screen, poly[1:], poly[0])

    def resolve_wall_collision(self, polys):
        collider_data = polys[0][1:]
        left = min([point[0] for point in collider_data])
        right = max([point[0] for point in collider_data])
        top = min([point[1] for point in collider_data])
        bottom = max([point[1] for point in collider_data])
        width = right - left
        height = bottom - top
        if left <= 0:
            self.px = 0.5 * width
        elif right >= CFG.screen_width:
            self.px = -0.5 * width + CFG.screen_width
        if top <= 0:
            self.py = 0.5 * height
        elif bottom >= CFG.screen_height:
            self.py = -0.5 * height + CFG.screen_height

    def render_sped(self):
        sped_surface = self.sped_font.render(f"{round(math.sqrt(self.vx**2 + self.vy**2) * CFG.speed_convert)}mph", True, (255, 255, 255))
        self.screen.blit(sped_surface, (0,0))

    def main(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            steering = 0
            throttle = 0
            for event in pygame.event.get():
                #game closed
                if event.type == pygame.QUIT:
                    running = False

            #keys held down
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                throttle += CFG.throttle_speed
            if keys[pygame.K_s]:
                throttle -= CFG.throttle_speed
            if keys[pygame.K_a]:
                steering -= CFG.steering_speed
            if keys[pygame.K_d]:
                steering += CFG.steering_speed

            #GAME LOGIC
            steering *= CFG.steering_centering

            self.rotation += steering * math.sqrt(self.vx**2 + self.vy**2) ** CFG.steering_exponent

            self.vx += throttle * math.cos(self.rotation) * CFG.drag
            self.vy += throttle * math.sin(self.rotation) * CFG.drag

            self.vx *= CFG.drag
            self.vy *= CFG.drag

            self.px += self.vx
            self.py += self.vy

            #RENDER

            #erase previous frame
            self.screen.fill("black")

            polys = self.rotate_rects(self.car_data)
            self.resolve_wall_collision(polys)
            polys = self.rotate_rects(self.car_data)
            self.draw_rects(polys)

            self.render_sped()

            #put stuff on new frame
            pygame.display.update()

            dt = clock.tick(60) / 1000

GME = Game