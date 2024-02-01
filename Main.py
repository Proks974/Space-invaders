import sys, pygame
from Player import Player	
import Obstaculo
from Alien import Alien, Extra
from random import choice, randint
from Laser import Laser

class Game:
    def __init__(self):
        #setup del jugador
        player_sprite = Player((screen_width / 2, screen_height), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)
        
        #setup vida y score
        self.lives = 3
        self.lives_surf = pygame.image.load('Imagenes/vida.png').convert_alpha()
        self.live_x_start_pos = screen_width - (self.lives_surf.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.Font('fuente/PixeloidSans-mLxMm.ttf', 20)
        

        #setup de los obstaculos
        self.forma = Obstaculo.forma
        self.tamaño_bloque = 6
        self.bloques = pygame.sprite.Group()
        self.obstaculo_cantidad = 4
        self.obstaculo_x_pos = [num * (screen_width / self.obstaculo_cantidad) for num in range(self.obstaculo_cantidad)]
        self.crear_multuiple_obst(*self.obstaculo_x_pos, x_start = screen_width/15 , y_start = 480)
        
        #setup de enemigos
        self.aliens= pygame.sprite.Group()
        self.alien_lasers= pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1
        
        #setup del extra
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400,800)
        
        #Audio
        music = pygame.mixer.Sound('Audio/music.wav')
        music.set_volume(0.2)
        music.play(loops = -1)
        
        self.laser_sound = pygame.mixer.Sound('Audio/laser.wav')
        self.laser_sound.set_volume(0.2)
        self.expl_sound = pygame.mixer.Sound('Audio/explosion.wav')
        self.expl_sound.set_volume(0.2)
        
    def crear_obst(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.forma):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x= x_start + col_index * self.tamaño_bloque + offset_x
                    y= y_start + row_index * self.tamaño_bloque
                    bloque= Obstaculo.Bloque(self.tamaño_bloque, (241, 79, 80), x, y)
                    self.bloques.add(bloque)
                    
    def crear_multuiple_obst(self,  *offset, x_start, y_start):
        for offset_x in offset:
            self.crear_obst(x_start, y_start, offset_x)
            
    def alien_setup(self, rows, cols, x_distancia = 60 , y_distancia = 48, x_offset = 70, y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distancia + x_offset
                y= row_index * y_distancia + y_offset
                
                if row_index == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)
                    
                self.aliens.add(alien_sprite)
            
    def alien_pos_check(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_mov(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_mov(2)
                
    def alien_mov(self, distancia):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distancia
                
    def alien_disparo(self):
        if self.aliens.sprites():
            random_alien= choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()
            
    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['right', 'left']), screen_width))
            self.extra_spawn_time = randint(400,800)

    def collisions_checks(self):
        
        #player laser
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                #obstacle colisions
                if pygame.sprite.spritecollide(laser, self.bloques, True):
                    laser.kill()
                #alien colisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.valor
                    laser.kill()
                    self.expl_sound.play()
                #extra colision
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    laser.kill()
                    self.score += 1000
                    
        #player laser
        if self.alien_lasers:
            for laser in self.alien_lasers:
                #obstacle colisions
                if pygame.sprite.spritecollide(laser, self.bloques, True):
                    laser.kill()
                #player colision
                #obstacle colisions
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()
                        
                    
        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.bloques, True)
                
                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def show_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.lives_surf.get_size()[0] + 10))
            screen.blit(self.lives_surf, (x,8))
            
    def display_score(self):
        score_surf = self.font.render(f'Score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft = (10,0))
        screen.blit(score_surf, score_rect)

    def victory(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('You win!', False, 'white')
            victory_rect = victory_surf.get_rect(center = (screen_width/2, screen_height/2))
            screen.blit(victory_surf, victory_rect)

    def run(self):
        #haremos update de todo, realmente nuestro framework
        self.player.update()
        self.aliens.update(self.alien_direction)
        self.alien_lasers.update()
        self.extra.update()
        
        self.alien_pos_check()
        self.extra_alien_timer()
        self.collisions_checks()
        
        
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.bloques.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.show_lives()
        self.display_score()
        self.victory()
    
class CRT:
    def __init__(self):
        self.tv = pygame.image.load('Imagenes/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (screen_width, screen_height))
    
    def create_crt_lines(self):
        line_height = 3
        line_amount = int(screen_height/ line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv, 'black', (0, y_pos), (screen_width, y_pos), 1)
        
    def draw(self):
        self.tv.set_alpha(randint(75,90))
        self.create_crt_lines()
        screen.blit(self.tv, (0,0))
        
    

if __name__ == '__main__':
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    pygame.display.set_caption('Space invaders')
    game = Game()
    crt= CRT()
    
    ALIENLASER = pygame.USEREVENT +1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit
            if event.type == ALIENLASER:
                game.alien_disparo()

        screen.fill((30,30,30))
        game.run()
        crt.draw()

        pygame.display.flip()
        clock.tick(60)
