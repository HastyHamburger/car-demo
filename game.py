import pygame
import math

from config import CFG

class Game(pygame.sprite.Sprite):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((CFG.screen_width, CFG.screen_height))
        pygame.sprite.Sprite.__init__(self, self.cars, self.all_sprites)

        self.px = 0
        self.py = 0
        self.vx = 0
        self.vy = 0
        self.rotation = 0

        self.car_image = self.load_image("assets/sports_car.jpg")
        self.car_rect = self.car_image.get_rect()
        self.car_rect.width = CFG.car_width
        self.car_rect.height = CFG.car_height
        self.update_car()

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

    cars = pygame.sprite.Group()
    all_sprites = pygame.sprite.RenderUpdates()

    def rotate_point(self, tx, ty, theta, x, y):
        nx = x * math.cos(theta) - y * math.sin(theta) + tx
        ny = x * math.sin(theta) + y * math.cos(theta) + ty
        return (nx, ny)

    def draw_rects(self, rects):
        for rect in rects:
            poly = []
            for map_point in self.rect_poly_map:
                poly.append(self.rotate_point(self.px, self.py, self.rotation, rect[map_point[0] + 1] * CFG.car_width, rect[map_point[1] + 1] * CFG.car_height))
            pygame.draw.polygon(self.screen, rect[0], poly)

    def update_car(self):
        self.car_rect.topleft = (self.px, self.py)
        self.car_rect.clamp_ip(self.screen.get_rect())

    def load_image(self, file):
        try:
            surface = pygame.image.load(file)
        except pygame.error:
            raise SystemExit(f"image: {file} loading error")
        return surface.convert()

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
            self.rotation += steering * math.sqrt(self.vx**2 + self.vy**2)

            self.vx += throttle * math.cos(self.rotation) * CFG.drag
            self.vy += throttle * math.sin(self.rotation) * CFG.drag

            self.vx *= CFG.drag
            self.vy *= CFG.drag

            self.px += self.vx
            self.py += self.vy

            #RENDER

            #erase previous frame
            self.screen.fill("black")

            #pygame.draw.polygon(self.screen, (255, 255, 255), (
            #    self.rotate_point(self.px, self.py, self.rotation, -CFG.car_width / 2, -CFG.car_height / 2),
            #    self.rotate_point(self.px, self.py, self.rotation, CFG.car_width / 2, -CFG.car_height / 2),
            #    self.rotate_point(self.px, self.py, self.rotation, CFG.car_width / 2, CFG.car_height / 2),
            #    self.rotate_point(self.px, self.py, self.rotation, -CFG.car_width / 2, CFG.car_height / 2)
            #))

            self.draw_rects(self.car_data)

            #put stuff on new frame
            pygame.display.flip()

            dt = clock.tick(60) / 1000

GME = Game