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

        self.image_right = pygame.image.load(
            "assets/Player/Player_Turned_to_Right.png"
        ).convert_alpha()
        self.image_center = pygame.image.load(
            "assets/Player/Player_Center.png"
        ).convert_alpha()
        self.image_left = pygame.image.load(
            "assets/Player/Player_Turned_to_Left.png"
        ).convert_alpha()

        self.current_image = self.image_center
        self.rect = self.current_image.get_rect(center=self.position)

        self.screen_width = pygame.display.get_surface().get_width()
        self.left_region = self.screen_width / 3
        self.right_region = 2 * self.screen_width / 3

    def update(self, offset: Vector2, frame_center_x: float) -> None:
        self.position = self.logical_position + offset
        self.rect.center = self.position

        if frame_center_x < self.left_region:
            self.current_image = self.image_left
        elif frame_center_x > self.right_region:
            self.current_image = self.image_right
        else:
            self.current_image = self.image_center

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.current_image, self.rect)


class Ghost:
    type = int
    buff: int
    base_size: float
    logical_position: Vector2

    hitbox: pygame.Rect
    velocity: Vector2
    hp: int
    _distance: float

    def __init__(
        self,
        position: Vector2,
        distance: float = 1.0,
        buff: int = 0,
        type: int = 0,
        player_position: Vector2 = None,
    ):
        super().__init__()
        self.hp = 10
        self.buff = buff
        self.logical_position = position

        if type == 0:  # Normal
            if buff == 0:
                self.hp = 10
                self.base_image = pygame.image.load(
                    "assets/Ghost_Normal/Normal_Red.png"
                ).convert_alpha()
            elif buff == 1:
                self.hp = 15
                self.base_image = pygame.image.load(
                    "assets/Ghost_Normal/Normal_Blue.png"
                ).convert_alpha()
            elif buff == 2:
                self.hp = 20
                self.base_image = pygame.image.load(
                    "assets/Ghost_Normal/Normal_Green.png"
                ).convert_alpha()
        if type == 1:  # Goat
            if buff == 0:
                self.hp = 10
                self.base_image = pygame.image.load(
                    "assets/Ghost_Goat/Goat_Red.png"
                ).convert_alpha()
            elif buff == 1:
                self.hp = 15
                self.base_image = pygame.image.load(
                    "assets/Ghost_Goat/Goat_Blue.png"
                ).convert_alpha()
            elif buff == 2:
                self.hp = 20
                self.base_image = pygame.image.load(
                    "assets/Ghost_Goat/Goat_Green.png"
                ).convert_alpha()
        if type == 2:  # Eye
            if buff == 0:
                self.hp = 10
                self.base_image = pygame.image.load(
                    "assets/Ghost_Eye/Eye_Red.png"
                ).convert_alpha()
            elif buff == 1:
                self.hp = 15
                self.base_image = pygame.image.load(
                    "assets/Ghost_Eye/Eye_Blue.png"
                ).convert_alpha()
            elif buff == 2:
                self.hp = 20
                self.base_image = pygame.image.load(
                    "assets/Ghost_Eye/Eye_Green.png"
                ).convert_alpha()

        size = GHOST_BASE_SIZE / (distance**2)
        self.hitbox = pygame.Rect(
            self.logical_position,
            Vector2(size),
        )

        self.velocity = Vector2(0, 0)  # inicia com velocidade zero
        self.base_speed = random.uniform(20, 40)  # velocidade aleatoria
        self.current_speed = self.base_speed

        self.is_hit = False
        self.hit_cooldown = 0
        self.hit_cooldown_max = 1  # tempo que fica parado ao levar dano (em segundos)

        self.distance = distance
        self.player_position = player_position

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

    def take_damage(self, amount: int):
        self.hp -= amount
        self.is_hit = True
        self.hit_cooldown = self.hit_cooldown_max
        self.current_speed = self.base_speed * 0.1

    def update(
        self,
        dt: float,
        offset: Vector2,
    ) -> None:
        if self.is_hit:
            self.hit_cooldown -= dt
            if self.hit_cooldown <= 0:
                self.is_hit = False
                self.hit_cooldown = 0

        self.distance -= 0.005 * dt
        if self.distance < 1:
            self.distance = 1

        if self.player_position and not self.is_hit:
            if self.player_position:
                direction = self.player_position - self.logical_position
                if direction.length() > 0:
                    direction = direction.normalize()

            speed_multiplier = (
                2 - self.distance
            ) * 0.5  # vai acelerando quando se aproxima da personagem
            self.current_speed = self.base_speed * speed_multiplier

            if self.is_hit:
                self.current_speed *= 0.2

            self.velocity = direction * self.current_speed
        else:
            self.velocity = Vector2(0, 0)

        self.logical_position += self.velocity * dt
        self.hitbox.topleft = self.logical_position + offset * self.parallax_factor

    def draw(self, screen: pygame.Surface) -> None:
        base = pygame.Color([255 / self.distance**2] * 3)

        size = GHOST_BASE_SIZE / (self._distance**2)
        scale_factor = size / max(self.base_image.get_size())
        self.image = pygame.transform.scale(
            self.base_image,
            (
                int(self.base_image.get_width() * scale_factor),
                int(self.base_image.get_height() * scale_factor),
            ),
        )
        self.rect = self.image.get_rect(center=self.logical_position)
        screen.blit(self.image, self.hitbox.topleft)


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


