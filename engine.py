import pygame as pg
import math,random,time
from settings import *

def clamp(n, minn, maxn):
  return max(min(maxn, n), minn)

def cutIMG(surf,x,y,width,height):
  handle = surf.copy()
  wantedArea = pg.Rect(x,y,width,height)
  handle.set_clip(wantedArea)
  image = surf.subsurface(handle.get_clip())
  return image.copy()

def move(movingItem,cGroup,dt):
  movingItem.collisions = {'top': False,'bottom': False,'left': False,'right': False}
  movingItem.rect.x += movingItem.vel[0] * dt
  for obj in cGroup:
    if movingItem.rect.colliderect(obj):
      if movingItem.vel[0] > 0:
        movingItem.collisions['right'] = True
        movingItem.rect.right = obj.left
        movingItem.vel[0] = 0 if movingItem.vel[0] > 0 else movingItem.vel[0]
      else:
        movingItem.collisions['left'] = True
        movingItem.rect.left = obj.right
  movingItem.rect.y += movingItem.vel[1] * dt
  for obj in cGroup:
    if movingItem.rect.colliderect(obj):
      if movingItem.vel[1] > 0:
        movingItem.collisions['bottom'] = True
        movingItem.rect.bottom = obj.top
      else:
        movingItem.collisions['top'] = True
        movingItem.rect.top = obj.bottom

def getSpeedToPoint(wantedSpeed,origin,point):
  xDisplacement = point[0] - origin[0]
  yDisplacement = point[1] - origin[1]
  
  #find gradient of the bullet's path
  if xDisplacement == 0:
    #to fix error when dividing by 0
    speed = [0,yDisplacement]
  else:
    xyRatio = yDisplacement / xDisplacement
    speedMulti = 1
    if xDisplacement < 0:
      speedMulti *= -1
    speed = [speedMulti,speedMulti*xyRatio]
  
  #get speed to be constant
  bulletSpeed = math.sqrt(speed[0]**2+speed[1]**2)
  speed[0] *= wantedSpeed / bulletSpeed
  speed[1] *= wantedSpeed / bulletSpeed
  return speed

class font():
  def __init__(self,path):
    font = pg.image.load('assets/'+path+'.png')
    charOrder = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9','-']
    count = charWidth = 0
    self.spacing = 4
    self.characters = {}
    for x in range(font.get_width()):
      c = font.get_at((x,0))
      if c[1] == 190:
        charIMG = cutIMG(font,x-charWidth,0,charWidth,font.get_height())
        self.characters[charOrder[count]] = charIMG
        charWidth = 0
        count += 1
      else:
        charWidth += 1

  def render(self,text,loc):
    offset = 0
    for char in text:
      if char == ' ':
        offset += 40
      else:
        display.blit(self.characters[char],(loc[0]+offset,loc[1]))
        offset += self.characters[char].get_width() + self.spacing

class particleSystem():
  def __init__(self):
    self.particles = []

  def addParticles(self,amount,loc,size,colour,speed,decay):
    for i in range(amount):
      self.particles.append({'x':loc[0],'y':loc[1],'size':size,'colour':colour,'speed':speed,'decay':decay,'startTime':time.time()})

  def update(self,dt):
    for particle in self.particles:
      self.move(particle,dt)
      self.render(particle)
      self.checkDecay(particle,dt)

  def move(self,particle,dt):
    particle['x'] += random.randint(-particle['speed'],particle['speed']) * dt
    particle['y'] += random.randint(-particle['speed'],particle['speed']) * dt

  def render(self,particle):
    pg.draw.circle(display,particle['colour'],(int(particle['x']),int(particle['y'])),particle['size']//2)

  def checkDecay(self,particle,dt):
    particle['decay'] -= dt
    if particle['decay'] < 0:
      self.particles.remove(particle)

class gameMap():
  def __init__(self,path):
    self.currentMap = path
    scale = resolution[1] / 27
    f = open('assets/'+path+'.txt','r')
    layers = f.read().split('\n')
    f.close()
    y = 0
    block1 = []
    self.rect = []
    for layer in layers:
      x= 0
      blocks = map(int, layer)
      for block in blocks:
        if block == 1:
          block1.append((x,y))
          self.rect.append(pg.Rect(x*scale,y*scale,scale,scale))
        x += 1
      y += 1

  def render(self):
    for rect in self.rect:
      pg.draw.rect(display,yellow,rect)