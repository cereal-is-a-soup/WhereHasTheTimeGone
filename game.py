import pygame as pg
import time,random
from pygame.locals import *

from settings import *
from engine import *

pg.init()
pg.mixer.init()
clock = pg.time.Clock()
particles = particleSystem()

#-------------------------assets-----------------------------
hurtSound = pg.mixer.Sound('assets/audio/hurt.wav')
shootSound = pg.mixer.Sound('assets/audio/rifleShoot.wav')
pickupSound = pg.mixer.Sound('assets/audio/pickup.wav')
blinkSound = pg.mixer.Sound('assets/audio/blink.wav')
ZAWARUDO = pg.mixer.Sound('assets/audio/timestop.wav')

class Player():
  def __init__(self):
    self.rect = pg.Rect(100,100,80,80)
    self.rect.center = (resolution[0]//2,resolution[1]//2)
    self.energy = self.health = 50
    self.collisions = {}
    self.dead = False
    self.vel = [0,0]
    self.maxspeed = 10
    self.moveUp = self.moveDown = self.moveLeft = self.moveRight = self.blink = False
    self.blinkTime = time.time()
    self.shooting = False
    self.lastShot = time.time()
    self.firerate = 0.8
    self.timeStop = False
    self.timer = 0

  def update(self):
    self.movement()
    if self.collisions['top']:
      particles.addParticles(5,(self.rect.centerx,self.rect.top),10,yellow,10,5)
    if self.collisions['bottom']:
      particles.addParticles(5,(self.rect.centerx,self.rect.bottom),10,yellow,10,5)
    if self.collisions['left']:
      particles.addParticles(5,(self.rect.left,self.rect.centery),10,yellow,10,5)
    if self.collisions['right']:
        particles.addParticles(2,(self.rect.right,self.rect.centery),10,yellow,10,5)
    if not self.timeStop:
      game.timescale = .1 if self.vel == [0,0] else 1.2
    self.shoot()
    self.stopTime()
    self.dead = self.checkState()
    self.rect.centerx = clamp(self.rect.centerx,0,resolution[0])
    self.rect.centery = clamp(self.rect.centery,0,resolution[1])
    self.render()

  def movement(self):
    self.control()
    self.changeSpeed()
    if self.blink and self.energy >= 5:
      blinkSound.play()
      particles.addParticles(20,self.rect.center,10,blue,30,5)
      self.energy -= 3
      self.vel = self.blinkSpeed
      timeSinceBlink = time.time() - self.blinkTime
      if timeSinceBlink > .1:
        self.blink = False
    move(self,game.world.rect,game.rdt)

  def control(self):
    keyDown = pg.key.get_pressed()
    self.moveUp = True if keyDown[K_w] else False
    self.moveDown = True if keyDown[K_s] else False
    self.moveLeft = True if keyDown[K_a] else False
    self.moveRight = True if keyDown[K_d] else False
    for event in pg.event.get():
      if event.type == KEYDOWN and event.key == K_LSHIFT and not self.blink:
        self.blink = True
        self.blinkTime = time.time()
        self.blinkSpeed = getSpeedToPoint(230,self.rect.center,pg.mouse.get_pos())
    mouseDown = pg.mouse.get_pressed()
    self.shooting = True if mouseDown[0] else False
    self.timeStop = True if mouseDown[2] and self.energy > 0 else False

  def changeSpeed(self):
    if self.moveRight:
      self.vel[0] += 1
    if self.moveLeft:
      self.vel[0] -= 1
    if self.moveDown:
      self.vel[1] += 1
    if self.moveUp:
      self.vel[1] -= 1
    if not(self.moveLeft or self.moveRight):
      self.vel[0] = 0
    if not(self.moveUp or self.moveDown):
      self.vel[1] = 0
    if self.vel[0] != 0 and self.vel[1] != 0:
      topspeed = math.sqrt(self.maxspeed ** 2 / 2)
    else:
      topspeed = self.maxspeed
    if self.shooting:
      topspeed /= 2
    self.vel[0] = clamp(self.vel[0],-topspeed,topspeed)
    self.vel[1] = clamp(self.vel[1],-topspeed,topspeed)

  def shoot(self):
    global projectiles
    if self.shooting and game.timescale != 0:
      if time.time() - self.lastShot > (1 - self.firerate) / math.sqrt(game.timescale):
        speed = getSpeedToPoint(25,self.rect.center,pg.mouse.get_pos())
        shootSound.play()
        projectiles.append(projectile(enemies, self.rect.center, speed, 25,black,10,5,self))
        self.lastShot = time.time()

  def getRecoil(self):
    if self.vel == [0,0]:
      recoil = .1
    else:
      recoil = .6
    spread = random.uniform(1-recoil,1+recoil)
    return spread

  def checkState(self):
    self.health = clamp(self.health,0,50)
    self.energy = clamp(self.energy,0,50)
    if self.health <= 0:
      return True
    return False

  def stopTime(self):
    if self.timeStop:
      if game.timescale > 0:
        pg.mixer.Channel(2).set_volume(0.8)
        pg.mixer.Channel(2).play(ZAWARUDO)
      game.timescale = 0
      s = pg.Surface(resolution)
      s.set_alpha(170)
      s.fill((0,0,0))
      display.blit(s,(0,0))
      self.timer += game.rdt
      if self.timer > 10:
        self.energy -= 2
        self.timer = 0
    else:
        pg.mixer.Channel(2).set_volume(0)

  def render(self):
    pg.draw.circle(display,blue,self.rect.center,self.rect.width//2)
    pg.draw.circle(display,(0,255,0),pg.mouse.get_pos(),5,1)
    pg.draw.rect(display,red,pg.Rect(20,resolution[1]-40,self.health*4,15))
    pg.draw.rect(display,blue,pg.Rect(20,resolution[1]-25,self.energy*4,5))

class enemyDisruptor(): 
  def __init__(self,loc):
    self.health = 100
    self.vel = [0,0]
    self.rect = pg.Rect(loc[0],loc[1],60,60)
    self.maxspeed = 5
    self.suicide = False
    self.flash = False
    self.colour = red
    self.timer = 4

  def update(self,target):
    self.render()
    self.pursuit(target)
    self.movement()

  def render(self):
    self.colour = red
    if self.flash:
      self.timer -= game.rdt
      self.colour = (240,240,240)
      if self.timer < 0:
        self.timer = 4
        self.flash = False
    pg.draw.rect(display,self.colour,self.rect)

  def pursuit(self,target):
    if self.vel[0] != 0 and self.vel[1] != 0:
      topspeed = math.sqrt(self.maxspeed ** 2 / 2)
    else:
      topspeed = self.maxspeed
    self.vel = getSpeedToPoint(topspeed,self.rect.center,target.rect.center)
    self.vel[0] = clamp(self.vel[0],-topspeed,topspeed)
    self.vel[1] = clamp(self.vel[1],-topspeed,topspeed)
    if self.rect.colliderect(target.rect) and game.timescale != 0:
      self.suicide = True
      hurtSound.play()
      target.health -= 10
      self.health = 0

  def movement(self):
    global enemies
    collGroup = game.world.rect.copy()
    for enemy in enemies:
      if enemy is not self:
        collGroup.append(enemy.rect)
    move(self,collGroup,game.dt)

class enemySniper():
  def __init__(self,loc):
    self.health = 100
    self.vel = [0,0]
    self.rect = pg.Rect(loc[0],loc[1],60,60)
    self.maxspeed = 8
    self.firerate = 0.2
    self.lastShot = time.time()
    self.suicide = False
    self.state = 'firing'
    self.timer = 4
    self.flash = False
  
  def update(self,target):
    self.render()
    self.movement()
    self.state = self.getState(target)
    if self.state == 'firing':
      self.shoot(target)
    elif self.state == 'hunt':
      self.track(target)

  def getState(self,target):
    state = 'hunt'
    xDistance = abs(self.rect.x - target.rect.x)
    yDistance = abs(self.rect.y - target.rect.y)
    distance = math.sqrt(xDistance**2+yDistance**2)
    if distance < 600:
      state = 'firing'
    return state

  def render(self):
    self.colour = black
    if self.flash:
      self.timer -= game.rdt
      self.colour = (240,240,240)
      if self.timer < 0:
        self.timer = 4
        self.flash = False
    pg.draw.rect(display,self.colour,self.rect)

  def movement(self):
    global enemies
    collGroup = game.world.rect.copy()
    for enemy in enemies:
      if enemy is not self:
        collGroup.append(enemy.rect)
    move(self,collGroup,game.dt)

  def track(self,target):
    if self.vel[0] != 0 and self.vel[1] != 0:
      topspeed = math.sqrt(self.maxspeed ** 2 / 2)
    else:
      topspeed = self.maxspeed
    self.vel[0] = topspeed if target.rect.x > self.rect.x else -topspeed
    self.vel[1] = topspeed if target.rect.y > self.rect.y else -topspeed

  def shoot(self,target):
    self.vel = [0,0]
    global projectiles
    if game.timescale != 0:
      if time.time() - self.lastShot > (1 - self.firerate) / math.sqrt(game.timescale):
        speed = getSpeedToPoint(5,self.rect.center,target.rect.center)
        projectiles.append(projectile([player],self.rect.center,speed,5,black,10,1,self))
        self.lastShot = time.time()

class projectile():
  def __init__(self, target, loc, speed, damage, colour=black, size=10,penetration=5,source=None):
    self.startTime = time.time()
    self.rect = pg.Rect(loc[0],loc[1],size,size)
    self.vel = speed
    self.dmg = damage
    self.colour = colour
    self.decay = False
    self.penetration = penetration
    self.targets = target
    self.source = source

  def update(self):
    self.movement()
    self.checkDecay()
    pg.draw.rect(display,self.colour,self.rect)

  def movement(self):
    self.rect.x += self.vel[0] * game.dt
    self.rect.y += self.vel[1] * game.dt

  def checkDecay(self):
    if time.time() - self.startTime > 10 or self.penetration < 0:
      self.decay = True
    for wall in game.world.rect:
      if self.rect.colliderect(wall) and self not in trails:
        particles.addParticles(5,self.rect.center,10,yellow,20,5)
        self.decay = True

  def damageTargets(self):
    if self.targets != None:
      for target in self.targets:
        if self.rect.colliderect(target.rect) and game.timescale != 0:
          if target in enemies:
            target.flash = True
          target.health -= self.dmg
          self.penetration -= 1

class healthpack():
  def __init__(self,loc,packType='health'):
    self.loc = loc
    self.rect = pg.Rect(loc[0],loc[1],60,60)
    self.pickedUp = False
    self.type = packType
  
  def update(self):
    for wall in game.world.rect:
      if self.rect.colliderect(wall):
        self.bottom = wall.top
        self.right = wall.left
    if self.type == 'health':
      pg.draw.circle(display,red,self.rect.center,30)
      pg.draw.circle(display,blue,self.rect.center,25)
      if player.rect.colliderect(self.rect) and player.health < 50:
        pickupSound.play()
        player.health += 5
        self.pickedUp = True
    elif self.type == 'energy':
      pg.draw.circle(display,blue,self.rect.center,30)
      if player.rect.colliderect(self.rect) and player.energy < 50:
        pickupSound.play()
        player.energy += 10
        self.pickedUp = True

class portal():
  def __init__(self,loc,destination):
    self.rect = pg.Rect(loc[0],loc[1],80,120)
    self.timer = 10
    self.active = False
    self.decay = False
    self.destination = destination

  def update(self,dt):
    if self.rect.colliderect(player.rect):
      self.active = True
    if self.active:
      self.timer -= dt
      if self.timer < 0:
        game.world = gameMap(self.destination)
        self.decay = True
    self.render()

  def render(self):
    pg.draw.ellipse(display,blue,self.rect)
    if self.active:
      transition = pg.Surface(resolution)
      if self.timer > 1:
        width = max(0,int(self.timer)*100 - 100) 
        pg.draw.circle(transition,red,player.rect.center,width)
        transition.set_colorkey(red)
      display.blit(transition,(0,0))

class Game():
  def __init__(self):
    self.timescale = 1.2
    self.lastTime = time.time()
    self.replayEndless = False
    self.score = self.highscore = 0
    self.world = None

  def mainMenu(self):
    run = True
    while run:
      pg.mouse.set_visible(True)
      for event in pg.event.get():
        if event.type == QUIT:
          run = False
        elif event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            run = False
      display.fill(black)
      text.render('WHEREHASTHETIMEGONE',(50,50))
      text.render('HIGH SCORE '+str(self.highscore),(950,950))
      playButton = pg.Rect(0,0,282,72)
      playButton.center = (resolution[0]//2,resolution[1]//2)
      mousePressed = pg.mouse.get_pressed()
      click = True if mousePressed[0] else False
      if playButton.collidepoint(pg.mouse.get_pos()):
        playButton = pg.Rect(0,0,282,120)
        playButton.center = (resolution[0]//2,resolution[1]//2)
        if click:
          self.endless()
      text.render('PLAY',(playButton.x,playButton.y))
      pg.display.update()

  def endless(self):
    pg.mouse.set_visible(False)
    self.score = 0
    global player, healthpacks, enemies, projectiles,trails
    self.world = gameMap("testWorld")
    projectiles = []
    player = Player()
    healthpacks = []
    enemies = []
    trails = []
    particles.particles = []
    while True:
      self.dt = time.time() - self.lastTime
      self.rdt = self.dt * framerate * 1.5
      self.dt *= framerate * self.timescale
      self.lastTime = time.time()
      clock.tick(framerate)
      
      #spawns enemy or objects
      if len(enemies) < 5 + self.score // 40:
        if random.random() < .1 and time.time() % 3  < 1:
          distance = 0
          while distance < 300:
            loc = (random.randint(0,resolution[0]),random.randint(0,resolution[1]))
            distance = math.sqrt(abs(loc[0]-player.rect.x)**2 + abs(loc[1]-player.rect.y)**2)
          spawnType = 0 if random.randint(-2000,self.score) <= 0 else 1
          if spawnType == 0:
            enemies.append(enemyDisruptor(loc))
          elif spawnType == 1:
            enemies.append(enemySniper(loc))
      if len(healthpacks) < 4:
        packtype = ['health','energy']
        h = 50 - player.health
        e = 50 - player.energy
        i = 0 if random.randint(-h,e) <= 0 else 1
        healthpacks.append(healthpack((random.randint(0,resolution[0]),random.randint(0,resolution[1])),packtype[i]))

      display.fill(white)
      self.world.render()
      for trail in trails:
        try:
          if time.time() - trail.startTime > .15 / self.timescale:
            trails.remove(trail)
        except ZeroDivisionError:
          pass
        trail.update()
      for bullet in projectiles:
        if bullet.decay:
          projectiles.remove(bullet)
        bullet.update()
        bullet.damageTargets()
        if bullet.source in enemies:
          trails.append(projectile(None,bullet.rect.center,(0,0),0,red,5))
        elif bullet.source is player:
          trails.append(projectile(None,bullet.rect.center,(0,0),0,blue,5))
      for enemy in enemies:
        enemy.update(player)
        if enemy.health <= 0:
          particles.addParticles(40,enemy.rect.center,10,red,20,10)
          enemies.remove(enemy)
          self.score += -2 if enemy.suicide else 5
      for pack in healthpacks:
        if pack.pickedUp:
          self.score += 5
          healthpacks.remove(pack)
        pack.update()
      player.update()
      particles.update(self.dt)
      text.render('SCORE '+str(self.score),(0,0))
      pg.display.update()
      if self.gameEnd():
        if self.score > self.highscore:
          self.highscore = self.score
        break

  def gameEnd(self):
    if player.dead:
      return True
    for event in pg.event.get():
      if event.type == QUIT:
        self.replayEndless = False
        return True
    keysPressed = pg.key.get_pressed()
    if keysPressed[K_ESCAPE]:
      self.replayEndless = False
      return True
    return False

text = font('font')
game = Game()
game.mainMenu()
pg.mixer.quit()
pg.QUIT