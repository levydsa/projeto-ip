import pygame
import random
from typing import List, Tuple
from pygame.locals import *
from sys import exit

VERMELHO = 0
VERDE = 1
AZUL = 2


# crio 2 variáveis globais, uma que acompanha a ultima vez que o jogador clicou, e outra que guarda o "cooldown" do clique
last_click = 0  # variavel que acompanha o ultimo clique
delay = 700  # delay da camera em milisegundos
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
        # o clique so é considerado se o ultimo clique+delay for menor que o tempo atual
        if last_click:
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
    shake_duration: float
    shake_intensity: int
    shake_offset: Vector2

    def __init__(
        self,
        position: Vector2,
        color: pygame.Color,
    ):
        self.logical_position = position.copy()
        self.position = position.copy()
        self.color = color

        self.shake_duration = 0
        self.shake_intensity = 8
        self.shake_offset = Vector2(0, 0)

    @property
    def hitbox(self) -> pygame.Rect:
        return pygame.Rect(
            self.position.x - PLAYER_RADIUS,
            self.position.y - PLAYER_RADIUS,
            PLAYER_RADIUS * 2,
            PLAYER_RADIUS * 2,
        )

    def start_shake(self, duration=0.4, intensity=8):
        self.shake_duration = duration
        self.shake_intensity = intensity

    def update(self, offset: Vector2, frame_center_x: int) -> None:
        if self.shake_duration > 0:
            self.shake_duration -= 1 / 60
            self.shake_offset.x = random.randint(
                -self.shake_intensity, self.shake_intensity
            )
            self.shake_offset.y = random.randint(
                -self.shake_intensity, self.shake_intensity
            )
            if self.shake_duration <= 0:
                self.shake_offset = Vector2(0, 0)

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

        self.position = self.logical_position + offset + self.shake_offset
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
            if buff == VERMELHO:
                self.hp = 10
                self.base_image = pygame.image.load(
                    "assets/Ghost_Normal/Normal_Red.png"
                ).convert_alpha()
            elif buff == AZUL:
                self.hp = 15
                self.base_image = pygame.image.load(
                    "assets/Ghost_Normal/Normal_Blue.png"
                ).convert_alpha()
            elif buff == VERDE:
                self.hp = 20
                self.base_image = pygame.image.load(
                    "assets/Ghost_Normal/Normal_Green.png"
                ).convert_alpha()
        if type == 1:  # Goat
            if buff == VERMELHO:
                self.hp = 10
                self.base_image = pygame.image.load(
                    "assets/Ghost_Goat/Goat_Red.png"
                ).convert_alpha()
            elif buff == AZUL:
                self.hp = 15
                self.base_image = pygame.image.load(
                    "assets/Ghost_Goat/Goat_Blue.png"
                ).convert_alpha()
            elif buff == VERDE:
                self.hp = 20
                self.base_image = pygame.image.load(
                    "assets/Ghost_Goat/Goat_Green.png"
                ).convert_alpha()
        if type == 2:  # Eye
            if buff == VERMELHO:
                self.hp = 10
                self.base_image = pygame.image.load(
                    "assets/Ghost_Eye/Eye_Red.png"
                ).convert_alpha()
            elif buff == AZUL:
                self.hp = 15
                self.base_image = pygame.image.load(
                    "assets/Ghost_Eye/Eye_Blue.png"
                ).convert_alpha()
            elif buff == VERDE:
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

        if self.player_position and not self.is_hit:
            self.distance -= 0.05 * dt
            if self.distance < 1:
                self.distance = 1.1

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
    hp: int
    particulas: pygame.sprite.Group
    last_ghost: int

    def __init__(self):
        self.last_ghost = 0
        pygame.init()
        pygame.mixer.init()

        self.points_green = 0
        self.points_blue = 0
        self.points_red = 0
        self.screen = pygame.display.set_mode((800, 600))
        self.hp = 3
        self.invulnerabilidade_timer = 1.0
        self.sons = {
            # provavelmente devia estar no outro arquivo
            "menu": pygame.mixer.Sound("sons/menu.mp3"),
            "bgm": pygame.mixer.Sound("sons/bgm.wav"),
            "flash": pygame.mixer.Sound("sons/flash.wav"),
            "estatua_morre": pygame.mixer.Sound("sons/morteestatua.wav"),
        }
        for sound in self.sons.values():
            sound.set_volume(0.1)

        self.points_green = 0
        self.points_blue = 0
        self.points_red = 0
        pygame.display.set_caption("Projeto IP")

        self.clock = pygame.time.Clock()
        self.flash = FlashEffect()
        self.frame = Frame(300, 200)
        self.player = Player(Vector2(400, 550), pygame.Color("blue"))
        self.particulas = pygame.sprite.Group()

        self.sons["bgm"].play()

        self.ghosts = []
        # diminui a quantidade de fantasmas para ficar mais vísivel
        for _ in range(3):
            self.ghosts.append(
                Ghost(
                    position=Vector2(
                        random.uniform(0, self.screen.get_width()),
                        (self.screen.get_height() / 2) - 80,
                    ),
                    distance=1.5,
                    buff=random.randint(0, 2),
                    type=random.randint(0, 2),
                    player_position=self.player.position,
                )
            )
        # diminui a quantidade de fantasmas para ficar mais vísivel

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

    def add_ghost(self, last_ghost):
        if last_ghost + 5000 < pygame.time.get_ticks():
            self.last_ghost = pygame.time.get_ticks()
            for _ in range(3):
                self.ghosts.append(
                    Ghost(
                        position=Vector2(
                            random.uniform(0, self.screen.get_width()),
                            (self.screen.get_height() / 2) - 80,
                        ),
                        distance=1.5,
                        type=random.randint(0, 2),
                        buff=random.randint(0, 2),
                    )
                )

    def exibe_hp(self, vida, tam, cor):
        font = pygame.font.Font("menuzinho/fonts/alagard.ttf", 20)
        vidas = f"{vida}"
        hp_formatado = font.render(vidas, True, cor)
        return hp_formatado

    def is_player_in_frame(self) -> bool:
        return self.frame.rect.colliderect(self.player.hitbox)

    def handle_events(self) -> None:
        global last_click
        global delay
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.MOUSEBUTTONDOWN:
                    # o evento de clicar so é considerado ser o ultimo clique + delay for menor que o tempo atual

                    if (
                        event.button == pygame.BUTTON_LEFT
                        and last_click + delay < pygame.time.get_ticks()
                    ):
                        last_click = (
                            pygame.time.get_ticks()
                        )  # atualizo o tempo do ultimo clique
                        self.clicked = True
                        self.sons["flash"].play()
                        self.flash.trigger()

    def update(self, dt: float) -> None:
        if self.invulnerabilidade_timer > 0:
            self.invulnerabilidade_timer -= dt

        if self.invulnerabilidade_timer <= 0:
            for ghost in self.ghosts:
                if ghost.hitbox.colliderect(self.player.hitbox) and self.hp > 0:
                    self.hp -= 1
                    self.invulnerabilidade_timer = 1.0
                    self.player.start_shake()
                    if self.hp <= 0:
                        self.points_blue = 0
                        self.points_green = 0
                        self.points_red = 0
                        gameover(self.screen)
                        self.running = False
                        return

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
            if self.is_player_in_frame():
                if (
                    self.points_red > 0
                    and self.points_blue > 0
                    and self.points_green > 0
                ):
                    self.points_red -= 1
                    self.points_blue -= 1
                    self.points_green -= 1

                    self.hp += 1
                    self.player.start_shake(
                        duration=0.2, intensity=4
                    )  # Small shake for healing

            # Process ghost damage
            new_ghosts = []

            for ghost in self.ghosts:
                if self.frame.rect.contains(ghost.hitbox):
                    ghost.take_damage(5)
                if ghost.hp > 0:
                    new_ghosts.append(ghost)
                else:
                    self.sons[
                        "estatua_morre"
                    ].play()  # por enquanto todo fantasma vai ter o mesmo som ja q so tem um sprite
                    for _ in range(5):
                        Particula(ghost.hitbox.center, self.particulas)

                    if ghost.buff == VERMELHO:
                        self.points_red += 1
                    elif ghost.buff == VERDE:
                        self.points_green += 1
                    elif ghost.buff == AZUL:
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

        texto_hp = self.exibe_hp(self.hp, 40, (255, 0, 0))
        self.screen.blit(texto_hp, (30, 30))

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick() / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()
            self.add_ghost(self.last_ghost)

        pygame.quit()


