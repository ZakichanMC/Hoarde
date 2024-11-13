import math
import pygame
import random

#initialize
pygame.init()
SCREEN = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Hoarde!")


#different timers
SHOOTEVENT = pygame.USEREVENT + 0

SPAWNEVENT = pygame.USEREVENT + 1

RELOADEVENT = pygame.USEREVENT + 2 

WAVEEVENT = pygame.USEREVENT + 3
waveDurations = [10000, 15000, 0]  # Durations for each wave in milliseconds

#some default variables
gameState = "start menu"
holding = "gun"
enemyState = "attack"

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (168, 168, 168)
YELLOW = (245, 240, 196)
BLUE = (72, 80, 219)
GOLD = (235, 152, 19)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()

playerHP = 100
ammo = 100
playerSpeed = 4
currentWave = 1
score = 0
enemiesKilled = 0
hasReloaded = False


#menus
def startMenu():
  SCREEN.fill(BLACK)
  titleFont = pygame.font.SysFont('arial', 80)
  font = pygame.font.SysFont('arial', 40)
  title = titleFont.render('Hoarde!', True, WHITE)
  startButton = font.render('Press Enter to Continue', True, WHITE)
  SCREEN.blit(title,
              (250 - title.get_width() / 2, 150))
  SCREEN.blit(
      startButton,
      (250 - startButton.get_width() / 2, 250 + startButton.get_height() / 2))
  pygame.display.update()


def intro():
  introText = [
      "You\'ve just won a billion dollars!",
      "But, oh no, everyone\'s jealous!",
      "Fend off the horde of angry, angry people",
      "who are trying to steal all your money!", "Take care of them quick,",
      "because the longer you take,", "the angrier they get!",
      "PS: Some people drop their coins when shot",
      "You didn't hear it from me",
      "I\'ll give you a useful tool to start with.", "Press E to continue"
  ]
  SCREEN.fill(BLACK)
  font = pygame.font.SysFont('arial', 25)
  for i in range(len(introText)):
    text = font.render(introText[i], True, WHITE)
    SCREEN.blit(text, (250 - text.get_width() / 2, 75 + i * 35))
  pygame.display.update()


def tutorial():
  tutorialText = [
      "WASD to move", "Left Click to Shoot", "R to Reload", "Press Enter to Start Game",
      "Good Luck Surviving the Apocalypse"
  ]
  SCREEN.fill(BLACK)
  font = pygame.font.SysFont('arial', 25)
  for i in range(len(tutorialText)):
    text = font.render(tutorialText[i], True, WHITE)
    SCREEN.blit(text, (250 - text.get_width() / 2, 200 + i * 35))
  pygame.display.update()


def gameOver():
  SCREEN.fill(BLACK)
  font = pygame.font.SysFont('arial', 40)
  smallFont = pygame.font.SysFont('arial', 20)
  gameOverText = font.render('YOU DIED!', True, WHITE)
  restart = smallFont.render('Press ENTER to restart or Esc to quit', True,
                             WHITE)
  SCREEN.blit(gameOverText, (250 - gameOverText.get_width() / 2,
                             250 - gameOverText.get_height() / 2))
  SCREEN.blit(restart,
              (250 - restart.get_width() / 2, 400 + restart.get_height() / 2))
  pygame.display.update()


