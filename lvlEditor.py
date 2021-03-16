import pygame as pg
from pygame.locals import *

resolution = (1920,1080)
pg.init()
pg.mixer.init()
clock = pg.time.Clock()
display = pg.display.set_mode(resolution, pg.FULLSCREEN)
pg.display.set_caption('lvlEditor')
scale = int(resolution[1] / 27)
white = (60, 71, 75)
black = (15, 15, 40)
red = (240, 56, 64)
blue = (89, 165, 216)
yellow = (249, 200, 70)

class gameMap():
  def __init__(self):
    f = open('assets/'+path+'.txt','r')
    layers = f.read().split('\n')
    f.close()
    y = 0
    self.block1 = []
    for layer in layers:
      x= 0
      blocks = map(int, layer)
      for block in blocks:
        if block == 1:
          self.block1.append((x,y))
        x += 1
      y += 1

  def render(self):
    display.fill(white)
    for block in self.block1:
      draw = pg.Rect(block[0]*scale,block[1]*scale,scale,scale)
      pg.draw.rect(display,yellow,draw)

run = True
path = "orbiter"
world = gameMap()
creating = destroy = False
scale = int(resolution[1] / 27)
while run:
  world.render()
  for event in pg.event.get():
    if event.type == QUIT:
      run = False
    elif event.type == KEYDOWN:
      if event.key == K_a:
        world.block1.clear()
      if event.key == K_ESCAPE:
        run = False
      if event.key == K_s:
        f = open('assets/'+path+'.txt','w')
        for y in range(27):
          line = ''
          for x in range(48):
            line += '1' if (x,y) in world.block1 else '0'
          f.write(line+'\n')
        f.close()
        run = False
    elif event.type == MOUSEBUTTONDOWN:
      x,y = pg.mouse.get_pos()
      x //= scale
      y //= scale
      start = (x,y)
      if event.button == 1:
        creating = True
      elif event.button == 3:
        destroy = True
    elif event.type == MOUSEBUTTONUP:
      if event.button == 1:
        creating = False
        for x in range(0,selection.width,scale):
          for y in range(0,selection.height,scale):
            world.block1.append((x//scale+start[0],y//scale+start[1]))
      elif event.button == 3:
        destroy = False
        for x in range(0,selection.width,scale):
          for y in range(0,selection.height,scale):
            if (x//scale+start[0],y//scale+start[1]) in world.block1:
              world.block1.remove((x//scale+start[0],y//scale+start[1]))
  x,y = pg.mouse.get_pos()
  x //= scale
  y //= scale
  end = (x,y)
  if creating:
    selection = pg.Rect(start[0]*scale,start[1]*scale,(end[0]-start[0])*scale,(end[1]-start[1])*scale)
    pg.draw.rect(display,yellow,selection,1)
  if destroy:
    selection = pg.Rect(start[0]*scale,start[1]*scale,(end[0]-start[0])*scale,(end[1]-start[1])*scale)
    pg.draw.rect(display,red,selection,1)
  pg.display.update()
  clock.tick(40)
pg.quit()