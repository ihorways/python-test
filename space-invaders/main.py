import pygame
import sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser


class Game:
    def __init__(self):
        # player setup
        player_sprite = Player((screen_width / 2, screen_height), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # health and score setup
        self.lives = 3
        self.live_surf = pygame.image.load('graphics/player.png').convert_alpha()
        self.live_x_end_pos = screen_width - 15
        self.score = 0
        self.font = pygame.font.Font('fonts/Pixeled.ttf', 20)

        # obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obst_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.obst_x = (screen_width - self.obst_x_positions[-1] - len(max(*self.shape, key=len)) * self.block_size) / 2
        self.obst_y = screen_height - 120
        self.create_multiple_obstacles(*self.obst_x_positions, x_start=self.obst_x, y_start=self.obst_y)

        # alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_setup(rows=1, cols=2)
        self.alien_direction = 1
        self.alien_lasers = pygame.sprite.Group()

        # extra alien setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400, 800)

        # audio setup
        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.1)
        music.play(loops=-1)
        self.laser_sound = pygame.mixer.Sound('audio/audio_laser.wav')
        self.laser_sound.set_volume(0.06)
        self.explosion_sound = pygame.mixer.Sound('audio/audio_explosion.wav')
        self.explosion_sound.set_volume(0.09)

    def create_obstacle(self, x_start, y_start, x_offset):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + x_offset + col_index * self.block_size
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (240, 80, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for x_offset in offset:
            self.create_obstacle(x_start, y_start, x_offset)

    def alien_setup(self, rows, cols):
        coef_x = 1.5
        coef_y = 1.5
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                alien_color = 'red'
                if row_index == 0:
                    alien_color = 'yellow'
                elif 0 < row_index < 3:
                    alien_color = 'green'

                alien_sprite = Alien(alien_color)

                # offset and position calculation
                alien_width = alien_sprite.image.get_width()
                alien_height = alien_sprite.image.get_height()
                x_offset = (screen_width - cols * alien_width * coef_x + alien_width / 2) / 2
                y_offset = (screen_height - rows * alien_height * coef_y + alien_height / 2) / 4
                x = x_offset + col_index * alien_width * coef_x
                y = y_offset + row_index * alien_height * coef_y

                alien_sprite.setup_rect(x, y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        for current_alien in self.aliens.sprites():
            if current_alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down()
            elif current_alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down()

    def alien_move_down(self):
        if self.aliens.sprites():
            for current_alien in self.aliens.sprites():
                current_alien.rect.y += current_alien.rect.height / 18

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, screen_height, -6)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right', 'left']), screen_width, screen_height))
            self.extra_spawn_time = randint(400, 800)

    def collision_checks(self):
        # player lasers
        if self.player.sprite.lasers:
            for current_laser in self.player.sprite.lasers:
                # obsticle collissions
                if pygame.sprite.spritecollide(current_laser, self.blocks, True):
                    current_laser.kill()

                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(current_laser, self.aliens, True)
                if aliens_hit:
                    for current_alien in aliens_hit:
                        self.score += current_alien.value
                    self.explosion_sound.play()
                    current_laser.kill()

                # extra alien collisions
                if pygame.sprite.spritecollide(current_laser, self.extra, True):
                    self.score += 500
                    self.explosion_sound.play()
                    current_laser.kill()

        # alien lasers
        if self.alien_lasers:
            for current_laser in self.alien_lasers:
                # obsticle collissions
                if pygame.sprite.spritecollide(current_laser, self.blocks, True):
                    current_laser.kill()

                # player collisions
                if pygame.sprite.spritecollide(current_laser, self.player, False):
                    current_laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()
        # aliens
        if self.aliens:
            for current_alien in self.aliens:
                # obsticle collisions
                pygame.sprite.spritecollide(current_alien, self.blocks, True)

                # player collisions
                if pygame.sprite.spritecollide(current_alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        life_surf_width = self.live_surf.get_size()[0]
        for live in range(self.lives - 1):
            x = self.live_x_end_pos - life_surf_width - live * (life_surf_width + 10)
            screen.blit(self.live_surf, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f'Score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft=(10, -5))
        screen.blit(score_surf, score_rect)

    def display_victory_msg(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('You won!', False, 'white')
            victory_rect = victory_surf.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)

    def run(self):
        self.player.update()
        self.aliens.update(self.alien_direction)
        self.extra.update()
        self.alien_lasers.update()

        self.alien_position_checker()
        self.extra_alien_timer()
        self.collision_checks()

        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.display_victory_msg()


class CRT:
    def __init__(self):
        self.tv = pygame.image.load('graphics/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (screen_width, screen_height))

    def create_crt_lines(self):
        line_height = 3
        line_amount = int(screen_height / line_height)
        for current_line in range(line_amount):
            y_pos = current_line * line_height
            pygame.draw.line(self.tv, 'black', (0, y_pos), (screen_width, y_pos), 1)

    def draw(self):
        self.tv.set_alpha(randint(55, 80))
        self.create_crt_lines()
        screen.blit(self.tv, (0, 0))


if __name__ == "__main__":
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()

        screen.fill((30, 30, 30))
        game.run()
        crt.draw()

        pygame.display.flip()
        clock.tick(60)
