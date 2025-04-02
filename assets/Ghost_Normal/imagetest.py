import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Teste de Imagens")

red_ghost = pygame.image.load("assets/Ghost_Normal/Normal_Blue.png").convert_alpha()
blue_ghost = pygame.image.load("assets/Ghost_Normal/Normal_Red.png").convert_alpha()
green_ghost = pygame.image.load("assets/Ghost_Normal/Normal_Green.png").convert_alpha()

ghost_positions = [
    (100, 150),  
    (200, 150),
    (300, 150) 
]

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))  

    screen.blit(red_ghost, ghost_positions[0])
    screen.blit(blue_ghost, ghost_positions[1])
    screen.blit(green_ghost, ghost_positions[2])
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()