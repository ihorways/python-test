import pygame


class Alien(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        file_path = 'graphics/' + color + '.png'
        self.image = pygame.image.load(file_path).convert_alpha()

        self.value = 100
        if color == 'green':
            self.value = 200
        elif color == 'yellow':
            self.value = 300

    def setup_rect(self, x, y):
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, direction):
        self.rect.x += direction


class Extra(pygame.sprite.Sprite):
    def __init__(self, side, screen_width, screen_hight):
        super().__init__()
        self.image = pygame.image.load('graphics/extra.png')
        self.speed = 3 if side == 'left' else -3

        x = -50 if side == 'left' else screen_width + 50
        y = screen_hight / 30
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        self.rect.x += self.speed