class Particula(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((4, 4))
        self.rect = self.image.get_rect(topleft=pos)
        self.color = "white"
        self.image.fill(self.color)

        self.dir_x = random.randint(-3, 3)
        self.dir_y = random.randint(-3, 3)

        if abs(self.dir_x) < 1 and abs(self.dir_y) < 1:
            if random.choice([True, False]):
                self.dir_x = random.choice([-3, 3])
            else:
                self.dir_y = random.choice([-3, 3])

    def update(self):
        self.rect.x += self.dir_x
        self.rect.y += self.dir_y


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
    # criei 1 variavel para cada tipo de fantasma
    points_green: int
    points_red: int
    points_blue: int
    particulas: pygame.sprite.Group

    def __init__(self):
        pygame.init()

        self.points_green = 0
        self.points_blue = 0
        self.points_red = 0
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Projeto IP")

        self.clock = pygame.time.Clock()
        self.flash = FlashEffect()
        self.frame = Frame(300, 200)
        self.player = Player(Vector2(400, 550), pygame.Color("blue"))
        self.particulas = pygame.sprite.Group()

        self.ghosts = []
        # diminui a quantidade de fantasmas para ficar mais vísivel
        for _ in range(50):
            self.ghosts.append(
                Ghost(
                    position=Vector2(
                        random.uniform(0, self.screen.get_width()),
                        random.uniform(0, self.screen.get_height()),
                    ),
                    distance=random.uniform(1.0, 3.0),
                    buff=random.randint(0, 2),
                    type=random.randint(0, 2),
                    player_position=self.player.position,
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
        font = pygame.font.SysFont("comicsanssms", tamanho, True, False)
        mensagem = f"{msg}"
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

        for ghost in self.ghosts:
            ghost.player_position = self.player.position

        PLAYER_PARALLAX_FACTOR = Vector2(0.4, 0.2)
        offset = self.frame.calculate_parallax_offset(
            self.screen.get_rect(),
            PLAYER_PARALLAX_FACTOR,
        )

        self.player.update(offset, self.frame.rect.centerx)

        frame_has_target = any(
            self.frame.rect.contains(ghost.hitbox) for ghost in self.ghosts
        )
        self.frame.has_target = frame_has_target

        if self.clicked:
            new_ghosts = []

            for ghost in self.ghosts:
                if self.frame.rect.contains(ghost.hitbox):
                    ghost.take_damage(5)
                if ghost.hp > 0:
                    new_ghosts.append(ghost)
                else:
                    for _ in range(5):
                        Particula(ghost.hitbox.topleft, self.particulas)
                        if ghost.buff == 0:
                            self.points_red += 1
                        elif ghost.buff == 1:
                            self.points_green += (
                                1  # fiz que os pontos so atualizem se o bicho morrer
                            )
                        elif ghost.buff == 2:
                            self.points_blue += 1
            self.ghosts = new_ghosts

            self.clicked = False

        self.particulas.update()

        for ghost in self.ghosts:
            ghost.update(dt, offset)

        self.ghosts.sort(
            key=lambda ghost: ghost.distance,
            reverse=True,
        )

        self.flash.update(dt)

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        self.particulas.draw(self.screen)

        for rect in self.ghosts:
            rect.draw(self.screen)

        self.player.draw(self.screen)
        self.frame.draw(self.screen)
        self.flash.draw(self.screen)

        # uma variavel para o os pontos de cada um

        texto_pontos_green = self.exibe_pontos(self.points_green, 40, (0, 255, 0))
        texto_pontos_blue = self.exibe_pontos(self.points_blue, 40, (0, 0, 255))
        texto_pontos_red = self.exibe_pontos(self.points_red, 40, (255, 0, 0))
        self.screen.blit(texto_pontos_green, (self.screen.get_width() - 100, 10))
        self.screen.blit(texto_pontos_blue, (self.screen.get_width() - 65, 10))
        self.screen.blit(texto_pontos_red, (self.screen.get_width() - 30, 10))

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
