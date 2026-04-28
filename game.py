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

    cars = pygame.sprite.Group()
    all_sprites = pygame.sprite.RenderUpdates()

    def rotate_point(self, tx, ty, theta, x, y):
        nx = x * math.cos(theta) - y * math.sin(theta) + tx
        ny = x * math.sin(theta) + y * math.cos(theta) + ty
        return (nx, ny)

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

            pygame.draw.polygon(self.screen, (255, 255, 255), (
                self.rotate_point(self.px + CFG.car_width / 2, self.py + CFG.car_height / 2, self.rotation, -CFG.car_width / 2, -CFG.car_height / 2),
                self.rotate_point(self.px + CFG.car_width / 2, self.py + CFG.car_height / 2, self.rotation, CFG.car_width / 2, -CFG.car_height / 2),
                self.rotate_point(self.px + CFG.car_width / 2, self.py + CFG.car_height / 2, self.rotation, CFG.car_width / 2, CFG.car_height / 2),
                self.rotate_point(self.px + CFG.car_width / 2, self.py + CFG.car_height / 2, self.rotation, -CFG.car_width / 2, CFG.car_height / 2)
            ))

            self.update_car()
            print(self.all_sprites)
            #dirty = self.cars.draw(self.screen)
            #pygame.display.update(dirty)

            #put stuff on new frame
            pygame.display.flip()

            dt = clock.tick(60) / 1000

GME = Game