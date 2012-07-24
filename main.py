#!/usr/bin/python
import os
class sys:
  from sys import argv
import time
import pylirc
class select:
  from select import select
import socket
class string:
  from string import digits
import threading
import subprocess
import ConfigParser
from math import pi
try:
  import magic_nonexistent # magic ended up being too slow, I have disabled it, for now atleast.
  mime = magic.open(magic.MAGIC_MIME)
  mime.load()
except ImportError:
  magic = None
  import mimetypes
  mime = False
import pygame
try: # I would like this to run on Android as well, this section is needed for that to work.
  import android
  android.init() # Usually this and the next line would be put into an if statement after this, I didn't see the point and put it here instead.
  android.map_key(4, pygame.K_ESCAPE)
  print android.KEYCODE_BACK, pygame.K_ESCAPE
except ImportError: android = None
except AttributeError: # I have a module on my desktop called "android" I suspect this is part of the SDK and meant for testing, I dont really care at the moment.
  del android
  android = None

global screenupdates
screenupdates = []
global running
running = True

def userquit():
  pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
  return pygame.event.Event(pygame.QUIT, {})

def render_textrect(string, font, rect, text_color, background = (0,0,0,0), justification=0):
  """Returns a surface containing the passed text string, reformatted
  to fit within the given rect, word-wrapping as necessary. The text
  will be anti-aliased.

  Takes the following arguments:

  string - the text you wish to render. \n begins a new line.
  font - a Font object
  rect - a rectstyle giving the size of the surface requested.
  text_color - a three-byte tuple of the rgb value of the
               text color. ex (0, 0, 0) = BLACK
  background - a three-byte tuple of the rgb value of the surface.
                  mikef: a four-byte tuple of the RGB*A* value of the surface. Defaults to pure transparency.
  justification - 0 (default) left-justified
                  1 horizontally centered
                  2 right-justified

  Returns the following values:

  Success - a surface object with the text rendered onto it.
  Failure - raises a TextRectException if the text won't fit onto the surface.
         mikef: I turned off this failure and just let it silently drop off what doesn't fit.
  """

  final_lines = []

  requested_lines = string.splitlines()

  # Create a series of lines that will fit on the provided
  # rectangle.

  for requested_line in requested_lines:
    if font.size(requested_line)[0] > rect.width:
      words = requested_line.split(' ')
#     # if any of our words are too long to fit, return.
#     for word in words:
#       if font.size(word)[0] >= rect.width:
#         raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
      # Start a new line
      accumulated_line = words[0] + " "
      for word in words[1:]:
        test_line = accumulated_line + word + " "
          # Build the line while the words fit.    
        if font.size(test_line)[0] < rect.width:
          accumulated_line = test_line 
        else:
          final_lines.append(accumulated_line) 
          accumulated_line = word + " " 
      final_lines.append(accumulated_line)
    else: 
      final_lines.append(requested_line) 

  # Let's try to write the text out on the surface.
  if rect.width < font.size(max(final_lines, key=font.size))[0]:
    width = rect.width
  else:
    width = font.size(max(final_lines, key=font.size))[0]
  if rect.height < font.size(final_lines[0])*len(final_lines):
    height = rect.height
  else:
    height = font.size(final_lines[0])*len(final_lines)

  if type(background) == tuple:
    surface = pygame.Surface((width, height), pygame.SRCALPHA) 
    surface.fill(background) 
  elif type(background) == pygame.Surface:
    surface = background
  else:
    raise Exception, "background must be either a colour tuple or a surface, you gave a %s" % type(background)

  accumulated_height = 0 
  templist = []
  for line in final_lines: 
#   if accumulated_height + font.size(line)[1] >= rect.height:
#     raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
#    if line != "":
    tempsurface = font.render(line, 1, text_color)
    templist.append(tempsurface)
    accumulated_height += font.size(line)[1]
  if justification == 3 and surface.get_height() > accumulated_height:
    pass
    accumulated_height = (surface.get_height()-accumulated_height)/2
    for tempsurface in templist:
      surface.blit(tempsurface, ((surface.get_width() - tempsurface.get_width()) / 2, accumulated_height))
      accumulated_height += font.size(line)[1]
  else:
    accumulated_height = 0
    for tempsurface in templist:
      if justification == 0:
        surface.blit(tempsurface, (0, accumulated_height))
      elif justification == 1 or justification == 3:
        surface.blit(tempsurface, ((surface.get_width() - tempsurface.get_width()) / 2, accumulated_height))
      elif justification == 2:
        surface.blit(tempsurface, (surface.get_width() - tempsurface.get_width(), accumulated_height))
      else:
        raise TextRectException, "Invalid justification argument: " + str(justification)
      accumulated_height += font.size(line)[1]
  return surface

class textmenu():
  clickables = {}
  realmenuitems = []
  selected = None
  def __init__(self, menuitems = None):
    self.font = pygame.font.Font(fontname, 36)
    return self.render(menuitems)
  def render(self, menuitems = None):
    global screenupdates
    # This puts the menu items on the screen and populates the necessary variables for selecting the items later.
    if not menuitems:
      for text, item, textpos in self.realmenuitems:
        if self.selected and self.selected[0] == text and self.selected[2] == textpos:
          surf = pygame.Surface(self.selected[2][2:4], pygame.SRCALPHA)
          surf.fill((0,0,0,50))
          surf.blit(self.selected[0], (0,0))
          screen.blit(surf, self.selected[2])
        screen.blit(text, textpos)
        screenupdates.append(textpos)
    else:
      itemheight = screen.get_height()/len(menuitems)
      itemnum = -1
      for item in menuitems:
        itemnum += 1
        text = self.font.render(item[0], 1, (255,255,255))
        textpos = text.get_rect(centerx=screen.get_width()/2,centery=(itemheight*itemnum)+(itemheight/2))
        self.clickables.update({tuple(textpos[0:4]): itemnum})#(text, item[1])})
        self.realmenuitems.append((text, item[1], textpos))
        screen.blit(text, textpos)
        screenupdates.append(textpos)
    pygame.display.update(screenupdates)
    screenupdates = []
  def mouseselect(self, mousepos):
    global screenupdates
    # This will highlight an item based on the current mouse location, this should be called anytime the mouse moves.
    item = pygame.Rect(mousepos[0],mousepos[1],0,0).collidedict(self.clickables)
    if item and self.realmenuitems[item[1]] != self.selected:
      if self.selected:
        screen.blit(background.subsurface(self.selected[2]), self.selected[2])
        screen.blit(self.selected[0], self.selected[2])
        screenupdates.append(self.selected[2])
      self.selected = self.realmenuitems[item[1]]
      surf = pygame.Surface(self.selected[2][2:4], pygame.SRCALPHA)
      surf.fill((0,0,0,75))
      screen.blit(surf, self.selected[2])
      screen.blit(self.selected[0], self.selected[2])
      screenupdates.append(self.selected[2])
      pygame.display.update(screenupdates)
      screenupdates = []
    elif not item and self.selected != None:
      screen.blit(background.subsurface(self.selected[2]), self.selected[2])
      screen.blit(self.selected[0], self.selected[2])
      screenupdates.append(self.selected[2])
      pygame.display.update(screenupdates)
      screenupdates = []
      self.selected = None
    return self.selected
  def keyselect(self, direction):
    global screenupdates
    # This will highlight the next/previous item based on keypress, this should be called with True for next (down), and False for previous (up).
    if not self.selected and direction == False:
      self.selected = self.realmenuitems[-1]
    elif not self.selected and direction == True:
      self.selected = self.realmenuitems[0]
    elif self.selected:
      screen.blit(background.subsurface(self.selected[2]), self.selected[2])
      screen.blit(self.selected[0], self.selected[2])
      screenupdates.append(self.selected[2])
      if direction == False:
        try: self.selected = self.realmenuitems[self.realmenuitems.index(self.selected)-1]
        except IndexError: self.selected = self.realmenuitems[-1]
      elif direction == True:
        try: self.selected = self.realmenuitems[self.realmenuitems.index(self.selected)+1]
        except IndexError: self.selected = self.realmenuitems[0]
    surf = pygame.Surface(self.selected[2][2:4], pygame.SRCALPHA)
    surf.fill((0,0,0,75))
    screen.blit(surf, self.selected[2])
    screen.blit(self.selected[0], self.selected[2])
    screenupdates.append(self.selected[2])
    pygame.display.update(screenupdates)
    screenupdates = []
  def action(self, args = None):
    # This will action the highlighted item.
    if self.selected != None:
      if type(self.selected[1]) == str:
        print self.selected[1]
      else:
        if args != None:
          out = self.selected[1](args)
        else:
          out = self.selected[1]()
        self.render()
        return out