def winScreen():
  SCREEN.fill(BLACK)
  largeFont = pygame.font.SysFont('arial', 60)
  font = pygame.font.SysFont('arial', 25)
  youWin = largeFont.render('YOU SURVIVED!', True, WHITE)
  scoreText = font.render("Score: " + str(score), True, WHITE)
  moneyText = font.render("You get to take home all your money.", True,
                          WHITE)
  SCREEN.blit(youWin, (250 - youWin.get_width() / 2, 100))
  SCREEN.blit(moneyText,
              (250 - moneyText.get_width() / 2, youWin.get_height() + 150))
  SCREEN.blit(scoreText, (250 - scoreText.get_width() / 2, 250))

  hiddenAchievements = [["Hidden Achievement: Skillful", "Survive without taking any damage"], ["Hidden Achievement: Sharpshooter", "Take out all enemies with 100 bullets or less"]]

  if playerHP == 100:
    for text in range(len(hiddenAchievements[0])):
      hiddenText = font.render(hiddenAchievements[0][text], True, WHITE)
      SCREEN.blit(hiddenText, (250 - hiddenText.get_width() / 2, 350 + text * 25))

  if not hasReloaded:
    for text in range(len(hiddenAchievements[1])):
      hiddenText = font.render(hiddenAchievements[1][text], True, WHITE)
      SCREEN.blit(hiddenText, (250 - hiddenText.get_width() / 2, 425 + text * 25))
  pygame.display.update()


#objects
class Player(pygame.sprite.Sprite):

  def __init__(self, color, width, height):
    super().__init__()

    self.image = pygame.Surface([width, height])
    self.image.fill(YELLOW)
    self.image.set_colorkey(YELLOW)
    pygame.draw.rect(self.image, color, [0, 0, width, height])
    self.rect = self.image.get_rect()

  #movement
  def UP(self):
    self.rect.y -= 1 * playerSpeed
    if self.rect.y < 0:
      self.rect.y = 0

  def DOWN(self):
    self.rect.y += 1 * playerSpeed
    if self.rect.y > 480:
      self.rect.y = 480

  def LEFT(self):
    self.rect.x -= 1 * playerSpeed
    if self.rect.x < 0:
      self.rect.x = 0

  def RIGHT(self):
    self.rect.x += 1 * playerSpeed
    if self.rect.x > 490:
      self.rect.x = 490


class Gun(pygame.sprite.Sprite):

  def __init__(self, color, width, height):
    super().__init__()

    #saving the original image
    self.original_image = pygame.Surface([width, height], pygame.SRCALPHA)
    self.original_image.fill(YELLOW)
    self.original_image.set_colorkey(YELLOW)
    pygame.draw.rect(self.original_image, color, [0, 0, width, height])

    #saving an image to blit, and also to use as rect
    self.image = self.original_image
    self.rect = self.image.get_rect()
    self.offset = pygame.math.Vector2(0, 10) #x and y values, offset y by 10

  def rotate(self): #following the mouse
    mouseX, mouseY = pygame.mouse.get_pos()
    relativeX, relativeY = mouseX - self.rect.x, mouseY - self.rect.y
    angle = (180 / math.pi) * -math.atan2(relativeX, relativeY)  #radians
    self.image = pygame.transform.rotozoom(self.original_image, -angle, 1)
    offsetRotated = self.offset.rotate(angle)
    self.rect = self.image.get_rect(center=player.rect.center + offsetRotated)


class Bullet(pygame.sprite.Sprite):

  def __init__(self, color, width, height):
    super().__init__()

    self.image = pygame.Surface([width, height])
    self.image.fill(YELLOW)
    self.image.set_colorkey(YELLOW)

    pygame.draw.rect(self.image, color, [0, 0, width, height])
    self.rect = self.image.get_rect()
    self.rect.x, self.rect.y = gun.rect.center

    #find the distance between bullet and target and calculate the angle between them
    mouseX, mouseY = pygame.mouse.get_pos()
    relativeX, relativeY = mouseX - self.rect.x, mouseY - self.rect.y
    self.angle = math.atan2(relativeY, relativeX)

  def shoot(self, spd):
    self.rect.x += spd * math.cos(self.angle)
    self.rect.y += spd * math.sin(self.angle)


