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

        self.health = CFG.max_health

        self.adt = 0
        self.current_moves = [0, 1, 2]
        self.attack_counter = 0

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

    current_attacks = []  #[[type, time_left, total_time, left, right, top, bottom, hit_car]]
    attack_gradients = [
        [[80, 0, 0], [255, 0, 0], [255, 100, 100]], #[start, end, flash/outline]
        [[0, 80, 0], [0, 255, 0], [100, 255, 100]],
        [[0, 0, 80], [0, 0, 255], [100, 100, 255]],
        [[80, 80, 0], [255, 255, 0], [255, 255, 150]]
    ]
    attack_length = .2

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
            if self.vx < 0:
                self.vx = 0
        elif right >= CFG.screen_width:
            self.px = -0.5 * width + CFG.screen_width
            if self.vx > 0:
                self.vx = 0
        if top <= 0:
            self.py = 0.5 * height
            if self.vy < 0:
                self.vy = 0
        elif bottom >= CFG.screen_height:
            self.py = -0.5 * height + CFG.screen_height
            if self.vy > 0:
                self.vy = 0

    def render_sped(self):
        sped_surface = self.sped_font.render(f"{round(math.sqrt(self.vx**2 + self.vy**2) * CFG.speed_convert)}mph", True, (255, 255, 255))
        self.screen.blit(sped_surface, (0,0))

    def render_attacks(self, dt):
        for attack in self.current_attacks:
            if attack[1] <= 0:
                self.current_attacks.remove(attack)
            else:
                gradient = self.attack_gradients[attack[8]]
                if attack[1] <= self.attack_length:
                    body_color = gradient[2]
                    attack[1] -= dt
                else:
                    body_color = self.lerp_color(gradient[0], gradient[1], 1 - attack[1] / attack[2])
                    attack[1] -= dt
                width, height = attack[4] - attack[3], attack[6] - attack[5]
                #body
                rect_surface = pygame.Surface((width, height))
                rect_surface.set_alpha(CFG.attack_transparency)
                rect_surface.fill(body_color)
                self.screen.blit(rect_surface, (attack[3], attack[5]))
                #outline
                pygame.draw.rect(self.screen, gradient[2], pygame.rect.Rect(attack[3], attack[5], width, height), 2)

    def lerp_color(self, color1, color2, percent):
        new_color = [
            color1[0] * (1 - percent) + color2[0] * percent,
            color1[1] * (1 - percent) + color2[1] * percent,
            color1[2] * (1 - percent) + color2[2] * percent,
        ]
        return new_color

    def resolve_attacks(self, polys):
        car_collider = polys[0]
        for i in range(len(car_collider) - 1):
            p1 = car_collider[i + 1]
            p2 = car_collider[(i + 1) % (len(car_collider) - 1) + 1]
            for attack in self.current_attacks:
                if attack[1] <= self.attack_length and not attack[7]:
                    attack_rect = pygame.rect.Rect(attack[3], attack[5], attack[4] - attack[3], attack[6] - attack[5])
                    if attack_rect.clipline(p1, p2):
                        self.health -= 1
                        attack[7] = True

    def add_attack(self, type, time, left, right, top, bottom, color):
        self.current_attacks.append([type, time, time, left, right, top, bottom, False, color])

    def render_health(self):
        left = CFG.screen_width / 2 - CFG.health_width / 2
        top = CFG.screen_height - CFG.health_height - CFG.health_offset
        pygame.draw.rect(self.screen, [150, 150, 150], pygame.rect.Rect(left, top, CFG.health_width, CFG.health_height))
        pygame.draw.rect(self.screen, [200, 0, 0], pygame.rect.Rect(
            left + CFG.health_outline,
            top + CFG.health_outline,
            CFG.health_width * self.health / CFG.max_health - CFG.health_outline * 2,
            CFG.health_height - CFG.health_outline * 2
        ))
        for i in range(self.health - 1):
            pygame.draw.rect(self.screen, [255, 120, 120], pygame.rect.Rect(
                left + (i + 1) * CFG.health_width / CFG.max_health,
                top + CFG.health_outline,
                CFG.health_outline,
                CFG.health_height - CFG.health_outline * 2))

    def move0(self, move_data):
        left = move_data[4] * CFG.screen_width / (move_data[1] - 0.5)
        right = left + CFG.screen_width / (move_data[1] - 0.5) / 2
        self.add_attack("rect", 2, move_data[4] * CFG.screen_width / (move_data[1] - 0.5), right, 0, CFG.screen_height, 3)

    def move1(self, move_data):
        top = move_data[4] * CFG.screen_height / (move_data[1] - 0.5)
        bottom = top + CFG.screen_height / (move_data[1] - 0.5) / 2
        self.add_attack("rect", 2, 0, CFG.screen_width, move_data[4] * CFG.screen_height / (move_data[1] - 0.5), bottom, 3)

    def move2(self, move_data):
        attack_index, iterations = move_data[4], move_data[1]
        size = .9
        width = CFG.screen_width / iterations * size
        if attack_index % 2 == 0:
            top = CFG.screen_height * .1
        else:
            top = CFG.screen_height * .9 - width
        left = attack_index * width / size
        self.add_attack("rect", 2, left, left + width, top, top + width, 1)

    move_data = [
        [move0, 3, .5, 0, 0], #[function, iterations, interval, time since started, times called]
        [move1, 2, 1, 0, 0],
        [move2, 5, 1, 0, 0]
    ]

    def run_attacks(self, dt):
        for i, attack_index in enumerate(self.current_moves):
            # noinspection PyTypeHints,PyArgumentList
            move_data = self.move_data[attack_index]
            move_data[3] += dt
            if move_data[3] >= move_data[4] * move_data[2]:
                move_data[0](self, move_data)
                move_data[4] += 1
            if move_data[4] == move_data[1]:
                self.current_moves.pop(i)

    def main(self):
        clock = pygame.time.Clock()
        running = True
        dt = 0

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

            polys = self.rotate_rects(self.car_data)
            self.resolve_wall_collision(polys)
            polys = self.rotate_rects(self.car_data)

            self.run_attacks(dt)
            self.resolve_attacks(polys)

            #RENDER
            #erase previous frame
            self.screen.fill("black")

            #draw all bounding boxes for attacks
            self.render_attacks(dt)

            #draw speedometer
            self.render_sped()

            self.render_health()

            #draw car
            self.draw_rects(polys)

            #put stuff on new frame
            pygame.display.update()

            dt = clock.tick(60) / 1000
            self.adt += dt

GME = Game