#tela de créditos
def créditos(screen, tamanho, font):
    while True:
        screen.fill("black")
        printimage(
            "menuzinho/imagens/fundomenu.png", tamanho, screen, (0, 0)
        )
        printimage(
            "menuzinho/imagens/detalhecantos.png",
            tamanho,
            screen,
            (0, 0),
        )
        printartext("Equipe 4", font, "grey", screen, (50,200))
        printartext("Heiji Hirakawa <hh>", font, "grey", screen, (50,240))
        printartext("Jessica Macedo <jalm2>", font, "grey", screen, (50,260))
        printartext("Levy Dorgival <ldsa>", font, "grey", screen, (50,280))
        printartext("Samira Cikarele <scsms>", font, "grey", screen, (50,300))
        printartext("Heitor Nascimento <hnd>", font, "grey", screen, (50,320))
        printartext("Vitor Nascimento <vnb>", font, "grey", screen, (50,340))
        printartext("> pressione C para voltar ao menu <", font, "grey", screen, (150,500))
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_c:
                    return
                
        pygame.display.update()
# adicionando o menu

# criando display do menu
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("menu")
fonte = pygame.font.Font("menuzinho/fonts/alagard.ttf", 20)

buttonplay = pygame.image.load("menuzinho/imagens/jogarbotao.png")
buttonexit = pygame.image.load("menuzinho/imagens/sairbotao.png")


