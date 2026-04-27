import pygame
import math
from config import CFG

class Game:
    def main(self):
        pygame.init()
        screen = pygame.display.set_mode((CFG.screen_width, CFG.screen_height))
        clock = pygame.time.Clock()
        running = True

        px = 0
        py = 0
        vx = 0
        vy = 0
        rotation = 0

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
            rotation += steering * math.sqrt(vx**2 + vy**2)

            vx += throttle * math.cos(rotation) * CFG.drag
            vy += throttle * math.sin(rotation) * CFG.drag

            px += vx
            py += vy

            #RENDER

            #erase previous frame
            screen.fill("black")

            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(px, py, 20, 20))
            pygame.draw.line(screen, (255, 0, 0), (px + 10, py + 10), (px + 10 + 20 * math.cos(rotation), py + 10 + 20 * math.sin(rotation)))
            pygame.draw.polygon(screen, (0, 255, 0), (
                (px - 10 * math.cos(rotation), py - 10 * math.sin(rotation)),
                (px + 10 * math.cos(rotation), py - 10 * math.sin(rotation)),
                (px + 10 * math.cos(rotation), py + 10 * math.sin(rotation)),
                (px - 10 * math.cos(rotation), py + 10 * math.sin(rotation))
            ))

            #put stuff on new frame
            pygame.display.flip()

            dt = clock.tick(60) / 1000

GME = Game