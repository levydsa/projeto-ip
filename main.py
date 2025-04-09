import pygame
import random
from typing import List, Tuple
from pygame.locals import *
from sys import exit

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


class Ghost(pygame.sprite.Sprite):
    buff: int
    base_size: float
    logical_position: Vector2

    hitbox: pygame.Rect
    velocity: Vector2
    hp: int
    _distance: float

    def __init__(self, position: Vector2, distance: float = 1.0, buff: int = 0):
        self.hp = 10
        self.buff = buff
        self.logical_position = position

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

        while True:
            self.dir_x = random.randint(-2, 2)
            self.dir_y = random.randint(-2, 2)

            if self.dir_x != 0 or self.dir_y != 0:
                break

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
        pygame.mixer.init()
        self.sons = {
            "menu": pygame.mixer.Sound("sons/menu.mp3"),  # provavelmente devia estar no outro arquivo
            "flash": pygame.mixer.Sound("sons/flash.wav"),
            "estatua_morre": pygame.mixer.Sound("sons/morteestatua.wav"),
        }
        for sound in self.sons.values():
            sound.set_volume(0.1)

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
        # jéssica: mudei a fonte para ficar algo mais pixel
        font = pygame.font.Font("menuzinho/fonts/alagard.ttf", 20)
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
                        self.sons['flash'].play()
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
            new_ghosts = []

            for ghost in self.ghosts:
                if self.frame.rect.contains(ghost.hitbox):
                    ghost.hp -= (
                        5  # mudei o dano para os bichos morrerem entre 2/4 cliques
                    )
                if ghost.hp > 0:
                    new_ghosts.append(ghost)
                else:
                    self.sons['estatua_morre'].play()  # por enquanto todo fantasma vai ter o mesmo som ja q so tem um sprite
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


# adicionando o menu

#criando display do menu
pygame.init()
pygame.display.set_caption("menu")
tamanhoscreen = (960, 540)
screenprincipal = pygame.display.set_mode(tamanhoscreen)
fonte = pygame.font.Font("menuzinho/fonts/alagard.ttf", 20)

buttonplay = pygame.image.load("menuzinho/imagens/jogarbotao.png")
buttonexit = pygame.image.load("menuzinho/imagens/sairbotao.png")

#função para deixar o print de imagens mais organizado
def printimage(folder, scale, screen, position):
    image = pygame.image.load(folder)
    image = pygame.transform.scale(image, scale)
    screen.blit(image, position)

#criando a estrutura do botão
class button:
    def __init__(self, x, y, image, scale):
        self.altura = image.get_height()
        self.compri = image.get_width()
        self.image = pygame.transform.scale(
            image, (int(self.compri * scale), int(self.altura * scale))
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicou = False

    def draw(self):  # colocar botão na tela
        action = False
        mouse = pygame.mouse.get_pos() #tracking do mouse. se passar por cima da área do botão e clicar, irá entrar no if
        if self.rect.collidepoint(mouse):
            # o 0 é button esquerdo do mouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicou is False:
                self.clicou = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicou = False
        screenprincipal.blit(self.image, (self.rect.x, self.rect.y))
        return action


def menu_principal():
    botaplay = button(160, 210, buttonplay, 0.65)
    botaexit = button(160, 310, buttonexit, 0.65)
    while True:
        screenprincipal.fill("black")
        printimage(
            "menuzinho/imagens/fundomenu.png", tamanhoscreen, screenprincipal, (0, 0)
        )
        printimage(
            "menuzinho/imagens/detalhecantos.png",
            tamanhoscreen,
            screenprincipal,
            (0, 0),
        )
        printimage(
            "menuzinho/imagens/título provisório.png",
            (512, 161),
            screenprincipal,
            (10, 35),
        )
        if botaplay.draw():
            pygame.quit()
            game = Game()
            game.run()
            exit()
        if botaexit.draw():
            pygame.quit()
            exit()

        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
        pygame.display.update()

# aqui termina o menu

if __name__ == "__main__":
    menu_principal()