# função para deixar o print de imagens e textos mais organizado
def printimage(folder, scale, screen, position):
    image = pygame.image.load(folder)
    image = pygame.transform.scale(image, scale)
    screen.blit(image, position)
def printartext(texto, fonfon, cor, tela, posição):
    textprint = fonfon.render(texto, True, cor)
    tela.blit(textprint, posição)

# criando a estrutura do botão
class button:
    def __init__(self, x, y, image, scale, screen):
        self.altura = image.get_height()
        self.compri = image.get_width()
        self.image = pygame.transform.scale(
            image, (int(self.compri * scale), int(self.altura * scale))
        )
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicou = False
        self.screeen = screen

    def draw(self):  # colocar botão na tela
        action = False
        mouse = pygame.mouse.get_pos()  # tracking do mouse. se passar por cima da área do botão e clicar, irá entrar no if

        if self.rect.collidepoint(mouse):
            # o 0 é button esquerdo do mouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicou is False:
                self.clicou = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicou = False
        self.screeen.blit(self.image, (self.rect.x, self.rect.y))
        return action

fonte = pygame.font.Font("menuzinho/fonts/alagard.ttf", 15)
fontemaior = pygame.font.Font("menuzinho/fonts/alagard.ttf", 20)

def menu_principal():
    tamanhoscreen = (960, 540)
    screenprincipal = pygame.display.set_mode(
        tamanhoscreen
    )  # o menu está em outra proporção
    musica = pygame.mixer.Sound("sons/menu.mp3").play()
    musica.set_volume(0.2)
    botaplay = button(160, 210, buttonplay, 0.65, screenprincipal)
    botaexit = button(160, 310, buttonexit, 0.65, screenprincipal)
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
        printartext("> pressione C para creditos <", fonte, "grey", screenprincipal, (150,500))
        if botaplay.draw():
            pygame.mixer.stop()
            game = Game()
            game.run()
        if botaexit.draw():
            pygame.quit()
            exit()

        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_c:
                    créditos(screenprincipal, tamanhoscreen, fontemaior)
                
        pygame.display.update()


# aqui termina o menu


# início do game over
buttonmenu = pygame.image.load("menuzinho/imagens/botãomenu.png")
gameover_image = pygame.image.load("menuzinho/imagens/gameover.png")


def gameover(screen):
    runnning = True
    pygame.mixer.stop()
    musica2 = pygame.mixer.Sound("sons/OMORI OST - 001 Title.wav").play()
    musica2.set_volume(0.2)
    while runnning:
        screen.fill("black")
        printimage("menuzinho/imagens/gameover.png", (512, 384), screen, (120, 40))
        botamenu = button(290, 350, buttonmenu, 0.65, screen)
        if botamenu.draw():
            pygame.mixer.stop()  # parar música
            menu_principal()  # iniciar menu principal
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
        pygame.display.update()


# fim do game over

if __name__ == "__main__":
    menu_principal()
