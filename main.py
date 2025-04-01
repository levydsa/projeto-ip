import pygame
import random
from typing import List, Tuple

PLAYER_RADIUS = 50

FRAME_ACTIVE_COLOR = pygame.Color("red")
FRAME_DEFAULT_COLOR = pygame.Color(100, 100, 100)
FRAME_THICKNESS = 5

GHOST_BASE_SIZE = 190

FLASH_FADE_SPEED = 500


class Vector2(pygame.Vector2):
    def multiply_componentwise(self, other: pygame.Vector2) -> pygame.Vector2:
        return Vector2(self.x * other.x, self.y * other.y)


class FlashEffect:
    alpha: int

    def __init__(self):
        self.alpha = 0

    def trigger(self) -> None:
        self.alpha = 255

    def update(self, dt: float) -> None:
        if self.alpha > 0:
            self.alpha -= FLASH_FADE_SPEED * dt
            if self.alpha < 0:
                self.alpha = 0

    def draw(self, screen: pygame.Surface) -> None:
        flash_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        flash_surface.fill((255, 255, 255, int(self.alpha)))
        screen.blit(flash_surface, (0, 0))


class Player:
    position: Vector2
    radius: int
    color: pygame.Color

    def __init__(
        self,
        position: Vector2,
        color: pygame.Color,
    ):
        self.logical_position = position.copy()
        self.position = position.copy()
        self.color = color

    def update(self, offset: Vector2) -> None:
        self.position = self.logical_position + offset

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, self.position, PLAYER_RADIUS)


class Ghost:
    base_size: float
    logical_position: Vector2

    hitbox: pygame.Rect
    velocity: Vector2
    _distance: float

    def __init__(self, position: Vector2, distance: float = 1.0):
        self.logical_position = position

        size = GHOST_BASE_SIZE / (distance**2)
        self.hitbox = pygame.Rect(
            self.logical_position,
            Vector2(size),
        )

        self.velocity = Vector2(
            random.uniform(-30, 30),
            random.uniform(-18, 18),
        )

        self.distance = distance

    @property
    def parallax_factor(self) -> float:
        return 1.0 / self.distance

    @property
    def distance(self) -> float:
        return self._distance

    @distance.setter
    def distance(self, value: float) -> None:
        self._distance = value
        size = GHOST_BASE_SIZE / (self._distance**2)
        self.hitbox.size = Vector2(size)

    def update(
        self,
        dt: float,
        offset: Vector2,
    ) -> None:
        self.distance -= 0.01 * dt
        if self.distance < 1:
            self.distance = 1

        self.logical_position += self.velocity * dt
        self.hitbox.topleft = self.logical_position + offset * self.parallax_factor

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            pygame.Color([255 / self.distance**2] * 3),
            self.hitbox,
        )


class Frame:
    rect: pygame.Rect
    color: pygame.Color
    thickness: int
    has_target: bool

    def __init__(self, width: int, height: int):
        self.rect = pygame.Rect(0, 0, width, height)
        self.color = FRAME_DEFAULT_COLOR
        self.thickness = FRAME_THICKNESS
        self.has_target = False

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        mouse_pos = Vector2(mouse_pos[0], mouse_pos[1])
        self.rect.center = mouse_pos

    def calculate_parallax_offset(
        self, screen: pygame.Rect, parallax_factor: Vector2
    ) -> Vector2:
        center_offset = Vector2(screen.center) - Vector2(self.rect.center)
        return center_offset.multiply_componentwise(parallax_factor)

    def draw(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        pygame.draw.rect(overlay, (0, 0, 0, 0), self.rect)
        screen.blit(overlay, (0, 0))

        color = FRAME_ACTIVE_COLOR if self.has_target else FRAME_DEFAULT_COLOR
        pygame.draw.rect(screen, color, self.rect, FRAME_THICKNESS)


class Game:
    screen: pygame.Surface
    clock: pygame.time.Clock
    frame: Frame
    player: Player
    ghosts: List[Ghost]
    flash: FlashEffect
    running: bool
    clicked: bool
    font: pygame.font.Font
    points: int

    def __init__(self):
        pygame.init()

        self.points = 0

        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Projeto IP")

        self.clock = pygame.time.Clock()
        self.flash = FlashEffect()
        self.frame = Frame(300, 200)
        self.player = Player(Vector2(400, 550), pygame.Color("blue"))

        self.ghosts = []
        for _ in range(100):
            self.ghosts.append(
                Ghost(
                    position=Vector2(
                        random.uniform(0, self.screen.get_width()),
                        random.uniform(0, self.screen.get_height()),
                    ),
                    distance=random.uniform(1.0, 3.0),
                )
            )

        self.ghosts.sort(
            key=lambda ghost: ghost.distance,
            reverse=True,
        )

        self.running = True
        self.clicked = False
        self.font = pygame.font.SysFont("sans", 14)

    def exibe_pontos(self, msg, tamanho, cor):
        font = pygame.font.SysFont('comicsanssms', tamanho, True, False)
        mensagem = f'{msg}'
        texto_formatado = font.render(mensagem, True, cor)
        return texto_formatado

    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        self.clicked = True
                        self.flash.trigger()

    def update(self, dt: float) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.frame.update(mouse_pos)

        PLAYER_PARALLAX_FACTOR = Vector2(0.4, 0.2)
        offset = self.frame.calculate_parallax_offset(
            self.screen.get_rect(),
            PLAYER_PARALLAX_FACTOR,
        )

        self.player.update(offset)

        frame_has_target = any(
            self.frame.rect.contains(ghost.hitbox) for ghost in self.ghosts
        )
        self.frame.has_target = frame_has_target

        if self.clicked:
            self.points += 1
            self.ghosts = [
                ghost
                for ghost in self.ghosts
                if not self.frame.rect.contains(ghost.hitbox)
            ]
            self.clicked = False
        else:
            texto_pontos = self.exibe_pontos(self.points, 40, (0, 255, 0))

        for ghost in self.ghosts:
            ghost.update(dt, offset)

        self.ghosts.sort(
            key=lambda ghost: ghost.distance,
            reverse=True,
        )

        self.flash.update(dt)

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        for rect in self.ghosts:
            rect.draw(self.screen)

        self.player.draw(self.screen)
        self.frame.draw(self.screen)
        self.flash.draw(self.screen)

        texto_pontos = self.exibe_pontos(self.points, 40, (0, 255, 0))
        self.screen.blit(texto_pontos, (self.screen.get_width() - 100, 10))

        text = self.font.render(
            f"""
FPS: {int(self.clock.get_fps())}
Player: ({self.player.position.x:.2f}, {self.player.position.y:.2f})
            """.strip(),
            True,
            (255, 255, 255),
        )
        self.screen.blit(text, (10, 10))

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick() / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
