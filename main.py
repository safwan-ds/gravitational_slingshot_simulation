import math
import random
import pygame

from pygame.locals import *
from constants import *

pygame.init()

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption("Gravitational Simulator")

background = pygame.image.load("assets/background.png")
background = pygame.transform.scale_by(background, 0.8)

earth = pygame.image.load("assets/earth.png")
earth = pygame.transform.scale(earth, (EARTH_SIZE * 2, EARTH_SIZE * 2))

moon = pygame.image.load("assets/moon.png")
moon = pygame.transform.scale(moon, (MOON_SIZE * 2, MOON_SIZE * 2))

orbits = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)

font = pygame.sysfont.SysFont("Consolas", 30)


class Earth(pygame.sprite.Sprite):
    def __init__(self, x, y, mass):
        super().__init__()
        self.mass = mass

        self.image = earth
        self.rect = self.image.get_frect(center=(x, y))


class Moon(pygame.sprite.Sprite):
    def __init__(self, x, y, vel_x, vel_y, mass):
        super().__init__()
        self.mass = mass

        self.vel_x = vel_x * VEL_SCALE
        self.vel_y = vel_y * VEL_SCALE

        self.image = moon
        self.rect: pygame.FRect = self.image.get_frect(center=(x, y))

        self.orbit = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        self.orbit_color = pygame.color.Color(255, 0, 0)
        self.orbit_color.hsla = (random.randint(0, 360), *self.orbit_color.hsla[1:4])

    def calculate_acceleration(self, planet: Earth):
        distance = (
            math.sqrt(
                (self.rect.x - planet.rect.x) ** 2 + (self.rect.y - planet.rect.y) ** 2
            )
            * DISTANCE_SCALE
        )
        force = G * self.mass * planet.mass / distance**2
        acceleration = force * self.mass
        angle = math.atan2(planet.rect.y - self.rect.y, planet.rect.x - self.rect.x)
        acceleration_x = acceleration * math.cos(angle)
        acceleration_y = acceleration * math.sin(angle)
        self.vel_x += acceleration_x
        self.vel_y += acceleration_y

    def move(self, planet: Earth):
        if planet:
            self.calculate_acceleration(planet)

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def update(self, planet: Earth, surface: pygame.Surface):
        self.move(planet)
        pygame.draw.circle(
            self.orbit, self.orbit_color, (self.rect.centerx, self.rect.centery), 1
        )
        surface.blit(self.orbit, (0, 0))

        if (
            self.rect.centerx > SCREEN_WIDTH + 200
            or self.rect.centerx < -200
            or self.rect.centery > SCREEN_HEIGHT + 200
            or self.rect.centery < -200
        ):
            self.kill()


def main():
    running = True
    clock = pygame.time.Clock()
    earth = pygame.sprite.GroupSingle(
        Earth(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, EARTH_MASS)  # type: ignore
    )
    new_obj_pos = None
    moons = pygame.sprite.Group()

    while running:
        win.blit(background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.MOUSEBUTTONDOWN:
                    new_obj_pos = mouse_pos
                case pygame.MOUSEBUTTONUP:
                    if new_obj_pos:
                        new_obj = Moon(
                            new_obj_pos[0],
                            new_obj_pos[1],
                            mouse_pos[0] - new_obj_pos[0],
                            mouse_pos[1] - new_obj_pos[1],
                            MOON_MASS,
                        )
                        moons.add(new_obj)
                        new_obj_pos = None
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_BACKSPACE:
                            moons.empty()
                        case pygame.K_ESCAPE:
                            running = False

        if new_obj_pos:
            pygame.draw.line(win, "red", new_obj_pos, mouse_pos, 2)
            pygame.draw.circle(win, "red", new_obj_pos, MOON_SIZE)

        moons.update(earth.sprite, win)
        pygame.sprite.groupcollide(moons, earth, True, False)
        # for moon1 in moons.sprites():
        #     for moon2 in pygame.sprite.spritecollide(moon1, moons, False):
        #         if moon1 != moon2:
        #             moon1.kill()
        #             moon2.kill()

        moons.draw(win)
        earth.draw(win)
        win.blit(font.render(f"Moons: {len(moons)}", True, "white"), (10, 10))
        win.blit(
            font.render(f"FPS: {clock.get_fps():.1f}", True, "white"),
            (10, 50),
        )
        clock.tick(FPS)
        pygame.display.flip()

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()