##### End class textmenu()

class filemenu():
  clickables = {}
  itemsinfo = {'../': {'file': False, 'title': '../', 'itemnum': 0}}
  selected = [None, None]
  pagerows = [[]]
  items = []
  cwd = './'
  rowoffset = 0
  def __init__(self):
    self.font = pygame.font.Font(fontname, 30)
    self.builditems()
    self.render()
    self.loop()
  def customsortkey(self, item):
    newitem = item
    itemHasDigit = False
    for num in string.digits:
      if num in newitem:
        itemHasDigit = True
        break
    if not itemHasDigit:
      if ' - ' in newitem:
        newitem = newitem.replace(' - ', ' 1 - ')
      elif ': ' in newitem:
        newitem = newitem.replace(': ', '1: ')
      else:
        newitem = ' 1.'.join(newitem.rsplit('.', 1))
    if newitem.lower().startswith('the '):
      newitem = newitem[4:]
    return newitem
  def builditems(self, directory = './'):
    self.items = []
    if not directory == rootdir and not (directory == './' and os.getcwd() == rootdir):
      self.items.append('../')
      self.itemsinfo['../']['filename'] = directory+'../'
    else:
      self.itemsinfo['../']['filename'] = '../'
    directories = []
    files = []
    for item in os.listdir(directory):
      if not item.startswith('.') and os.access(directory+item, os.R_OK):
        if os.path.isdir(directory+item):
          directories.append(item + '/')
        else:
          files.append(item)
    directories.sort(key=self.customsortkey)
    files.sort(key=self.customsortkey)
    for item in directories:
      if not directory+item in self.items:
        self.items.append(directory+item)
        if not self.itemsinfo.has_key(directory+item):
          self.itemsinfo[directory+item] = {}
          self.itemsinfo[directory+item]['file'] = False
          self.itemsinfo[directory+item]['title'] = item
          self.itemsinfo[directory+item]['filename'] = directory+item + '/'
          if not self.itemsinfo[directory+item].has_key('thumb'):
            for extension in ['.jpg', '.png', '.jpeg', '.gif']:
              for filename in ['folder'+extension, '.folder'+extension, 'folder'+extension.upper(), '.folder'+extension.upper()]:
                if os.path.isfile(directory + item + filename) and os.access(directory + item + filename, os.R_OK):
                  self.itemsinfo[directory+item]['thumb'] = directory + item + filename
                  break
        self.itemsinfo[directory+item]['itemnum'] = self.items.index(directory+item)
    for filename in files:
      if not directory+filename in self.items:
        item = filename.rpartition('.')
        if item[1] == '.':
          item = item[0]
        else:
          item = item[2]
        try: ftype = mimetypes.guess_type(filename)[0].split('/')[0]
        except AttributeError: ftype = 'Unknown'
        if ftype == 'video':
          self.items.append(directory+item)
          if not self.itemsinfo.has_key(directory+item):
            self.itemsinfo[directory+item] = {}
          self.itemsinfo[directory+item]['file'] = True
          self.itemsinfo[directory+item]['title'] = item
          self.itemsinfo[directory+item]['filename'] = directory+filename
          self.itemsinfo[directory+item]['itemnum'] = self.items.index(directory+item)
        elif ftype == 'image':
          if not self.itemsinfo.has_key(directory+item):
            self.itemsinfo[directory+item] = {}
          self.itemsinfo[directory+item]['thumb'] = directory+filename
        elif filename[-5:] == '.info':
          if not self.itemsinfo.has_key(directory+item):
            self.itemsinfo[directory+item] = {}
          self.itemsinfo[directory+item]['info'] = directory+filename
  def render(self, directory = cwd, rowoffset = 0):
    global screenupdates
    screen.blit(background, (0,0))
    pygame.display.update()
    titleoffset = self.font.size('')[1]
    vertborder = 50
    horizborder = 75
    screenheight = screen.get_height()-titleoffset-vertborder
    screenwidth = screen.get_width()-horizborder
    itemheight = 110 #5 on 1280 #210 #280 # 5 on 1050 vertical resolution
    itemwidth = 190 #6 on 720 #280 # 6 on 1680 horizontal resolution
    numcols = screenwidth/itemwidth
    numrows = screenheight/itemheight
    self.pagerows = []
    rowspace = (screenheight-(numrows*itemheight))/numrows
    colspace = (screenwidth-(numcols*itemwidth))/numcols
    self.titleoffset = colspace, rowspace/4
    if rowoffset < 0 and len(self.items) > (numrows*numcols):
      rowoffset = -(((numrows*numcols)-len(self.items))/numcols)
    elif rowoffset > -(((numrows*numcols)-len(self.items))/numcols):
      rowoffset = 0
    itemnum = -1
    self.clickables = {}
    brake = False
    if True: # I'm simply using this as a seperater because I'm currently working on this section.
      butbg = pygame.Surface((itemwidth,itemheight), pygame.SRCALPHA)
      ellipse_width=itemwidth/9
      ellipse_height=itemheight/9
      start_angle = 0
      pygame.draw.ellipse(butbg, (0,0,0,50), (0,0,ellipse_width,ellipse_height), 0)
      pygame.draw.ellipse(butbg, (0,0,0,50), (0,butbg.get_height()-ellipse_height,ellipse_width,ellipse_height), 0)
      pygame.draw.ellipse(butbg, (0,0,0,50), (butbg.get_width()-ellipse_width,butbg.get_height()-ellipse_height,ellipse_width,ellipse_height), 0)
      butbg.subsurface((ellipse_width/2,butbg.get_height()-(ellipse_height/2),butbg.get_width()-ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      butbg.subsurface((0,ellipse_height/2,ellipse_width/2,butbg.get_height()-ellipse_height)).fill((0,0,0,50))

      filebutbg = butbg.copy()
      filebutbg.subsurface((ellipse_width/2,ellipse_height/2,filebutbg.get_width()-(ellipse_width/2),filebutbg.get_height()-ellipse_height)).fill((0,0,0,50))
      filebutbg.subsurface((ellipse_width/2,0,filebutbg.get_width()-ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      pygame.draw.ellipse(filebutbg, (0,0,0,50), (filebutbg.get_width()-ellipse_width,0,ellipse_width,ellipse_height), 0)

      dirbutbg = butbg.copy()
      pygame.draw.ellipse(dirbutbg, (0,0,0,50), (ellipse_width,0,ellipse_width,ellipse_height), 0)
      dirbutbg.subsurface((ellipse_width/2,0,ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      dirbutbg.subsurface((ellipse_width/2,ellipse_height/2,dirbutbg.get_width()-ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      dirbutbg.subsurface((ellipse_width/2,ellipse_height,dirbutbg.get_width()-(ellipse_width/2),dirbutbg.get_height()-(ellipse_height*1.5))).fill((0,0,0,50))
      pygame.draw.ellipse(dirbutbg, (0,0,0,50), (dirbutbg.get_width()-ellipse_width,ellipse_height/2,ellipse_width,ellipse_height), 0)
    while True:
      if not itemnum < (rowoffset*numcols)-1:
        for rownum in xrange(numrows):
          row = []
          for colnum in xrange(numcols):
            itemnum += 1
            try: item = self.items[itemnum]
            except IndexError:
              brake = True
              break
#            while not self.itemsinfo[item].has_key('title'):
#              itemnum += 1
#              try: item = self.items[itemnum]
#              except IndexError:
#                brake = True
#                break
            if self.itemsinfo[item].has_key('file') and self.itemsinfo[item]['file'] == False:
              surf = dirbutbg.copy()
            else:
              surf = filebutbg.copy()
            if not self.itemsinfo[item].has_key('surface'):
              if self.itemsinfo[item].has_key('thumb'):
                thumb = pygame.image.load(self.itemsinfo[item]['thumb']).convert()
                if self.itemsinfo[item].has_key('file') and self.itemsinfo[item]['file'] == False:
                  rect = thumb.get_rect().fit((0,0,itemwidth-ellipse_width,itemheight-(ellipse_height*1.5)))
                  thumb = pygame.transform.smoothscale(thumb.convert_alpha(), (rect[2], rect[3]))
                  surf.blit(thumb, thumb.get_rect(center=(surf.get_width()/2,(surf.get_height()+(ellipse_width/4))/2)))
                else:
                  rect = thumb.get_rect().fit((0,0,itemwidth-ellipse_width,itemheight-ellipse_height))
                  thumb = pygame.transform.smoothscale(thumb.convert_alpha(), (rect[2], rect[3]))
                  surf.blit(thumb, thumb.get_rect(center=(surf.get_width()/2,surf.get_height()/2)))
              else:
                thumb = render_textrect(self.itemsinfo[item]['title'], self.font, pygame.rect.Rect((0,0,itemwidth-ellipse_width,itemheight-ellipse_height)), (255,255,255), (0,0,0,0))
                if self.itemsinfo[item].has_key('file') and self.itemsinfo[item]['file'] == False:
                  surf.blit(thumb, thumb.get_rect(left=ellipse_width/2, top=ellipse_height))
                else:
                  surf.blit(thumb, thumb.get_rect(left=ellipse_width/2, top=ellipse_height/2))
              self.itemsinfo[item]['surface'] = surf
            top = (rownum*itemheight)+(rownum*rowspace)+(rowspace/2)+titleoffset+(vertborder/2)
            left = (colnum*itemwidth)+(colnum*colspace)+(colspace/2)+(horizborder/2)
            self.itemsinfo[item]['buttonloc'] = self.itemsinfo[item]['surface'].get_rect(top=top, left=left)
            self.clickables.update({tuple(self.itemsinfo[item]['buttonloc'][0:4]): item})
            col = item
            screen.blit(self.itemsinfo[item]['surface'], self.itemsinfo[item]['buttonloc'])
            pygame.display.update(self.itemsinfo[item]['buttonloc'])
            row.append(col)
          if row != []:
            self.pagerows.append(row)
          if brake:
            break
        break
      else:
        itemnum = itemnum+numcols
    self.rowoffset = rowoffset
  def mouseselect(self, mousepos):
    global screenupdates
    try: item = pygame.Rect(mousepos[0],mousepos[1],0,0).collidedict(self.clickables)[1]
    except TypeError: item = None
    if item:# and item != self.selected[1]:
      return self.select(self.items.index(item))
  def keyselect(self, direction):
    global screenupdates
    prevselected = None
    if self.selected[1]:
      screen.blit(background.subsurface(self.itemsinfo[self.selected[1]]['buttonloc']), self.itemsinfo[self.selected[1]]['buttonloc'])
      screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
      screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
    if not self.selected[0] or not self.selected[1]:
      if direction == 0:
        itemnum = self.pagerows[-1][0]['itemnum']
      elif direction == 1:
        itemnum = self.pagerows[0][0]['itemnum']
      elif direction == 2:
        itemnum = self.pagerows[-1][-1]['itemnum']
      elif direction == 3:
        itemnum = self.pagerows[0][0]['itemnum']
    elif self.selected[0] and self.selected[1]:
      if direction == 0:
        itemnum = self.items.index(self.selected[1])-len(self.pagerows[0])
      elif direction == 1:
        itemnum = self.items.index(self.selected[1])+len(self.selected[0])
      elif direction == 2:
        itemnum = self.items.index(self.selected[1])-1
      elif direction == 3:
        itemnum = self.items.index(self.selected[1])+1
    self.select(itemnum)
  def select(self, itemnum):
    global screenupdates
    if self.selected[0] in self.pagerows and self.selected[1] in self.pagerows[self.pagerows.index(self.selected[0])]:
      screen.blit(background.subsurface(self.itemsinfo[self.selected[1]]['buttonloc']), self.itemsinfo[self.selected[1]]['buttonloc'])
      screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
      screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
    if itemnum == None:
      pygame.display.update(screenupdates)
      screenupdates = []
      return
    if itemnum < self.itemsinfo[self.pagerows[0][0]]['itemnum']:
      self.scroll(0,1)
      if itemnum < 0:
        if itemnum+(len(self.pagerows[0])-len(self.pagerows[-1])) >= 0:
          itemnum = -1
        else:
          itemnum += (len(self.pagerows[0])-len(self.pagerows[-1]))
    elif itemnum > self.itemsinfo[self.pagerows[-1][-1]]['itemnum']:
      if itemnum > len(self.items)-1:
        itemnum -= len(self.items)
        if not self.pagerows[-1][-1] == self.items[-1]:
          self.scroll(1,1)
        if not self.selected[1] in self.pagerows[-1] and not itemnum > len(self.pagerows[0])-len(self.pagerows[-1]):
          itemnum = self.items.index(self.pagerows[-1][-1])
        else:
          self.scroll(1,1)
      elif itemnum > self.itemsinfo[self.pagerows[-1][-1]]['itemnum']+len(self.pagerows[0]):
        distance = (itemnum-self.itemsinfo[self.pagerows[-1][-1]]['itemnum'])/float(len(self.pagerows[0]))
        self.scroll(1,distance)
      else:
        self.scroll(1,1)
    item = self.items[itemnum]
    for row in self.pagerows:
      if item in row:
        rownum = self.pagerows.index(row)
        colnum = row.index(item)
        break
    self.selected = [self.pagerows[rownum], self.pagerows[rownum][colnum]]
    if True: # I'm simply using this as a seperater because I'm currently working on this section.
      butsel = pygame.Surface(self.itemsinfo[self.selected[1]]['buttonloc'][2:4], pygame.SRCALPHA)
      ellipse_width=butsel.get_width()/9
      ellipse_height=butsel.get_height()/9
      start_angle = 0
      pygame.draw.ellipse(butsel, ((127,127,0)), (0,0,ellipse_width,ellipse_height), 0)
      pygame.draw.ellipse(butsel, ((127,127,0)), (0,butsel.get_height()-ellipse_height,ellipse_width,ellipse_height), 0)
      pygame.draw.ellipse(butsel, ((127,127,0)), (butsel.get_width()-ellipse_width,butsel.get_height()-ellipse_height,ellipse_width,ellipse_height), 0)
      butsel.subsurface((ellipse_width/2,butsel.get_height()-(ellipse_height/2),butsel.get_width()-ellipse_width,ellipse_height/2)).fill(((127,127,0)))
      butsel.subsurface((0,ellipse_height/2,ellipse_width/2,butsel.get_height()-ellipse_height)).fill(((127,127,0)))

      if self.itemsinfo[item].has_key('file') and self.itemsinfo[item]['file'] == False:
        pygame.draw.ellipse(butsel, ((127,127,0)), (ellipse_width,0,ellipse_width,ellipse_height), 0)
        butsel.subsurface((ellipse_width/2,0,ellipse_width,ellipse_height/2)).fill(((127,127,0)))
        butsel.subsurface((ellipse_width/2,ellipse_height/2,butsel.get_width()-ellipse_width,ellipse_height/2)).fill(((127,127,0)))
        butsel.subsurface((ellipse_width/2,ellipse_height,butsel.get_width()-(ellipse_width/2),butsel.get_height()-(ellipse_height*1.5))).fill(((127,127,0)))
        pygame.draw.ellipse(butsel, ((127,127,0)), (butsel.get_width()-ellipse_width,ellipse_height/2,ellipse_width,ellipse_height), 0)
      else:
        butsel.subsurface((ellipse_width/2,ellipse_height/2,butsel.get_width()-(ellipse_width/2),butsel.get_height()-ellipse_height)).fill(((127,127,0)))
        butsel.subsurface((ellipse_width/2,0,butsel.get_width()-ellipse_width,ellipse_height/2)).fill(((127,127,0)))
        pygame.draw.ellipse(butsel, ((127,127,0)), (butsel.get_width()-ellipse_width,0,ellipse_width,ellipse_height), 0)
      butsel.blit(self.itemsinfo[self.selected[1]]['surface'], (0,0))
      screen.blit(butsel, self.itemsinfo[self.selected[1]]['buttonloc'])
    screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
    title = self.font.render(self.itemsinfo[self.selected[1]]['title'], 1, (255,255,255))
    titlepos = title.get_rect(topleft=self.titleoffset, width=screen.get_width()-self.titleoffset[0])
    screen.blit(background.subsurface(titlepos), titlepos)
    screen.blit(title,titlepos)
    screenupdates.append(titlepos)
    pygame.display.update(screenupdates)
    screenupdates = []
    return itemnum
  def scroll(self, direction, distance = 1):
    if direction:
      self.rowoffset = self.rowoffset+distance
    else:
      self.rowoffset = self.rowoffset-distance
    self.render(rowoffset=self.rowoffset)
  def loop(self):
    global running
    self.select(0)
    while running == True:
      try: event = pygame.event.wait()
      except KeyboardInterrupt: event = userquit()
      if event.type == pygame.QUIT:
        running = False
        pygame.quit()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
        self.scroll(0,len(self.pagerows))
        self.select(self.items.index(self.selected[1])-(len(self.pagerows[0])*len(self.pagerows)))
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
        self.scroll(1,len(self.pagerows))
        self.select(self.items.index(self.selected[1])+(len(self.pagerows[0])*len(self.pagerows)))
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        self.keyselect(0)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        self.keyselect(1)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
        self.keyselect(2)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
        self.keyselect(3)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
        surf = render_textrect('Movie player is running\nPress the back button to quit', pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
        screenbkup = screen.copy()
        screen.blit(surf, (0,0))
        pygame.display.update()
        player = movieplayer(self.itemsinfo[self.selected[1]]['filename'])
        player.play()
        player.loop()
        screen.blit(screenbkup, (0,0))
        pygame.display.update()
      elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
        self.action(self.selected[1])
      elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
        if self.action('../') == pygame.QUIT:
          screen.blit(background, (0,0)) # Put the background on the window.
          pygame.display.update() # Update the display.
          return
      elif event.type == pygame.MOUSEMOTION:
        self.mouseselect(event.pos)
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        released = False
        scrolled = False
        origpos = event.pos
        item = self.mouseselect(event.pos)
        while released != True:
          event = pygame.event.wait()
          if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if not item == None and self.mouseselect(event.pos) == item and not scrolled:
              self.action(self.selected[1])
            released = True
            break
          if origpos[1] >= event.pos[1]+140:
            scrolled = True
            origpos = event.pos
            self.scroll(1,1)
          elif origpos[1] <= event.pos[1]-140:
            scrolled = True
            origpos = event.pos
            self.scroll(0,1)
      elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
        self.scroll(event.button==5, 1)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
        pygame.display.toggle_fullscreen()
      else:
        if android:
          print 'event', event
          print android.check_pause()
  def action(self, selected):
    if selected == '../' and (self.itemsinfo[selected]['filename'] == '../'):
      return pygame.QUIT
    elif self.itemsinfo[selected]['file']:
#      surf = render_textrect('Movie player is running\nPress the back button to quit', pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
      screenbkup = screen.copy()
      info = movieinfo(self.itemsinfo[selected])
      info.display()
      info.loop()
#      screen.blit(surf, (0,0))
#      pygame.display.update()
#      player = movieplayer(self.itemsinfo[selected]['filename'])
#      player.play()
#      player.loop()
##      pygame.display.set_mode((0,0), pygame.FULLSCREEN|pygame.HWSURFACE)
      screen.blit(screenbkup, (0,0))
      pygame.display.update()
    elif not self.itemsinfo[selected]['file']:
      self.select(None)
      filename = self.itemsinfo[selected]['filename'].replace('//', '/')
      if '../' in filename:
        filename = filename[:filename.rindex('../')].rsplit('/', 2)[0]+'/'
      self.builditems(directory=filename)
      self.selected = [None, None]
      self.render()
      if self.cwd in self.items:
        self.select(self.items.index(self.cwd))
      else:
        self.select(0)
      self.cwd = filename
##### End class filemenu()

class movieinfo():
  def __getitem__(self, item):
    if item.startswith('int:'):
      item = item[len('int:'):]
      if self.config.has_section('local') and self.config.has_option('local', item):
        return self.config.getint('local', item)
      elif self.iteminfo.has_key(item):
        return int(self.iteminfo[item])
      elif self.config.has_section('IMDB') and self.config.has_option('IMDB', item):
        return self.config.getint('IMDB', item)
      else:
        return 0
    elif item.startswith('float:'):
      item = item[len('float:'):]
      if self.config.has_section('local') and self.config.has_option('local', item):
        return self.config.getfloat('local', item)
      elif self.iteminfo.has_key(item):
        return float(self.iteminfo[item])
      elif self.config.has_section('IMDB') and self.config.has_option('IMDB', item):
        return self.config.getfloat('IMDB', item)
      else:
        return 0.0
    elif item.startswith('boolean:'):
      item = item[len('boolean:'):]
      if self.config.has_section('local') and self.config.has_option('local', item):
        return self.config.getboolean('local', item)
      elif self.iteminfo.has_key(item):
        return boolean(self.iteminfo[item])
      elif self.config.has_section('IMDB') and self.config.has_option('IMDB', item):
        return self.config.getboolean('IMDB', item)
      else:
        return False
    if item.startswith('list:'):
      item = item[len('list:'):]
      if self.config.has_section('local') and self.config.has_option('local', item):
        return self.config.get('local', item).rstrip(' | ').split(' | ')
      elif self.iteminfo.has_key(item):
        if type(self.iteminfo[item]) == str:
          return self.iteminfo[item].rstrip(' | ').split(' | ')
        else:
          return list(self.iteminfo[item])
      elif self.config.has_section('IMDB') and self.config.has_option('IMDB', item):
        return self.config.get('IMDB', item).rstrip(' | ').split(' | ')
      else:
        return ['Unknown']
    else:
      if item.startswith('str:'): item = item[len('str:'):]
      if self.config.has_section('local') and self.config.has_option('local', item):
        return self.config.get('local', item).rstrip(' | ')
      elif self.iteminfo.has_key(item):
        return self.iteminfo[item]
      elif self.config.has_section('IMDB') and self.config.has_option('IMDB', item):
        return self.config.get('IMDB', item).rstrip(' | ')
      else:
        return 'Unknown'
  def __setitem__(self, item, newvalue):
    if type(newvalue) == list:
      newvalue = ' | '.join(newvalue)
    if self.iteminfo.has_key('info'):
      self.config.read(self.iteminfo['info'])
    else:
      self.iteminfo['info'] = '.'.join(self['filename'].split('.')[:-1])+'.info'
    if not self.config.has_section('local'):
      self.config.add_section('local')
    self.config.set('local', item, newvalue)
    if os.access(self.iteminfo['info'], os.W_OK):
      try: configfile = open(self.iteminfo['info'], 'w')
      except IOError: return
      self.config.write(configfile)
      configfile.flush()
      configfile.close()
  def __delitem__(self, item):
    if not self.iteminfo.has_key('info'):
      return
    self.config.read(self.iteminfo['info'])
    if not self.config.has_section('local'):
      self.config.add_section('local')
    self.config.set('local', item, None)
    if os.access(self.iteminfo['info'], os.W_OK):
      try: configfile = open(self.iteminfo['info'], 'w')
      except IOError: return
      self.config.write(configfile)
      configfile.flush()
      configfile.close()
  def __contains__(self, item):
    if self.config.has_section('local') and self.config.has_option('local', item):
      return True
    elif self.iteminfo.has_key(item):
      return True
    elif self.config.has_section('IMDB') and self.config.has_option('IMDB', item):
      return True
    else:
      return False
  def __init__(self, iteminfo):
    global fontname
    self.font = pygame.font.Font(fontname, 30)
    self.iteminfo = iteminfo
    self.config = ConfigParser.ConfigParser()
    if self.iteminfo.has_key('info'):
      self.config.read(self.iteminfo['info'])
  def display(self):
    global screenupdates
    screen.blit(background, (0,0))
    pygame.display.update()
    if 'thumb' in self:
      thumb = pygame.image.load(self['thumb']).convert()
      thumbrect = thumb.get_rect().fit(screen.get_rect(width=(screen.get_width()/100)*95, height=(screen.get_height()/100)*95, center=(screen.get_width()/2, screen.get_height()/2)))
      thumb = pygame.transform.smoothscale(thumb.convert_alpha(), (thumbrect[2], thumbrect[3]))
      screen.blit(thumb, thumb.get_rect(center=(screen.get_width()/2,screen.get_height()/2)))
    title = self.font.render(self['title'], 1, (255,255,255))
    screen.blit(title,title.get_rect(midtop=(screen.get_width()/2,self.font.size('')[1])))
    vertborder = screen.get_height()/20
    horizborder = (screen.get_width()-self.font.size('')[1]*3)/20
    infosurf = pygame.surface.Surface((screen.get_width()-(horizborder*2),screen.get_height()-(self.font.size('')[1]*3)-vertborder), pygame.SRCALPHA)
    directorsurf = infosurf.subsurface(infosurf.get_rect(top=self.font.get_height()/2, height=self.font.get_height()))
    directorsurf.fill((0,0,0,200))
    render_textrect('Directed by: '+self['director'], self.font, directorsurf.get_rect(), (255,255,255), directorsurf, 0)
    if not self['boolean:watched']: render_textrect('Not seen', self.font, directorsurf.get_rect(), (255,255,255), directorsurf, 2)
    miscsurf = infosurf.subsurface(infosurf.get_rect(top=(infosurf.get_height()-(self.font.get_height()/2))-(self.font.get_height()*2), height=self.font.get_height()*2))
    miscsurf.fill((0,0,0,100), (0,0,miscsurf.get_width(),self.font.get_height()))
    miscsurf.fill((0,0,0,200), (0,self.font.get_height(),miscsurf.get_width(),self.font.get_height()))
    runtime = self['list:runtimes']
    if runtime == ['Unknown']:
      runtime = 0
    elif runtime[0].isdigit():
      runtime = int(runtime[0])
    else:
      if self['list:runtimes'][0].split(':')[0].strip(' ').isdigit():
        runtime = int(self['list:runtimes'][0].split(':')[0].strip(' '))
      elif self['list:runtimes'][0].split(':')[1].strip(' ').isdigit():
        runtime = int(self['list:runtimes'][0].split(':')[1].strip(' '))
      else:
        runtime = ', '.join(runtime)
    render_textrect('Runtime\n%s minutes' % runtime, self.font, miscsurf.get_rect(), (255,255,255), miscsurf, 0)
    render_textrect('Year\n%d' % self['int:year'], self.font, miscsurf.get_rect(), (255,255,255), miscsurf, 1)
    render_textrect('User rating\n%2.1f' % self['float:rating'], self.font, miscsurf.get_rect(), (255,255,255), miscsurf, 2)
    plotsurf = infosurf.subsurface(infosurf.get_rect(height=infosurf.get_height()-(self.font.get_height()*5), top=self.font.get_height()*2))
    plotsurf.fill((0,0,0,150))
    plots = ''
    for plot in self['list:plot']:
      if not plot == '' and not plot == 'Unknown':
        if '::' in plot:
          author = plot.split('::')[-1]
          plot = '::'.join(plot.split('::')[0:-1])
        else:
          author = 'Anonymous'
        plots += 'Plot written by '+author+':\n      '+plot+'\n\n'
    if plots == '':
      plots = 'None'
    render_textrect(plots, self.font, plotsurf.get_rect(), (255,255,255), plotsurf, 0)
    ##FINDME###
#    infosurf.fill((0,0,0,150))
#    if self.info.has_key('plot'):
#      plotsurf = render_textrect(self.info['plot'], self.font, infosurf.get_rect(), (255,255,255), (0,0,0,0), 0)
#      infosurf.blit(plotsurf, (0,0))
#    if self.info.has_key('runtimes'):
#      runtimesurf = self.font.render('Runtime: '+self.info['runtimes'], 1, (255,255,255))
#      infosurf.blit(runtimesurf, runtimesurf.get_rect(left=0, bottom=infosurf.get_height()))
    screen.blit(infosurf,(horizborder,self.font.size('')[1]*3,))
    pygame.display.update()
    if False:
      ellipse_width=itemwidth/9
      ellipse_height=itemheight/9
      start_angle = 0
      pygame.draw.ellipse(butbg, (0,0,0,50), (0,0,ellipse_width,ellipse_height), 0)
      pygame.draw.ellipse(butbg, (0,0,0,50), (0,butbg.get_height()-ellipse_height,ellipse_width,ellipse_height), 0)
      pygame.draw.ellipse(butbg, (0,0,0,50), (butbg.get_width()-ellipse_width,butbg.get_height()-ellipse_height,ellipse_width,ellipse_height), 0)
      butbg.subsurface((ellipse_width/2,butbg.get_height()-(ellipse_height/2),butbg.get_width()-ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      butbg.subsurface((0,ellipse_height/2,ellipse_width/2,butbg.get_height()-ellipse_height)).fill((0,0,0,50))

      filebutbg = butbg.copy()
      filebutbg.subsurface((ellipse_width/2,ellipse_height/2,filebutbg.get_width()-(ellipse_width/2),filebutbg.get_height()-ellipse_height)).fill((0,0,0,50))
      filebutbg.subsurface((ellipse_width/2,0,filebutbg.get_width()-ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      pygame.draw.ellipse(filebutbg, (0,0,0,50), (filebutbg.get_width()-ellipse_width,0,ellipse_width,ellipse_height), 0)

      dirbutbg = butbg.copy()
      pygame.draw.ellipse(dirbutbg, (0,0,0,50), (ellipse_width,0,ellipse_width,ellipse_height), 0)
      dirbutbg.subsurface((ellipse_width/2,0,ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      dirbutbg.subsurface((ellipse_width/2,ellipse_height/2,dirbutbg.get_width()-ellipse_width,ellipse_height/2)).fill((0,0,0,50))
      dirbutbg.subsurface((ellipse_width/2,ellipse_height,dirbutbg.get_width()-(ellipse_width/2),dirbutbg.get_height()-(ellipse_height*1.5))).fill((0,0,0,50))
      pygame.draw.ellipse(dirbutbg, (0,0,0,50), (dirbutbg.get_width()-ellipse_width,ellipse_height/2,ellipse_width,ellipse_height), 0)
  def loop(self):
    global running
    while running == True:
      try: event = pygame.event.wait()
      except KeyboardInterrupt: event = userquit()
      if event.type == pygame.QUIT:
        running = False
        pygame.quit()
      elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
        self.action()
      elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
        return
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        self.action()
  def action(self):
    if not os.path.isfile(str(self['filename'])):
      surf = render_textrect('This file does not seem to exist. Has it been deleted?\n'+str(self['filename']), pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
      screenbkup = screen.copy()
      screen.blit(surf, (0,0))
      pygame.display.update()
      time.sleep(5)
      screen.blit(screenbkup, (0,0))
      pygame.display.update()
      return
    screenbkup = screen.copy()
    surf = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
    surf.fill((0,0,0,225))
    screen.blit(surf, (0,0))
    render_textrect('Movie player is running.\n\nPress the back button to quit.', pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), screen, 3)
    pygame.display.update()
    player = movieplayer(self['filename'])
    player.play()
    player.loop()
    self['watched'] = True
    screen.blit(screenbkup, (0,0))
    pygame.display.update()
##### End class movieinfo()

class movieplayer():
  # I've tried to make this fairly compatible with the pygame.movie module, but there's a lot of features in this that are not in the pygame.movie module.
  # Also, I haven't really tested this compatibility or even used pygame.movie ever before.
  osd = None
  bmovl = None
  osd_visible = False
  paused = None
  time_pos = 0
  percent_pos = 0
  time_length = 0
  osd_percentage = -1
  osd_time_pos = -1
  osd_last_run = -1
  remapped_keys = {'ESC': 'ESCAPE', 'MOUSE_BTN2_DBL': 'ESCAPE', 'ENTER': 'RETURN'}
  video_resolution = (0,0)
  volume = 0
  threads = {}
  osdtype = 'time'
  def __init__(self, filename):
    global fontname
    self.font = pygame.font.Font(fontname, 18)
    self.filename = filename
  def procoutput(self):
    statusline = None
    response = None
    while not response == '' and not self.mplayer.stdout.closed:
      response = self.mplayer.stdout.read(1)+self.mplayer.stdout.readline().strip('\r\n')
      if response.startswith("No bind found for key '"):
        key = response.strip(' ')[len("No bind found for key '"):].rstrip('.').rstrip("'")
        if key in self.remapped_keys.keys(): key = self.remapped_keys[key]
        if 'K_'+key in dir(pygame):
          pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': eval('pygame.K_'+key)}))
          pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': eval('pygame.K_'+key)}))
        elif key.startswith('MOUSE_BTN'):
          try:
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': int(key.replace('MOUSE_BTN', ''))+1, 'pos': (0,0)}))
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': int(key.replace('MOUSE_BTN', ''))+1, 'pos': (0,0)}))
          except:
            print 'This try except block is temporary, I will put a proper fix in place.'
        elif key == 'CLOSE_WIN':
          pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
      elif response.startswith('ANS_') or response.startswith('ID_'):
        response = '_'.join(response.split('_')[1:]).lower()
        if response.startswith('exit'):
          break
        elif response == 'paused':
          self.paused = True
        elif response.startswith('pause='):
          self.paused = response.split('=')[-1] == 'yes'
        elif response.startswith('length='):
          self.time_length = float(response.split('=')[1])
        elif response.startswith('time_pos='):
          self.time_pos = float(response.split('=')[1])
          if not self.time_pos == 0 and not self.time_length == 0:
            self.percent_pos = self.time_pos/(self.time_length/100)
        elif response.startswith('volume='):
          self.volume = float(response.split('=')[1])
        elif response.startswith('video_width='):
          self.video_resolution = (int(response.split('=')[1]), self.video_resolution[1])
        elif response.startswith('video_height='):
          self.video_resolution = (self.video_resolution[0], int(response.split('=')[1]))
        elif response.startswith('video_resolution='):
          rawvidres = response.split('=')[1].strip("'")
          self.video_resolution = (int(rawvidres.split(' x ')[0]), int(rawvidres.split(' x ')[1]))
        elif response.startswith('sub_visibility='):
          if response.split('=')[1].strip("'") == 'yes': self.mplayer.stdin.write('osd_show_text "Subtitles enabled"\n')
          else: self.mplayer.stdin.write('osd_show_text "Subtitles disabled"\n')
      elif response.startswith('vf_bmovl: '):
        response = response[len('vf_bmovl: '):]
        if response.startswith('Opened fifo ') and self.bmovl == None:
          response = response[len('Opened fifo '):]
          self.bmovl = os.open(response[:response.rindex(' as FD ')], os.O_WRONLY)
  def play(self, loops=None, osd=True):
    # Starts playback of the movie. Sound and video will begin playing if they are not disabled. The optional loops argument controls how many times the movie will be repeated. A loop value of -1 means the movie will repeat forever.
#    surf = render_textrect('Movie player is running\nPress the back button to quit', pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
#    self.screenbkup = screen.copy()
#    screen.blit(surf, (0,0))
#    pygame.display.update()
    args = ['-really-quiet','-input','conf=/dev/null:nodefault-bindings','-msglevel','vfilter=5:identify=5:global=4:input=5:cplayer=0:statusline=0','-slave','-identify','-stop-xscreensaver','-volume','75','-idx']
    if len(sys.argv) > 1 and sys.argv[1] == '--no-sound': args += ['-ao', 'null']
    if windowed == False: args += ['-fs']
    if loops == 0:
      loops = None
    elif loops == -1:
      loops = 0
    if loops != None:
      args += ['-loop', str(loops)]
    if osd:
      bmovlfile = '/tmp/bmovl-%s-%s' % (os.geteuid(), os.getpid())
      os.mkfifo(bmovlfile)
      args += ['-osdlevel','0','-vf','bmovl=1:0:'+bmovlfile] #'-vc', '-ffodivx,-ffodivxvdpau,', 
    if os.path.isfile(os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+'-'+os.uname()[1]+'.save'):
      starttime = open(os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+'-'+os.uname()[1]+'.save', 'r').readline().strip('\n')
      if ';' in starttime:
        args += ['-volume', starttime.split(';')[1]]
        starttime = starttime.split(';')[0]
      args += ['-ss', starttime]
      try: os.remove(os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+'-'+os.uname()[1]+'.save')
      except OSError, (Errno, Errmsg):
        if Errno == 30:
          pass # Read-only, nothing I can do about it.
        else:
          raise OSError((Errno, Errmsg))
    elif os.path.isfile(os.path.dirname(self.filename)+'/'+self.filename+'-'+os.uname()[1]+'.save'):
      starttime = open(os.path.dirname(self.filename)+'/'+self.filename+'-'+os.uname()[1]+'.save', 'r').readline().strip('\n')
      if ';' in starttime:
        args += ['-volume', starttime.split(';')[1]]
        starttime = starttime.split(';')[0]
      args += ['-ss', starttime]
      try: os.remove(os.path.dirname(self.filename)+'/'+self.filename+'-'+os.uname()[1]+'.save')
      except OSError, (Errno, Errmsg):
        if Errno == 30:
          pass # Read-only, nothing I can do about it.
        else:
          raise OSError((Errno, Errmsg))
    self.mplayer = subprocess.Popen(['mplayer']+args+[self.filename],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1)
    if self.mplayer.poll() != None:
      raise Exception(mplayer.stdout.read())
#    if osd:
#      print 'opening bmovl'
#      self.bmovl = os.open(bmovlfile, os.O_WRONLY)
    self.mplayer.stdin.write('pausing_keep_force get_property pause\n')
    self.mplayer.stdin.write('pausing_keep_force get_property volume\n')
    thread = threading.Thread(target=self.procoutput, name='stdout')
    self.threads.update({thread.name: thread})
    thread.start()
#    while self.paused == None: pass
    threading.Thread(target=self.showosd, args=[5, 'time', True], name='showosd').start()
    return self.mplayer
  def pause(self):
    # This will temporarily stop or restart movie playback.
    self.mplayer.stdin.write('pausing_keep_force osd_show_text "Paused"\n')
    self.mplayer.stdin.write('pause\n')
  def skip(self, seconds):
    # Advance the movie playback time in seconds. This can be called before the movie is played to set the starting playback time. This can only skip the movie forward, not backwards. The argument is a floating point number.
    ### I've added being able to go backwards.
    self.showosd(2, osdtype='time')
    if type(seconds) == float or type(seconds) == int:
      if seconds < 0:
        self.mplayer.stdin.write('seek %s\n' % seconds)
      else:
        self.mplayer.stdin.write('seek +%s\n' % seconds)
    else:
      self.mplayer.stdin.write('seek %s\n' % seconds)
  def rewind(self, seconds=0):
    # Sets the movie playback position to the start of the movie. The movie will automatically begin playing even if it stopped.
    ### I've added being able to specify how far back to go
    if seconds == 0:
      self.mplayer.stdin.write('seek 0\n')
    elif type(seconds) == float or type(seconds) == int:
      self.mplayer.stdin.write('seek -%s\n' % seconds)
    else:
      self.mplayer.stdin.write('seek %s\n' % seconds)
  def render_frame(self,frame_number):
    # This takes an integer frame number to render. It attempts to render the given frame from the movie to the target Surface. It returns the real frame number that got rendered.
    ### Might be worth implementing via 'jpeg' (or similar) video output driver, I can't be bothered with it for now.
    return frame_number
  def get_frame(self):
    # Returns the integer frame number of the current video frame.
    ### Would take a lot of effort to make work in Mplayer.
    return 0
  def get_time(self):
    # Return the current playback time as a floating point value in seconds. This method currently seems broken and always returns 0.0.
    ### This is easy to implement so do so even though the pygame version fails.
    self.time_pos = None
    self.mplayer.stdin.write('pausing_keep_force get_property time_pos\n')
    while self.time_pos == None: pass
    return self.time_pos
  def get_busy(self):
    self.paused = None
    self.mplayer.stdin.write('pausing_keep_force get_property pause\n')
    while self.paused == None: pass
    return not self.paused
  def get_length(self):
    # Returns the length of the movie in seconds as a floating point value.
    return self.time_length
  def get_size(self):
    # Gets the resolution of the movie video. The movie will be stretched to the size of any Surface, but this will report the natural video size.
    return self.video_resolution
  def has_video(self):
    # True when the opened movie file contains a video stream.
    return True
  def has_audio(self):
    # True when the opened movie file contains an audio stream.
    return True
  def set_volume(self,volume=None):
    # Set the playback volume for this movie. The argument is a value between 0.0 and 1.0. If the volume is set to 0 the movie audio will not be decoded.
    if type(volume) == str and volume.startswith('+'):
      if volume.endswith('%'): volume = int(volume.lstrip('+').rstrip('%'))
      else: volume = float(volume.lstrip('+'))*100
      self.mplayer.stdin.write('step_property volume %d\n' % volume)
    elif type(volume) == str and volume.startswith('-'):
      if volume.endswith('%'): volume = int(volume.lstrip('-').rstrip('%'))
      else: volume = float(volume.lstrip('-'))*100
      self.mplayer.stdin.write('step_property volume -%d\n' % volume)
    elif type(volume) == int or type(volume) == float:
      volume = volume*100
      self.mplayer.stdin.write('set_property volume %d\n' % volume)
    elif type(volume) == str and volume.endswith('%'):
      volume = int(volume.rstrip('%'))
      self.mplayer.stdin.write('set_property volume %d\n' % volume)
    else:
      raise Exception("Proper volume argument required. Got %s" % volume)
    self.mplayer.stdin.write('get_property volume\n')
  def set_display(self,surface=None,rect=None):
    print "Setting a display surface is not supported by MPlayer"
    return None
  def toggleosd(self, delay = 0):
    if self.threads.has_key('hideosd') and self.threads['hideosd'].isAlive():
      self.threads['hideosd'].cancel()
      thread = threading.Timer(0, self.hideosd)
      thread.name = 'hideosd'
      self.threads.update({thread.name: thread})
      thread.start()
    else:
      self.showosd(delay)
  def showosd(self, delay = 0, osdtype = None, wait = False):
    if threading.currentThread().name in self.threads and not threading.currentThread().ident == self.threads[threading.currentThread().name].ident:
      print 'Returning '+threading.currentThread().name+' because it is running in parallel with its self'
      return
    if self.bmovl == None:
      if wait == False:
        return
      elif wait == True:
        while self.bmovl == None: pass
    if not osdtype == None:
      self.osdtype = osdtype
    if self.threads.has_key('hideosd') and self.threads['hideosd'].isAlive():
      self.threads['hideosd'].cancel()
    else:
      try:
        os.write(self.bmovl, 'SHOW\n')
      except OSError: pass
    if delay > 0:
      thread = threading.Timer(delay, self.hideosd)
      thread.name = 'hideosd'
      self.threads.update({thread.name: thread})
      thread.start()
    if not (self.threads.has_key('renderosd') and self.threads['renderosd'].isAlive()):
      thread = threading.Thread(target=self.renderosd, args=[True], name='renderosd')
      self.threads.update({thread.name: thread})
      thread.start()
  def hideosd(self, wait = False):
    if threading.currentThread().name in self.threads and not threading.currentThread().ident == self.threads[threading.currentThread().name].ident:
      print 'Returning '+threading.currentThread().name+' because it is running in parallel with its self'
      return
    if self.bmovl == None:
      return
    while not self.get_busy(): pass
    if self.threads.has_key('renderosd') and self.threads['renderosd'].isAlive():
      self.threads['renderosd'].join()
    try:
      os.write(self.bmovl, 'HIDE\n')
    except OSError: pass
    self.osdtype = 'time'
    if 'hideosd' in self.threads.keys():
      self.threads['hideosd'].cancel()
  def updateosd(self, wait = False):
    if not (self.threads.has_key('hideosd') and self.threads['hideosd'].isAlive()):
      return
    if self.bmovl == None and wait == False:
      return
    elif self.bmovl == None and wait == True:
      while self.bmovl == None: pass
    try:
      os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % (self.osd_rect[0], self.osd_rect[1], self.osd_rect[2], self.osd_rect[3], 0, 0))
      string_surf = pygame.image.tostring(self.osd, 'RGBA')
      os.write(self.bmovl, string_surf)
    except OSError: pass
  def renderosd(self, wait = False):
    if threading.currentThread().name in self.threads and not threading.currentThread().ident == self.threads[threading.currentThread().name].ident:
      print 'Returning '+threading.currentThread().name+' because it is running in parallel with its self'
      return
    if self.bmovl == None and wait == False:
      return
    elif self.bmovl == None and wait == True:
      while self.bmovl == None: pass
    width, height = self.video_resolution
    more = self.font.render('...', 1, (255,255,255,255))
    if not self.osd:
      self.osd_rect = pygame.rect.Rect((280,22*3,width-280-15,15))
      self.osd = pygame.surface.Surface(self.osd_rect[0:2], pygame.SRCALPHA)
      self.osd.fill((25,25,25,157))
      title = self.font.render(os.path.basename(self.filename).rpartition('.')[0], 1, (255,255,255,255))
      if title.get_width() > self.osd.get_width():
        self.osd.blit(title.subsurface((0,0,self.osd.get_width()-more.get_width(),title.get_height())), (0,0))
        self.osd.blit(more, (self.osd.get_width()-more.get_width(), title.get_height()-more.get_height()))
      else:
        self.osd.blit(title, (0,0))
      self.updateosd()
    curtime = self.font.render(time.strftime('%I:%M:%S %p '), 1, (255,255,255,255))
    if self.osdtype == 'time' and (not self.osd_time_pos == int(self.get_time()) or not int(self.percent_pos) == self.osd_percentage):
      subosd = self.osd.subsurface([0,22,self.osd.get_width(),44])
      subosd.fill((25,25,25,157))
      curhrs = int(self.time_pos/60.0/60.0)
      curmins = int((self.time_pos-(curhrs*60*60))/60)
      cursecs = int(self.time_pos-((curhrs*60*60)+(curmins*60)))
      totalhrs = int(self.time_length/60.0/60.0)
      totalmins = int((self.time_length-(totalhrs*60*60))/60)
      totalsecs = int(self.time_length-((totalhrs*60*60)+(totalmins*60)))
      if totalhrs == 0 and curhrs == 0 and totalmins == 0 and curmins == 0:
        curpos = '%02d' % (cursecs)
        totallength = '%02d' % (totalsecs)
      elif totalhrs == 0 and curhrs == 0:
        curpos = '%02d:%02d' % (curmins,cursecs)
        totallength = '%02d:%02d' % (totalmins,totalsecs)
      else:
        curpos = '%02d:%02d:%02d' % (curhrs,curmins,cursecs)
        totallength = '%02d:%02d:%02d' % (totalhrs,totalmins,totalsecs)
      pos = self.font.render('%s of %s' % (curpos, totallength), 1, (255,255,255,255))
      if pos.get_width() > subosd.get_width()-curtime.get_width():
        subosd.blit(pos.subsurface((0,0,subosd.get_width()-curtime.get_width()-more.get_width(),pos.get_height())), (0,0))
        subosd.blit(more, (subosd.get_width()-curtime.get_width()-more.get_width(), pos.get_height()-more.get_height()))
      else:
        subosd.blit(pos, (0,0))
      subosd.blit(curtime, (subosd.get_width()-curtime.get_width(), pos.get_height()-curtime.get_height()))
      percbg = pygame.surface.Surface((subosd.get_width(), 22), pygame.SRCALPHA)
      percbg.fill((0,0,0,255))
      subosd.blit(percbg, (0,pos.get_height()))
      perc = pygame.surface.Surface((subosd.get_width()/100.0*self.percent_pos, 22), pygame.SRCALPHA)
      perc.fill((127,127,127,255))
      subosd.blit(perc, (0,pos.get_height()))
      percnum = self.font.render(str(int(self.percent_pos))+'%', 1, (255,255,255,255))
      subosd.blit(percnum, ((subosd.get_width()/2)-(percnum.get_width()/2),pos.get_height()))
      self.osd_percentage = int(self.percent_pos)
      self.osd_time_pos = int(self.time_pos)
      self.updateosd()
      self.osd_last_run = int(time.time())
    elif self.osdtype == 'volume' and not int(self.volume) == self.osd_percentage:
      subosd = self.osd.subsurface([0,22,self.osd.get_width(),44])
      subosd.fill((25,25,25,157))
      voltext = self.font.render('%s%% volume' % int(self.volume), 1, (255,255,255,255))
      if voltext.get_width() > subosd.get_width()-curtime.get_width():
        subosd.blit(voltext.subsurface((0,0,subosd.get_width()-curtime.get_width(),0)), (0,0))
        subosd.blit(more, (subosd.get_width()-curtime.get_width()-more.get_width(), voltext.get_height()-more.get_height()))
      else:
        subosd.blit(voltext, (0,0))
      subosd.blit(curtime, (subosd.get_width()-curtime.get_width(), voltext.get_height()-curtime.get_height()))
      percbg = pygame.surface.Surface((subosd.get_width(), 22), pygame.SRCALPHA)
      percbg.fill((0,0,0,255))
      subosd.blit(percbg, (0,voltext.get_height()))
      perc = pygame.surface.Surface((subosd.get_width()/100.0*self.volume, 22), pygame.SRCALPHA)
      perc.fill((127,127,127,255))
      subosd.blit(perc, (0,voltext.get_height()))
      percnum = self.font.render(str(int(self.volume))+'%', 1, (255,255,255,255))
      subosd.blit(percnum, ((subosd.get_width()/2)-(percnum.get_width()/2),voltext.get_height()))
      self.osd_percentage = int(self.volume)
      self.updateosd()
      self.osd_last_run = int(time.time())
    elif not self.osd_last_run == int(time.time()):
      subosd = self.osd.subsurface([self.osd.get_width()-curtime.get_width(),22,curtime.get_width(),22])
      subosd.fill((25,25,25,157))
      subosd.blit(curtime, (0,0))
      self.updateosd()
      self.osd_last_run = int(time.time())
#    screen.blit(self.osd, self.osd.get_rect(center=screen.get_rect().center))
#    pygame.display.update()
    if self.threads.has_key('hideosd') and self.threads['hideosd'].isAlive():
      thread = threading.Thread(target=self.renderosd, name='renderosd')
      self.threads.update({thread.name: thread})
      thread.start()
  def poll(self):
    status = self.mplayer.poll()
    if status != None:
      self.stop()
    return status
  def stop(self):
    for thread in self.threads.values():
      if 'cancel' in dir(thread):
        thread.cancel()
    try:
      self.mplayer.stdin.write('quit\n')
      self.mplayer.stdin.close()
    except: pass
    try:
      os.close(self.bmovl)
      os.unlink('/tmp/bmovl-%s-%s' % (os.geteuid(), os.getpid()))
    except: pass
    if self.mplayer.poll() != None:
      try:
        self.mplayer.terminate()
        self.mplayer.kill()
      except OSError: pass
      response = self.mplayer.wait()
    else:
      response = self.mplayer.poll()
#    screen.blit(self.screenbkup, (0,0))
#    pygame.display.update()
    return response
  def loop(self):
    while self.poll() == None:
      try: events = pygame.event.get()
      except KeyboardInterrupt: events = [userquit()]
      for event in events:
        if event.type == pygame.QUIT:
          running = False
          try: self.stop()
          except: break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          self.stop()
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
          self.showosd(2, osdtype='time')
          self.pause()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
          self.skip(60)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
          self.skip(-50)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
          self.skip(-20)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
          self.skip(30)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_o:
          self.showosd(2, osdtype='time')
          self.mplayer.stdin.write('osd\n')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
          self.toggleosd(5)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
          self.mplayer.stdin.write('step_property fullscreen\n')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
          self.mplayer.stdin.write('step_property sub_visibility\n')
          self.mplayer.stdin.write('get_property sub_visibility\n')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
          self.mplayer.stdin.write('step_property switch_audio\n')
          self.mplayer.stdin.write('get_property switch_audio\n')
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
          save_pos = self.get_time()-10
          save_hrs = int(save_pos/60.0/60.0)
          save_mins = int((save_pos-(save_hrs*60*60))/60)
          save_secs = int(save_pos-((save_hrs*60*60)+(save_mins*60)))
          try: open(os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+'-'+os.uname()[1]+'.save', 'w').write('%s;%s\n# This line and everything below is ignored, it is only here so that you don\'t need to understand ^ that syntax.\nTime: %02d:%02d:%02d\nVolume: %d%%\n' % (save_pos, self.volume, save_hrs, save_mins, save_secs, self.volume))
          except IOError, (Errno, Errmsg):
            if Errno == 13:
              pass # Permission denied
              self.mplayer.stdin.write('osd_show_text "Unable to save, permission denied."\n')
            else:
              raise OSError((Errno, Errmsg))
          else:
            self.mplayer.stdin.write('osd_show_text "Saved position: %02d:%02d:%02d"\n' % (save_hrs, save_mins, save_secs))
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_9) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 5):
          self.showosd(2, osdtype='volume')
          self.set_volume('-0.02')
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
          self.showosd(2, osdtype='volume')
          self.set_volume('+0.02')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
          if self.get_busy():
            self.pause()
    self.stop()
    for thread in self.threads.keys(): self.threads[thread].isAlive() # It seems as though if I don't interact with these processes Python gets confused and waits for them to finish even though they are already finished, simply checking all processes '.isAlive()' gets around this.
##### End class movieplayer()

def networkhandler():
  remapped_keys = {'ESC': 'ESCAPE', 'ENTER': 'RETURN', 'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4', 'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9'}
  server = socket.socket()
  while True:
    try:
      server.bind(('', 6546))
      break
    except:
      time.sleep(15)
  while True:
    quit = False
    server.listen(1)
    (client, clientinfo) = server.accept()
    clientfile = client.makefile('r')
    client.send("Unnamed Python Media Center network control interface\n")
    client.send("Currently only supports sending keypresses, more will come eventually.\n")
    client.send("----------------------------------------------------------------------\n")
    while not clientfile.closed:
      client.send('> ')
      data = clientfile.readline()
      if data == '':
        clientfile.close()
      elif data[:-1] == 'quit '+os.uname()[1]:
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        quit = True
        clientfile.close()
      elif data[:4] == 'key ':
         if len(data[4:-1]) == 1:
            key = data[4:-1]
         elif len(data[4:-1]) > 1:
           key = data[4:-1].upper()
         if key.isdigit():
           pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': int(key)}))
           pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': int(key)}))
         elif key in remapped_keys.keys() and 'K_'+remapped_keys[key] in dir(pygame):
           pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': eval('pygame.K_'+remapped_keys[key])}))
           pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': eval('pygame.K_'+remapped_keys[key])}))
         elif 'K_'+key in dir(pygame):
           pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': eval('pygame.K_'+key)}))
           pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': eval('pygame.K_'+key)}))
         else:
           client.send("Unrecognised key '"+key+"'.\n")
    if quit:
      break
  server.close()

def LIRChandler():
  pylirc.blocking(False)
  lirc = pylirc.init("UPMC")
  while lirc != 0:
    if select.select([lirc], [], [], 6) != ([], [], []):
      codes = pylirc.nextcode()
      if not codes == None:
        for code in codes:
          if code.startswith('key '):
            key = code[4:-1]
          else:
            key = code
          if 'K_'+key in dir(pygame):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': eval('pygame.K_'+key)}))
            pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': eval('pygame.K_'+key)}))
  pylirc.exit()

## The Pygame modules need to be initialised before they can be used.
### The Pygame docs say to just initialise *everything* at once, I think this is wasteful and am only initialising the bits I'm using.
#pygame.init()
pygame.font.init()
#pygame.image.init() # Doesn't have an '.init()' funtion.
pygame.display.init()
#pygame.transform.init() # Doesn't have an '.init()' funtion.
#pygame.event.init() # Doesn't have an '.init()' funtion.

netthread = threading.Thread(target=networkhandler, name='networkhandler')
netthread.setDaemon(True)
netthread.start()
lircthread = threading.Thread(target=LIRChandler, name='LIRChandler')
lircthread.setDaemon(True)
lircthread.start()

## Pygame on Android doesn't handle system fonts properly, and since I would rather use the system things whereever possible I have told this to treat Android differently.
### This could be done better, possible pack a font with the program?
global fontname
if android:
  fontname = '/system/fonts/DroidSans.ttf'
else:
  fontname = pygame.font.match_font(u'trebuchetms') # Might want to use a non-MS font.

resolution = None
global windowed
if len(sys.argv) > 1 and ('--windowed' in sys.argv or '-w' in sys.argv):
  try: resolution = sys.argv[sys.argv.index('--windowed')+1]
  except ValueError: resolution = sys.argv[sys.argv.index('-w')+1]
  if resolution == '0x0':
    windowed = False
  else:
    windowed = True
else:
  windowed = False

foundfile = False
founddir = False
if len(sys.argv) > 1:
  for filename in sys.argv[1:]:
    if os.path.isfile(filename):
      foundfile = True
      player = movieplayer(filename)
      mplayer = player.play()
      player.loop()
    elif os.path.isdir(filename):
      founddir = filename
  if foundfile == True:
    quit()


if windowed == False and resolution == None:
  screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # Create a new window.
else:
  screen = pygame.display.set_mode((int(resolution.split('x')[0]),int(resolution.split('x')[1]))) # Create a new window.
try: background = pygame.transform.scale(pygame.image.load(os.path.dirname(sys.argv[0])+'/background.png'), screen.get_size()).convert() # Resize the background image to fill the window.
except: # Failing that (no background image?) just create a completely blue background.
  background = pygame.Surface(screen.get_size()).convert() 
  background.fill((125,0,0))
pygame.mouse.set_visible(False)
screen.blit(background, (0,0)) # Put the background on the window.
pygame.display.update() # Update the display.

def terminal():
  term = subprocess.Popen(['x-terminal-emulator'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
  return term.wait

menuitems = [('Videos', filemenu), ('Terminal', terminal), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
menu = textmenu(menuitems)

if android:
  os.chdir('/sdcard/Movies')
elif not founddir == False:
  os.chdir(founddir)
rootdir = os.getcwd()

## These should avoid going through the loop unnecessarily (and wasting resources) when there is events that I'm not going to use anyway.
pygame.event.set_allowed(None) # This says to not put *any* events into the event queue.
pygame.event.set_allowed([pygame.QUIT])
pygame.event.set_allowed([pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.KEYDOWN]) # This says to put the events I want to see into the event queue, this needs to be updated anytime I want to monitor more events.
while running == True:
  try: events = pygame.event.get()
  except KeyboardInterrupt: event = userquit()
  for event in events:
    if event.type == pygame.QUIT:
      running = False
      pygame.quit()
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
      userquit()
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
      released = False
      item = menu.mouseselect(event.pos)
      if item:
        while released != True:
          event = pygame.event.wait()
          if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            released = True
            if menu.mouseselect(event.pos) == item:
              menu.action()
    elif event.type == pygame.MOUSEMOTION:
      menu.mouseselect(event.pos)
    elif event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_DOWN):
      menu.keyselect(event.key==pygame.K_DOWN) # This will call keyselect(False) if K_UP is pressed, and keyselect(True) if K_DOWN is pressed.
    elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
      menu.action()
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
      pygame.display.toggle_fullscreen()
    else:
      pass

