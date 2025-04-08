import pygame
from pygame.locals import *
from sys import exit

import subprocess

pygame.init()
pygame.display.set_caption('menu')
tamanhoscreen = (960,540)
screenprincipal = pygame.display.set_mode(tamanhoscreen) 
fonte = pygame.font.Font('menuzinho/fonts/alagard.ttf', 20)

buttonplay = pygame.image.load('menuzinho/imagens/jogarbotao.png')
buttonexit = pygame.image.load('menuzinho/imagens/sairbotao.png')

def printext(text, fonfon, color, screen, position):
    textprint = fonfon.render(text, True, color)
    screen.blit(textprint, position)

def printimage(folder, scale, screen, position):
    image = pygame.image.load(folder)
    image = pygame.transform.scale(image, scale)
    screen.blit(image, position)

class button():
    def __init__(self, x, y, image, scale):
        self.altura = image.get_height()
        self.compri = image.get_width()
        self.image = pygame.transform.scale(image, (int(self.compri * scale), int(self.altura * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicou = False


    def draw(self):#bots botao na screen
        action = False
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            #o 0 é button esquerdo domouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicou == False:
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
        screenprincipal.fill('black')
        printimage('menuzinho/imagens/fundomenu.png', tamanhoscreen, screenprincipal, (0,0))
        printimage('menuzinho/imagens/detalhecantos.png', tamanhoscreen, screenprincipal, (0,0))
        printimage('menuzinho/imagens/título provisório.png', (512, 161), screenprincipal, (10,35))
        if botaplay.draw():
            print('iniciar jogo')
            pygame.quit() 
            subprocess.run(["python", "main.py"])  
            exit()
            #tenho que puxar main.py e executar aqui
        if botaexit.draw():
            pygame.quit()
            exit()

        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
        pygame.display.update()

menu_principal()