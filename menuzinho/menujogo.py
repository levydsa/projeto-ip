import pygame
from pygame.locals import *
from sys import exit

pygame.init()
pygame.display.set_caption("menu")
tamanhotela = (960, 540)
telaprincipal = pygame.display.set_mode(tamanhotela)
fonte = pygame.font.Font("menuzinho/fonts/alagard.ttf", 25)

botãoimagem = pygame.image.load("menuzinho/imagens/botoes.png")


def printartext(texto, fonfon, cor, tela, posição):
    textprint = fonfon.render(texto, True, cor)
    tela.blit(textprint, posição)


def printarimagem(repositorio, escala, tela, posição):
    imagem = pygame.image.load(repositorio)
    imagem = pygame.transform.scale(imagem, escala)
    tela.blit(imagem, posição)


class botão:
    def __init__(self, x, y, imagem, texto, ajustetexto=(0, 0)):
        self.image = imagem
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.text = texto
        self.ajuste = (x + ajustetexto[0], y + ajustetexto[1])

    def draw(self):  # bots botao na tela
        printarimagem(
            "menuzinho/imagens/botoes.png", (275, 114), telaprincipal, self.ajuste
        )
        printartext(self.text, fonte, "white", telaprincipal, self.ajuste)


def menu_principal():
    botaplay = botão(200, 250, botãoimagem, "fui gongada")
    botaexit = botão(200, 300, botãoimagem, "sair")
    botacredits = botão(200, 350, botãoimagem, "créditos")
    while True:
        telaprincipal.fill("black")
        printarimagem(
            "menuzinho/imagens/fundomenu.png", tamanhotela, telaprincipal, (0, 0)
        )
        printarimagem(
            "menuzinho/imagens/detalhecantos.png", tamanhotela, telaprincipal, (0, 0)
        )
        printarimagem(
            "menuzinho/imagens/título provisório.png",
            (512, 161),
            telaprincipal,
            (-10, 25),
        )
        botaplay.draw()
        botaexit.draw()
        botacredits.draw()

        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
        pygame.display.update()


menu_principal()