class Enemy(pygame.sprite.Sprite):

  def __init__(self, color, width, height):
    super().__init__()

    self.image = pygame.Surface([width, height])
    self.image.fill(YELLOW)
    self.image.set_colorkey(YELLOW)
    pygame.draw.rect(self.image, color, [0, 0, width, height])
    self.rect = self.image.get_rect()
    #spawn in random locations
    self.rect.x, self.rect.y = random.randint(0, 500), random.randint(0, 500) 

    #to prevent enemies spawning within 100px of player
    def spawn(self):
      self.rect.x, self.rect.y = random.randint(0, 500), random.randint(0, 500)
      if abs(player.rect.x - self.rect.x) < 100 and abs(player.rect.y -
                                                        self.rect.y) < 100:
        self.spawn()

  def moveTowards(self, spd):
    global playerHP, currentWave
    relX, relY = player.rect.x - self.rect.x, player.rect.y - self.rect.y
    self.angle = math.atan2(relY, relX)

    if abs(relX) < 200 and abs(relY) < 200:
      self.rect.x += spd * 0.5 * math.cos(self.angle)
      self.rect.y += spd * 0.5 * math.sin(self.angle)

      if random.randint(1, 1000) == 1: #randomize enemy movement more
        self.rect.x -= spd * 10 * math.cos(self.angle)
        self.rect.y -= spd * 10 * math.sin(self.angle)

    else: #idle if not in range
      self.rect.x, self.rect.y = self.rect.x, self.rect.y
    if self.rect.colliderect(player.rect): #move away when collide with player
      self.rect.x -= spd * 5 * math.cos(self.angle)
      self.rect.y -= spd * 5 * math.sin(self.angle)
      if currentWave == 1:
        playerHP -= 1
      elif currentWave == 2:
        playerHP -= 5
      elif currentWave == 3:
        playerHP -= 10


class Coin(pygame.sprite.Sprite):

  def __init__(self, color, width, height):
    super().__init__()

    self.image = pygame.Surface([width, height])
    self.image.fill(YELLOW)
    self.image.set_colorkey(YELLOW)
    pygame.draw.rect(self.image, color, [0, 0, width, height])
    self.rect = self.image.get_rect()


player = Player(BLUE, 10, 20)

gun = Gun(GRAY, 5, 30)


spritesList = pygame.sprite.Group() #for perma sprites like player and gun
spritesList.add(player)

#for any class that spawns multiple instances of objects
bulletsList = pygame.sprite.Group()
enemiesList = pygame.sprite.Group()
coinsList = pygame.sprite.Group()

enemiesInWave = 0
addBullets = False


#to reset all the game variables
def initializeGame():
  global player, gun, enemiesInWave, currentWave, playerHP, ammo, playerSpeed, score, enemiesKilled, hasReloaded
  enemiesInWave = 0
  currentWave = 1
  playerHP = 100
  ammo = 100
  playerSpeed = 4
  score = 0
  enemiesKilled = 0
  hasReloaded = False
  player.rect.x, player.rect.y = 250, 250
  gun.rect.x, gun.rect.y = player.rect.x, player.rect.y
  pygame.time.set_timer(WAVEEVENT, waveDurations[currentWave - 1])
  pygame.time.set_timer(SPAWNEVENT, 1000)
  pygame.time.set_timer(SHOOTEVENT, 250)
  enemiesList.empty()
  bulletsList.empty()
  coinsList.empty()


