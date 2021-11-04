import pygame
import sys
import random
import math
from os import path

WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

HS_FILE = "highscore.txt"

class Game:
    screen = None
    aliens = []
    rockets = []
    alien_rockets = []
    bunker_list = []
    mat_aliens = [[0] * 500 for _ in range(500)]
    lost = False
    score = 0

    def __init__(self, width, height):

        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.load_data()
        done = False

        hero = Hero(self, width / 2, height - 20)
        generator = Generator(self)
        rocket = None

        while not done:

            if self.score > self.highscore:
                self.highscore = self.score
                with open(path.join(self.dir, HS_FILE), 'w') as f:
                    f.write(str(self.score))

            if len(self.aliens) == 0:
                # self.displayText("VICTORY")
                self.displayText("VICTORY")
                self.displayScore("SCORE : " + str(self.score))
                self.displayHighscore("HIGHSCORE : " + str(highscore))

            hero.checkCollision(self)
            if self.lost == True:
                self.displayText("YOU DIED")
                self.displayScore("SCORE : " + str(self.score))
                self.displayHighscore("HIGHSCORE : " + str(self.highscore))

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_a]:
                hero.x -= 2 if hero.x > 20 else 0
            elif pressed[pygame.K_d]:
                hero.x += 2 if hero.x < width - 20 else 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.lost:
                    self.rockets.append(Rocket(self, hero.x, hero.y))
            


            pygame.display.flip()
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))

            for alien in self.aliens:
                alien.draw()
                alien.checkCollision(self)
                if (alien.y > height):
                    self.lost = True
                    self.displayText("YOU DIED")
                  
            bottom_row_aliens = []

            for alien in self.aliens:
                alien.time_since_last_rocket += 1
            
            for alien in self.aliens:
                alienX = alien.x
                alien_maxY = alien.y
                bottom_alien = alien
                for aux_alien in self.aliens:
                    if aux_alien.x == alienX:
                        if aux_alien.y > alien_maxY:
                            alien_maxY = aux_alien.y
                            bottom_alien = aux_alien
                bottom_row_aliens.append(bottom_alien)                

            if len(bottom_row_aliens) > 0:
                random_alien = random.choice(bottom_row_aliens)
                if random_alien.time_since_last_rocket >= 60:
                    self.alien_rockets.append(AlienRocket(self, random_alien.x + 15, random_alien.y + 20))
                    random_alien.time_since_last_rocket = 0
            

            for alien_rocket in self.alien_rockets:
                for bunker in self.bunker_list:
                    if self.distance(alien_rocket.x, alien_rocket.y, bunker.x, bunker.y) < 20:
                        if alien_rocket in self.alien_rockets:
                            self.alien_rockets.remove(alien_rocket)
                        self.bunker_list.remove(bunker)
            
            for rocket in self.rockets:
                for bunker in self.bunker_list:
                    if self.distance(rocket.x, rocket.y, bunker.x, bunker.y) < 5:
                        self.rockets.remove(rocket)
                        self.bunker_list.remove(bunker)
            
            for rocket in self.rockets:
                rocket.draw()

            for alien_rocket in self.alien_rockets:
                alien_rocket.draw()

            if not self.lost: hero.draw()

            for bunker in self.bunker_list:
                bunker.draw()

            for alien_rocket in self.alien_rockets:
                if alien_rocket.y < 0 or alien_rocket.y > 1000:
                    self.alien_rockets.remove(alien_rocket)
            
            for rocket in self.rockets:
                if rocket.y < 0 or rocket.y > 1000:
                    self.rockets.remove(rocket)
            

    def displayText(self, text):
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 50)
        textsurface = font.render(text, False, RED)
        self.screen.blit(textsurface, (200, 160))
    
    def displayScore(self, text):
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 50)
        textsurface = font.render(text, False, RED)
        self.screen.blit(textsurface, (200, 300))
    
    def displayHighscore(self, text):
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 50)
        textsurface = font.render(text, False, RED)
        self.screen.blit(textsurface, (200, 440))

    def load_data(self):
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))


class Alien:

    time_since_last_rocket = 0

    def __init__(self, game, x, y, index):
        self.x = x
        self.game = game
        self.y = y
        self.size = 30
        self.index = index

    def draw(self):
        pygame.draw.rect(self.game.screen,
                         (81, 43, 88),
                         pygame.Rect(self.x, self.y, self.size, self.size))
        self.y += 0.05

    def checkCollision(self, game):
        for rocket in game.rockets:
            if (rocket.x < self.x + self.size and
                    rocket.x > self.x - self.size and
                    rocket.y < self.y + self.size and
                    rocket.y > self.y - self.size):
                game.rockets.remove(rocket)
                game.aliens.remove(self)
                game.score += 5

class Hero:
    def __init__(self, game, x, y):
        self.x = x
        self.game = game
        self.y = y

    def draw(self):
        pygame.draw.rect(self.game.screen,
                         (210, 250, 251),
                         pygame.Rect(self.x, self.y, 12, 8))

    def checkCollision(self, game):
        for alien_rocket in game.alien_rockets:
            if self.dist(alien_rocket.x, alien_rocket.y, self.x, self.y) < 10:
                game.alien_rockets.remove(alien_rocket)
                game.lost = True
    
    def dist(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))
    
class Generator:
    def __init__(self, game):
        margin = 30
        width = 40
        index = 0
        i = -1
        j = -1
        for x in range(margin, game.width - margin, width):
            i += 1
            j = -1
            for y in range(margin, int(game.height / 3), width):
                j += 1
                game.aliens.append(Alien(game, x, y, index))
                index += 1
                game.mat_aliens[i][j] = game.aliens[len(game.aliens) - 1]
        
        for bunk in range(3):
                for row in range(5):
                    for column in range(10):
                        bunker = Bunker(game, (130 + (200 * bunk)) + (10 * column), 450 + (10 * row))
                        game.bunker_list.append(bunker)
        

class Bunker:
    def __init__(self, game, x, y):
        self.x = x
        self.y = y
        self.game = game

    def draw(self):
        pygame.draw.rect(self.game.screen,
                        GREEN,
                        pygame.Rect(self.x, self.y, 8, 8))

class Rocket:
    def __init__(self, game, x, y):
        self.x = x
        self.y = y
        self.game = game

    def draw(self):
        pygame.draw.rect(self.game.screen,
                         (255, 255, 255),
                         pygame.Rect(self.x, self.y, 3, 5))
        self.y -= 4

class AlienRocket:
    def __init__(self, game, x, y):
        self.x = x
        self.y = y
        self.game = game

    def draw(self):
        pygame.draw.rect(self.game.screen,
                        RED,
                        pygame.Rect(self.x, self.y, 3, 5))
        self.y += 4                

if __name__ == '__main__':
    game = Game(800, 650)
    #game = Game(1500, 1500)