import pygame


class Sounds:
    pygame.init()
    boot = pygame.mixer.Sound('./sounds/success-48018.mp3')
    start = pygame.mixer.Sound('./sounds/start-13691.mp3')
    stop = pygame.mixer.Sound('./sounds/stop-13692.mp3')