#starting the game
run = True
while run:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

    if holding == "gun":
      if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(
      )[0]:
        addBullets = True #so that bullets keep moving while true not only while pressed
      if event.type == pygame.MOUSEBUTTONUP or ammo == 0:
        addBullets = False
      if event.type == SHOOTEVENT and gameState == "game" and addBullets:
        bullet = Bullet(RED, 5, 5)
        bulletsList.add(bullet)
        ammo -= 1

      if event.type == RELOADEVENT: #after 2 seconds pass
        ammo = 100
        hasReloaded = True
        pygame.time.set_timer(RELOADEVENT, 0) #stop the reload timer

      if event.type == WAVEEVENT and gameState == "game":
        currentWave += 1

        if currentWave <= len(waveDurations): #if not final wave
          pygame.time.set_timer(WAVEEVENT, waveDurations[currentWave - 1])

    if event.type == SPAWNEVENT and gameState == "game": #spawn enemies each second
      if enemiesInWave < 60:
        enemy = Enemy(BLACK, 10, 20)
        enemiesList.add(enemy)
        enemiesInWave += 1

  keys = pygame.key.get_pressed()

  #switching states
  if gameState == "start menu":
    startMenu()
    if keys[pygame.K_RETURN]:
      gameState = "intro"
  elif gameState == "intro":
    intro()
    if keys[pygame.K_e]:
      gameState = "tutorial"
  elif gameState == "tutorial":
    tutorial()
    if keys[pygame.K_RETURN]:
      gameState = "game"
      initializeGame()
  elif gameState == "game over":
    gameOver()
    if keys[pygame.K_RETURN]:
      gameState = "game"
      initializeGame()
    if keys[pygame.K_ESCAPE]:
      pygame.quit()
  elif gameState == "win":
    winScreen()

  elif gameState == "game":
    #game code here
    SCREEN.fill(YELLOW)

    #player movement
    if keys[pygame.K_w]:
      player.UP()
    if keys[pygame.K_s]:
      player.DOWN()
    if keys[pygame.K_a]:
      player.LEFT()
    if keys[pygame.K_d]:
      player.RIGHT()

    if keys[pygame.K_r]: #when press r start reload timer for 2 secs
      pygame.time.set_timer(RELOADEVENT, 2000)

    for bullet in bulletsList: #every bullet on screen
      bullet.shoot(4)
      if bullet.rect.x > 490 or bullet.rect.y < 0 or bullet.rect.y > 490 or bullet.rect.y < 0:
        bulletsList.remove(bullet) #delete when offscreen
      for enemy in enemiesList:
        if bullet.rect.colliderect(enemy.rect):
          enemiesList.remove(enemy)
          bulletsList.remove(bullet)
          enemiesKilled += 1
          if random.randint(1, 4) == 1: #25% chance to drop a coin
            coin = Coin(GOLD, 20, 20)
            coinsList.add(coin)
            coin.rect.x, coin.rect.y = enemy.rect.x, enemy.rect.y #drop at pos of enemy kill
          if currentWave == 1:
            score += 10
          elif currentWave == 2:
            score += 30
          elif currentWave == 3:
            score += 100 #kills are harder, but more valuable at later waves

    for coin in coinsList:
      if coin.rect.colliderect(player.rect):
        coinsList.remove(coin)
        if currentWave == 1:
          score += 50
        elif currentWave == 2:
          score += 100
        elif currentWave == 3:
          score += 1000 #coins are more valuable at later waves

    if holding == "gun":
      spritesList.add(gun)
      gun.rect.x, gun.rect.y = player.rect.x, player.rect.y
      gun.rotate()

    for enemy in enemiesList:
      if currentWave == 1:
        enemy.moveTowards(2)
      elif currentWave == 2:
        enemy.moveTowards(3)
      elif currentWave == 3:
        enemy.moveTowards(4)

    if playerHP <= 0:
      gameState = "game over"

    if enemiesKilled == 60:
      gameState = "win"

    #hp, ammo, wave and score on screen
    font = pygame.font.Font(None, 30)
    hpText = font.render("HP: " + str(playerHP), 1, BLACK)
    SCREEN.blit(hpText, (10, 10))
    ammoText = font.render("Ammo: " + str(ammo), 1, BLACK)
    SCREEN.blit(ammoText, (10, 30))
    waveText = font.render("Wave: " + str(currentWave), 1, BLACK)
    SCREEN.blit(waveText, (10, 50))
    scoreText = font.render("Score: " + str(score), 1, BLACK)
    SCREEN.blit(scoreText, (10, 70))

    #draw all sprites
    spritesList.update()
    spritesList.draw(SCREEN)
    bulletsList.draw(SCREEN)
    enemiesList.draw(SCREEN)
    coinsList.draw(SCREEN)

  pygame.display.update()
  clock.tick(30) #fps