#!/usr/bin/python
import os
import ast
class sys:
  from sys import argv, stdout
import mpd
import aosd
import time
import cairo
class Queue:
  from Queue import Queue, Empty
import getopt
import pylirc
class select:
  from select import select
class urllib2:
  from urllib2 import urlparse
import socket
class string:
  from string import digits
import mimetypes
import threading
import subprocess
import ConfigParser
from math import pi
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
  pygame.quit()
  return pygame.event.Event(pygame.QUIT, {})

def DrawRoundRect(surface, colort = ((25,25,25,150),(53.75,53.75,53.75,163.125),(82.5,82.5,82.5,176.25),(111.25,111.25,111.25,189.375),(140,140,140,202.5),(168.75,168.75,168.75,215.625),(197.5,197.5,197.5,228.75),(226.25,226.25,226.25,241.875),(255,255,255,255)), rect = None, widtht = (0,9,8,7,6,5,4,3,2), xr = 10, yr = 10):
    oldsurface = None
    if rect == None:
      oldsurface = surface
      surface = pygame.surface.Surface((surface.get_width()+(xr*2),surface.get_height()+(yr*2)), pygame.SRCALPHA)
      rect = surface.get_rect()
    clip = surface.get_clip()
    
    for width in widtht:
        color = colort[widtht.index(width)]
        # left and right
        surface.set_clip(clip.clip(rect.inflate(0, -yr*2)))
        pygame.draw.rect(surface, color, rect.inflate(1-width,0), width)

        # top and bottom
        surface.set_clip(clip.clip(rect.inflate(-xr*2, 0)))
        pygame.draw.rect(surface, color, rect.inflate(0,1-width), width)

        # top left corner
        surface.set_clip(clip.clip(rect.left, rect.top, xr, yr))
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.top, 2*xr, 2*yr), width)

        # top right corner
        surface.set_clip(clip.clip(rect.right-xr, rect.top, xr, yr))
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.right-2*xr, rect.top, 2*xr, 2*yr), width)

        # bottom left
        surface.set_clip(clip.clip(rect.left, rect.bottom-yr, xr, yr))
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.bottom-2*yr, 2*xr, 2*yr), width)

        surface.set_clip(clip.clip(rect.right-xr, rect.bottom-yr, xr, yr))
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.right-2*xr, rect.bottom-2*yr, 2*xr, 2*yr), width)

    surface.set_clip(clip)
    if not oldsurface == None:
      surface.blit(oldsurface, (xr,yr))
    return surface

def aosd_render(context, data):
    pygsurf = DrawRoundRect(data['image'])
    width = pygsurf.get_width()
    height = pygsurf.get_height()
    image = cairo.ImageSurface.create_for_data(pygame.surfarray.pixels2d(pygsurf).data, cairo.FORMAT_ARGB32, width, height)
    
    context.set_source_surface(image, 10, 10)
    context.paint()

def render_textscroll(string, font, surface, text_color = (255,255,255), background = (0,0,0,0), update = False):
  text = font.render(string, 1, text_color)
  x_pos = 0
  x_increment = -1
  background = surface.copy()
  while running == True:
    surface.blit(background, (0,0))
    surface.blit(text, (x_pos,0))
#    if update == True:
#      pygame.display.update()
    x_pos += x_increment
    if x_pos <= -(text.get_width()-screen.get_width()) or x_pos >= 0:
      x_increment = -x_increment
    time.sleep(0.01)

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

class osd_thread():
  threads = {}
  display_data = ['', '', 0.0]
  osdvisible = False
  temp_hook = None
  hook = None
  def __init__(self):
    global fontname
    self.font = pygame.font.Font(fontname, 45)
    self.queue = Queue.Queue()
    self.queue.queue.clear()
    thread = threading.Thread(target=self.manageosd, name='manageosd')
    self.threads.update({thread.name: thread})
    thread.start()
  def update(self, line_one = None, line_two = None, percentage = None):
    if not line_one == None:
      self.display_data[0] = line_one
    if not line_two == None:
      self.display_data[1] = line_two
    if not percentage == None:
      self.display_data[2] = percentage
  def get_hook(self):
    if not self.hook == None:
      return self.hook
    elif not self.temp_hook == None:
      return self.temp_hook
    else:
      return None
  def update_hook(self, func):
    self.hook = func
  def toggle(self):
    if "hide" in self.threads.keys():
      self.threads["hide"].cancel()
    self.queue.put("toggle")
  def show(self, delay = 0):
    if "hide" in self.threads.keys():
      self.threads["hide"].cancel()
    self.queue.put("show")
    if delay > 0:
      thread = threading.Timer(delay, self.hide)
      thread.name = 'hide'
      self.threads.update({thread.name: thread})
      thread.start()
  def hide(self):
    if "hide" in self.threads.keys():
      self.threads["hide"].cancel()
    self.queue.put("hide")
  def stop(self):
    self.queue.put("cancel")
  def quit(self):
    self.queue.put("cancel")
  def cancel(self):
    self.queue.put("cancel")
  def visible(self):
    return self.aosd.is_shown()
  def manageosd(self):
    print "Starting OSD"
    time.sleep(0.1)
    command = None
    osd_time = -1
    self.osd_rect = pygame.rect.Rect(((self.font.size('W')[0]*18),(self.font.get_height()*2)+(self.font.get_height()/3),0,0)) # The position is set by OSD and is useless in the pygame rect
    self.osd = pygame.surface.Surface(self.osd_rect[0:2], pygame.SRCALPHA)
    line_one = self.osd.subsurface([0,0,self.osd.get_width(),self.font.get_height()])
    title = self.font.render(self.display_data[0], 1, (255,255,255,255))
    if title.get_width() > self.osd.get_width():
      scrolltitle = True
      line_one_x_pos = 0
      line_one_x_increment = -7
      line_one.blit(title, (line_one_x_pos,0))
    else:
      scrolltitle = False
      line_one.blit(title, (0,0))
    cur_title = ''
    cur_line_two = ''
    curtime = self.font.render(time.strftime('%I:%M:%S %p '), 1, (255,255,255,255))
    time_surf = self.osd.subsurface([self.osd.get_width()-curtime.get_width(),self.font.get_height(),curtime.get_width(),self.font.get_height()])
    time_surf.fill((25,25,25,0))
    time_surf.blit(curtime, (0,0))
    line_two = self.osd.subsurface([0,self.font.get_height(),self.osd.get_width()-curtime.get_width(),self.font.get_height()])
    line_two.fill((25,25,25,0))
    percentage_surf = self.osd.subsurface([0,self.font.get_height()*2,self.osd.get_width(),self.font.get_height()/3])
    percentage_surf.fill((0,0,0,255))
    self.aosd = aosd.Aosd()
    self.aosd.set_transparency(aosd.TRANSPARENCY_COMPOSITE)
    self.aosd.set_position(2, self.osd.get_width()+40, self.osd.get_height()+40) #20 is an abitrary number that fixed something, don't ask me how or what. :/
    self.aosd.set_position_offset(-50, 50)
    self.aosd.set_renderer(aosd_render, {'image': self.osd})
    self.aosd.set_hide_upon_mouse_event(True)
    while command != "cancel":
      try: command = self.queue.get_nowait()
      except Queue.Empty:
        command = None
      if command == "show":
        if not self.hook == None:
          hook_data = self.hook('show')
        self.aosd.show()
        self.aosd.loop_once()
        self.osdvisible = True
      elif command == "hide":
        if not self.hook == None:
          hook_data = self.hook('hide')
        self.aosd.hide()
        self.aosd.loop_once()
        self.osdvisible = False
      elif command == "toggle":
        if not self.hook == None:
          hook_data = self.hook('toggle')
        if self.osdvisible == False:
          self.aosd.show()
          self.aosd.loop_once()
          self.osdvisible = True
          thread = threading.Timer(5, self.queue.put, args=['hide'])
          thread.name = 'hide'
          self.threads.update({thread.name: thread})
          thread.start()
        elif self.osdvisible == True:
          self.aosd.hide()
          self.aosd.loop_once()
          self.osdvisible = False
      if not command == None:
        self.queue.task_done()
      if self.osdvisible == True:
        line_one_str = self.display_data[0]
        line_two_str = self.display_data[1]
        percentage_float = self.display_data[2]
        if not self.hook == None:
          hook_data = self.hook('updating')
          if not hook_data[0] == None:
            line_one_str = hook_data[0]
          if not hook_data[1] == None:
            line_two_str = hook_data[1]
          if not hook_data[2] == None:
            percentage_float = hook_data[2]
        if not line_one_str == cur_title:
          title = self.font.render(line_one_str, 1, (255,255,255,255))
          cur_title = line_one_str
          if title.get_width() > line_one.get_width():
            scrolltitle = True
            line_one_x_increment = -7
            line_one_x_pos = 0
          else:
            scrolltitle = False
            line_one.fill((25,25,25,0))
            line_one.blit(title, (0,0))
        if scrolltitle == True:
          line_one.fill((25,25,25,0))
          line_one.blit(title, (line_one_x_pos,0))
          line_one_x_pos += line_one_x_increment
          if line_one_x_pos+(line_one.get_width()/5) <= -(title.get_width()-line_one.get_width()) or line_one_x_pos >= line_one.get_width()/5:
            line_one_x_increment = -line_one_x_increment
        if not osd_time == int(time.time()):
          curtime = self.font.render(time.strftime('%I:%M:%S %p '), 1, (255,255,255,255))
          time_surf.fill((25,25,25,0))
          time_surf.blit(curtime, (0,0))
          osd_time = int(time.time())
        if not line_two_str == cur_line_two:
          line_two_surf = self.font.render(line_two_str, 1, (255,255,255,255))
          cur_line_two = line_two_str
          if line_two_surf.get_width() > line_two.get_width():
            scrollline_two = True
            line_two_x_increment = -7
            line_two_x_pos = 0
          else:
            scrollline_two = False
            line_two.fill((25,25,25,0))
            line_two.blit(line_two_surf, (0,0))
        if scrollline_two == True:
          line_two.fill((25,25,25,0))
          line_two.blit(line_two_surf, (line_two_x_pos,0))
          line_two_x_pos += line_two_x_increment
          if line_two_x_pos+(line_two.get_width()/8) <= -(line_two_surf.get_width()-line_two.get_width()) or line_two_x_pos >= line_two.get_width()/8:
            line_two_x_increment = -line_two_x_increment
        percentage_surf.fill((0,0,0,255))
        try: percentage_surf.subsurface([0,0,percentage_surf.get_width()*(percentage_float/100), percentage_surf.get_height()]).fill((127,127,127,255))
        except: pass
        self.aosd.render()
        self.aosd.loop_once()
    if not self.hook == None:
      hook_data = self.hook('cancel')
    self.aosd.hide()
    self.aosd.loop_once()

class textmenu():
  clickables = {}
  realmenuitems = []
  selected = None
  def __init__(self, menuitems = None):
    self.font = pygame.font.Font(fontname, 63)
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
    self.font = pygame.font.Font(fontname, 45)
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
    screenwidth = screen.get_width()-horizborder
    screenheight = screen.get_height()-titleoffset-vertborder
#    itemwidth = 190 #6 on 1280 #280 # 5 on 1050 vertical resolution
    itemwidth = 280
#    itemheight = 110 #5 on 720 #210 # 6 on 1680 horizontal resolution
    itemheight = 180
    numcols = screenwidth/itemwidth
    numrows = screenheight/itemheight
    self.pagerows = []
    colspace = (screenwidth-(numcols*itemwidth))/numcols
    rowspace = (screenheight-(numrows*itemheight))/numrows
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
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        pygame.quit()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        self.keyselect(0)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        self.keyselect(1)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
        self.keyselect(2)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
        self.keyselect(3)
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER:
        surf = render_textrect('Movie player is running\nPress the back button to quit', pygame.font.Font(fontname, 45), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
        screenbkup = screen.copy()
        screen.blit(surf, (0,0))
        pygame.display.update()
        player = movieplayer(self.itemsinfo[self.selected[1]]['filename'])
        if not music == None and music.get_busy() == True:
          old_osd_hook = osd.get_hook()
          music.pause()
          startmusic = True
        else:
          startmusic = False
        player.play()
        player.loop()
        if startmusic == True:
          osd.update_hook(old_osd_hook)
          music.unpause()
        screen.blit(screenbkup, (0,0))
        pygame.display.update()
      elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_SPACE):
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
      elif not music == None:
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_9) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 5):
          music.set_volume('-0.12')
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
          music.set_volume('+0.12')
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_m):
          music.pause()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
          music.set_channel("+1")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
          music.set_channel("-1")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LESS or (event.key == pygame.K_COMMA and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
          music.prev()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_GREATER or (pygame.K_PERIOD and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
          music.next()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
          osd.toggle()
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
    self.font = pygame.font.Font(fontname, 36)
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
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        pygame.quit()
      elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_SPACE):
        self.action()
      elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
        return
      elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        self.action()
      elif not music == None:
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_9) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 5):
          music.set_volume('-0.12')
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
          music.set_volume('+0.12')
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_m):
          music.pause()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
          music.set_channel("+1")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
          music.set_channel("-1")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LESS or (event.key == pygame.K_COMMA and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
          music.prev()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_GREATER or (pygame.K_PERIOD and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
          music.next()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
          osd.toggle()
  def action(self):
    if not os.path.isfile(str(self['filename'])):
      surf = render_textrect('This file does not seem to exist. Has it been deleted?\n'+str(self['filename']), pygame.font.Font(fontname, 45), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
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
    render_textrect('Movie player is running.\n\nPress the back button to quit.', pygame.font.Font(fontname, 63), screen.get_rect(), (255,255,255), screen, 3)
    pygame.display.update()
    player = movieplayer(self['filename'])
    if not music == None and music.get_busy() == True:
      old_osd_hook = osd.get_hook()
      music.real_mute()
      startmusic = True
    else:
      startmusic = False
    player.play()
    player.loop()
    if startmusic == True:
      if "lirc_amp" in rare_options.keys():
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"RESET"]).wait()
        for _ in xrange(60): music.set_volume('-0.01')
#        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL-","--count=60"]).wait()
        osd.update_hook(old_osd_hook)
        music.real_mute()
        for _ in xrange(20): music.set_volume('+0.01')
#        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL+","--count=20"])
      else:
        osd.update_hook(old_osd_hook)
        music.unpause()
    self['watched'] = True
    screen.blit(screenbkup, (0,0))
    pygame.display.update()
##### End class movieinfo()

class movieplayer():
  # I've tried to make this fairly compatible with the pygame.movie module, but there's a lot of features in this that are not in the pygame.movie module.
  # Also, I haven't really tested this compatibility or even used pygame.movie ever before.
  paused = None
  time_pos = 0
  percent_pos = 0
  time_length = 0
  str_length = '0'
  osd_percentage = -1
  osd_time_pos = -1
  remapped_keys = {'ESC': 'ESCAPE', 'MOUSE_BTN2_DBL': 'ESCAPE', 'ENTER': 'RETURN'}
  video_resolution = (0,0)
  volume = 0
  threads = {}
  osdtype = 'time'
  old_osd_hook = None
  def __init__(self, filename):
    global fontname
    self.font = pygame.font.Font(fontname, 45)
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
          totalhrs = int(self.time_length/60.0/60.0)
          totalmins = int((self.time_length-(totalhrs*60*60))/60)
          totalsecs = int(self.time_length-((totalhrs*60*60)+(totalmins*60)))
          if totalhrs == 0 and totalmins == 0:
            self.str_length = '%02d' % (totalsecs)
          elif totalhrs == 0:
            self.str_length = '%02d:%02d' % (totalmins,totalsecs)
          else:
            self.str_length = '%02d:%02d:%02d' % (totalhrs,totalmins,totalsecs)
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
    return
  def play(self, loops=None):
    # Starts playback of the movie. Sound and video will begin playing if they are not disabled. The optional loops argument controls how many times the movie will be repeated. A loop value of -1 means the movie will repeat forever.
    args = ['-really-quiet','-input','conf=/dev/null:nodefault-bindings','-msglevel','vfilter=5:identify=5:global=4:input=5:cplayer=0:statusline=0','-slave','-identify','-stop-xscreensaver','-idx']
    args += ['-wid',str(pygame.display.get_wm_info()['window']),'-vf','expand=:::::'+str(screen.get_width())+'/'+str(screen.get_height())]
    global rare_options
    if "lirc_amp" in rare_options.keys():
      args += ['-volume','98']
    else:
      args += ['-volume','75']
    if movie_args:
      args += movie_args
#    if windowed == False: args += ['-fs']
    if loops == 0:
      loops = None
    elif loops == -1:
      loops = 0
    if loops != None:
      args += ['-loop', str(loops)]
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
    self.mplayer.stdin.write('pausing_keep_force get_property volume\n')
    self.mplayer.stdin.write('pausing_keep_force get_property pause\n')
    thread = threading.Thread(target=self.procoutput, name='stdout')
    self.threads.update({thread.name: thread})
    thread.start()
    osd.update(line_one=os.path.basename(self.filename).rpartition('.')[0], percentage=0)
    osd.update_hook(self.osd_hook)
    return self.mplayer
  def pause(self):
    # This will temporarily stop or restart movie playback.
    self.mplayer.stdin.write('pausing_keep_force osd_show_text "Paused"\n')
    self.mplayer.stdin.write('pause\n')
  def skip(self, seconds):
    # Advance the movie playback time in seconds. This can be called before the movie is played to set the starting playback time. This can only skip the movie forward, not backwards. The argument is a floating point number.
    ### I've added being able to go backwards.
    self.osdtype = 'time'
    osd.show(2)
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
    try: self.mplayer.stdin.write('pausing_keep_force get_property time_pos\n')
    except:
      self.time_pos = 0
      return 0
    while self.time_pos == None: 
      if not (self.threads.has_key('stdout') and self.threads['stdout'].isAlive()):
        self.time_pos = 0
    return self.time_pos
  def osd_hook(self, arg):
    # Return the current playback time as a floating point value in seconds. This method currently seems broken and always returns 0.0.
    ### This is easy to implement so do so even though the pygame version fails.
    if arg == 'updating' and self.osdtype == 'time':
      self.get_time()
      curhrs = int(self.time_pos/60.0/60.0)
      curmins = int((self.time_pos-(curhrs*60*60))/60)
      cursecs = int(self.time_pos-((curhrs*60*60)+(curmins*60)))
      if len(self.str_length.split(':')) == 1:
        curpos = '%02d' % (cursecs)
      elif len(self.str_length.split(':')) == 2:
        curpos = '%02d:%02d' % (curmins,cursecs)
      else:
        curpos = '%02d:%02d:%02d' % (curhrs,curmins,cursecs)
      if not self.str_length == '0':
        return [None, "%s of %s" % (curpos, self.str_length), self.percent_pos]
      else:
        return [None, "%s" % curpos, self.percent_pos]
    elif arg == 'updating' and self.osdtype == "volume":
      return [None, "%s%% volume" % int(self.volume), self.volume]
    elif arg == 'updating' and not self.osdtype == 'time':
      return osd.display_data
    elif arg == 'toggle' and not self.osdtype == 'time':
      self.osdtype = 'time'
      return None
    return None
  def get_busy(self):
    self.paused = None
    try: self.mplayer.stdin.write('pausing_keep_force get_property pause\n')
    except:
      self.paused = True
      return True
    while self.paused == None:
      if not (self.threads.has_key('stdout') and self.threads['stdout'].isAlive()):
        self.paused = True
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
    global rare_options
    if not "lirc_amp" in rare_options.keys():
      osd.show(2)
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
    else:
      if type(volume) == str and volume.startswith('+'):
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL+"]).wait()
      elif type(volume) == str and volume.startswith('-'):
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL-"]).wait()
      elif type(volume) == int or type(volume) == float:
        volume = volume*100
        self.mplayer.stdin.write('set_property volume %d\n' % volume)
      elif type(volume) == str and volume.endswith('%'):
        volume = int(volume.rstrip('%'))
        self.mplayer.stdin.write('set_property volume %d\n' % volume)
      else:
        raise Exception("Proper volume argument required. Got %s" % volume)
  def set_display(self,surface=None,rect=None):
    print "Setting a display surface is not supported by MPlayer"
    return None
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
    if self.mplayer.poll() != None:
      try:
        self.mplayer.terminate()
        self.mplayer.kill()
      except OSError: pass
      response = self.mplayer.wait()
    else:
      response = self.mplayer.poll()
    pygame.mouse.set_visible(pygame.mouse.set_visible(True))
    return response
  def loop(self):
    while self.poll() == None:
      try: events = pygame.event.get()
      except KeyboardInterrupt: events = [userquit()]
      for event in events:
        if event.type == pygame.QUIT:
          running = False
          pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
          try: self.stop()
          except: break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          self.stop()
        elif (event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_p)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
          self.osdtype = 'time'
          osd.show(2)
          self.pause()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
          self.skip(300)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
          self.skip(-290)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
          self.skip(-20)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
          self.skip(30)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_o:
          self.osdtype = 'time'
          osd.show(2)
          self.mplayer.stdin.write('osd\n')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
          osd.toggle()
#        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
#          self.mplayer.stdin.write('step_property fullscreen\n')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
          self.mplayer.stdin.write('step_property sub_visibility\n')
          self.mplayer.stdin.write('get_property sub_visibility\n')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
          self.mplayer.stdin.write('step_property switch_audio\n')
          self.mplayer.stdin.write('get_property switch_audio\n')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
          if "lirc_amp" in rare_options.keys():
            subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"POWER"]).wait()
          else:
            self.mplayer.stdin.write('step_property mute\n')
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
          save_pos = self.get_time()-10
          save_hrs = int(save_pos/60.0/60.0)
          save_mins = int((save_pos-(save_hrs*60*60))/60)
          save_secs = int(save_pos-((save_hrs*60*60)+(save_mins*60)))
          try: open(os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+'-'+os.uname()[1]+'.save', 'w').write('%s;%s\n# This line and everything below is ignored, it is only here so that you don\'t need to understand ^ that syntax.\nTime: %02d:%02d:%02d\nVolume: %d%%\n' % (save_pos, self.volume, save_hrs, save_mins, save_secs, self.volume))
          except IOError, (Errno, Errmsg):
            if Errno == 13:
              self.mplayer.stdin.write('osd_show_text "Unable to save, permission denied."\n')
            else:
              raise OSError((Errno, Errmsg))
          else:
            self.mplayer.stdin.write('osd_show_text "Saved position: %02d:%02d:%02d"\n' % (save_hrs, save_mins, save_secs))
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_9) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 5):
          ### FIXME ### Need to display volume in the OSD
          self.osdtype = 'volume'
          self.set_volume('-0.02')
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
          ### FIXME ### Need to display volume in the OSD
          self.osdtype = 'volume'
          self.set_volume('+0.02')
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
          if self.get_busy():
            self.pause()
    self.stop()
    for thread in self.threads.keys(): self.threads[thread].isAlive() # It seems as though if I don't interact with these processes Python gets confused and waits for them to finish even though they are already finished, simply checking all processes '.isAlive()' gets around this.
##### End class movieplayer()

class musicplayer():
  # This should be a drop-in replacement for pygame.mixer.music but this only needs to support a HTTP streamed audio stream via Mplayer.
  url = None
  mpc = mpd.MPDClient()
  muted = False
  paused = None
  volume = None
  mplayer = None
  threads = {}
  trackinfo = {}
  streaminfo = {}
  cur_channel = 0
  def load(self, url):
    # This will load a music URL object and prepare it for playback. This does not start the music playing.
    global fontname
    self.font = pygame.font.Font(fontname, 45)
    self.url = url
  def mpcReconnect(self):
    try: self.mpc.disconnect()
    except mpd.ConnectionError: pass #Probably not connected yet, ignore.
    finally: self.mpc.connect(mpd_host, mpd_port+self.cur_channel)
  def procoutput(self):
    response = None
    while not response == '' and not self.mplayer.stdout.closed:
      response = self.mplayer.stdout.read(1)+self.mplayer.stdout.readline().strip('\r\n')
      if response.startswith("ICY Info: ") or response.startswith("\nICY Info: "):
        self.streaminfo = {}
        for key_value in ' '.join(response.split(' ')[2:]).split(';'):
          key = key_value.split('=')[0]
          value = '='.join(key_value.split('=')[1:]).strip("\"'")
          self.streaminfo[key] = value
        print "StreamTitle changed: %s" % self.streaminfo["StreamTitle"]
        self.trackinfo = {}
        try: self.trackinfo = self.mpc.currentsong()
        except mpd.ConnectionError: 
          self.mpcReconnect()
          self.trackinfo = self.mpc.currentsong()
        if 'artist' in self.trackinfo.keys() and 'album' in self.trackinfo.keys() and 'title' in self.trackinfo.keys():
          print "Assuming a new track started: %s - %s/%s" % (self.trackinfo["artist"], self.trackinfo["album"], self.trackinfo["title"])
        else:
          print "Assuming a new track started: at least one of artist, album, or title is missing."
        if not self.volume == 0.0 and self.muted == False:
          osd.show(4)
        sys.stdout.flush()
      elif response.startswith("No bind found for key '"):
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
	elif not self.paused == None and response.startswith('video_aspect'):
          threading.Timer(1, osd.show, [5]).start()
        elif response == 'paused':
          self.paused = True
        elif response.startswith('pause='):
          self.paused = response.split('=')[-1] == 'yes'
        elif response.startswith('volume='):
          self.volume = float(response.split('=')[1])
        elif response.startswith('mute='):
          self.muted = bool(response.split('=')[1].lower() == 'yes')
  def osd_hook(self, arg):
#    if 'title' in self.trackinfo.keys():
#      line_one = self.trackinfo['title']
#    else:
#      line_one = "Unkown"
    line_one = ''
    if 'artist' in self.trackinfo.keys():
      line_one += self.trackinfo['artist']
      line_one += ' - '
    if 'title' in self.trackinfo.keys():
      line_one += self.trackinfo['title']
    else:
      line_one += "Unknown"
    if line_one == '':
      line_one = "Unknown"
    line_two= "Channel %02d" % self.cur_channel
    if self.volume == None:
      try: self.mplayer.stdin.write('pausing_keep_force get_property volume\n')
      except: pass
    return line_one, line_two, self.volume
  def play(self, loops=0, start=0.0):
    # This will play the loaded music stream. If the music is already playing it will be restarted.
    # This can't work for streaming audio: The loops argument controls the number of repeats a music will play. play(5) will cause the music to played once, then repeated five times, for a total of six. If the loops is -1 then the music will repeat indefinitely.
    # Neither can this: The starting position argument controls where in the music the song starts playing. The starting position is dependent on the format of music playing. MP3 and OGG use the position as time (in seconds). MOD music it is the pattern order number. Passing a startpos will raise a NotImplementedError if it cannot set the start position
    if not start == 0.0:
      raise NotImplementedError("Can not set a start position on streaming media.")
    if self.url == None:
      return "musicplayer().play: No URL loaded, ignoring."
    elif "%02d" in self.url:
      url = self.url % self.cur_channel
    else:
      url = self.url
    print "Starting playback of '%s', channel %02d: '%s'" % (self.url, self.cur_channel, url)
    args = ['-really-quiet','-input','conf=/dev/null:nodefault-bindings','-msglevel','demuxer=4:identify=5:global=4:input=5:cplayer=0:statusline=0','-slave','-identify']
    global rare_options
    if "lirc_amp" in rare_options.keys():
      args += ['-volume','98']
    else:
      args += ['-volume','25']
    if music_args:
      args += music_args
    self.mplayer = subprocess.Popen(['mplayer']+args+[url],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1)
    if self.mplayer.poll() != None:
      raise Exception(mplayer.stdout.read())
    self.mplayer.stdin.write('pausing_keep_force get_property pause\n')
    self.mplayer.stdin.write('pausing_keep_force get_property volume\n')
    thread = threading.Thread(target=self.procoutput, name='stdout')
    self.mpcReconnect()
    self.threads.update({thread.name: thread})
    thread.start()
  def rewind(self):
    # This could be done if there is decent buffering, don't care not worth it: Resets playback of the current music to the beginning.
    return None
  def stop(self):
    # Stops the music playback if it is currently playing.
    osd.hide()
    if not self.mplayer == None and not self.mplayer.stdin.closed:
      self.mplayer.stdin.write("quit\n")
      self.mplayer.stdin.close()
      self.mpc.disconnect()
  def pause(self):
    # Could also be possible if good buffering is in use, don't care not worth it: Temporarily stop playback of the music stream. It can be resumed with the pygame.mixer.music.unpause() function.
    if "lirc_amp" in rare_options.keys():
      subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"POWER"]).wait()
    else:
      if not self.mplayer == None and not self.mplayer.stdin.closed:
        self.mplayer.stdin.write("mute\n")
        self.mplayer.stdin.write('pausing_keep_force get_property mute\n')
  def real_mute(self):
    if not self.mplayer == None and not self.mplayer.stdin.closed:
      self.mplayer.stdin.write("mute\n")
      self.mplayer.stdin.write('pausing_keep_force get_property mute\n')
  def unpause(self):
    # Could also be possible if good buffering is in use, don't care not worth it: This will resume the playback of a music stream after it has been paused.
    ## I have implemented pausing as a toggle and can't programatically tell whether it is paused or not.
    return self.pause()
  def fadeout(self, fadetime):
    # This will stop the music playback after it has been faded out over the specified time (measured in milliseconds).
    ## I haven't set up any way to query for Mplayer's current volume, I'll deal with this some other time, tbis would be quite useful with the chanell changing.
    return self.stop()
    # orig_volume = mplayer.volume
    # for i in range(mplayer.volume,0,-(mplayer.volume/fadetime)):
    #   self.set_volume(i)
    # 
    # mplayer.stop()
    # self.set_volume(orig_volume)
  def set_volume(self,volume=None):
    # Set the playback volume for this movie. The argument is a value between 0.0 and 1.0. If the volume is set to 0 the movie audio will not be decoded.
    if not "lirc_amp" in rare_options.keys():
      osd.show(2)
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
    else:
      if type(volume) == str and volume.startswith('+'):
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL+"]).wait()
      elif type(volume) == str and volume.startswith('-'):
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL-"]).wait()
      elif type(volume) == int or type(volume) == float:
        volume = volume*100
        self.mplayer.stdin.write('set_property volume %d\n' % volume)
      elif type(volume) == str and volume.endswith('%'):
        volume = int(volume.rstrip('%'))
        self.mplayer.stdin.write('set_property volume %d\n' % volume)
      else:
        raise Exception("Proper volume argument required. Got %s" % volume)
  def get_volume(self):
    # Returns the current volume for the mixer. The value will be between 0.0 and 1.0.
    self.volume = None
    self.muted = None
    self.mplayer.stdin.write('pausing_keep_force get_property volume\n')
    self.mplayer.stdin.write('pausing_keep_force get_property mute\n')
    while self.volume == None or self.muted == None: pass
    if self.muted == True:
      return 0
    else:
      return self.volume/100.0
  def get_busy(self):
    # Returns True when the music stream is actively playing. When the music is idle this returns False.
    if not self.mplayer.poll() == None:
      return False

    return not self.get_volume() == 0.0
  def set_pos(self, pos):
    # Also not possible with a stream: This sets the position in the music file where playback will start. The meaning of "pos", a float (or a number that can be converted to a float), depends on the music format. Newer versions of SDL_mixer have better positioning support than earlier. An SDLError is raised if a particular format does not support positioning.
    return None
  def get_pos(self):
    # Possible, but not useful, don't care to support it: This gets the number of milliseconds that the music has been playing for. The returned time only represents how long the music has been playing; it does not take into account any starting position offsets.
    return None
  def queue(self, url):
    # Not useful because the stream should always be there: This will load a music file and queue it. A queued music file will begin as soon as the current music naturally ends. If the current music is ever stopped or changed, the queued song will be lost.
    return None
  def set_endevent(self, type = None):
    # This causes Pygame to signal (by means of the event queue) when the music is done playing. The argument determines the type of event that will be queued.
    # The event will be queued every time the music finishes, not just the first time. To stop the event from being queued, call this method with no argument.
    ## Possible, not very useful, can't be bothered.
    return None
  def get_endevent(self):
    # Returns the event type to be sent every time the music finishes playback. If there is no endevent the function returns pygame.NOEVENT.
    return pygame.NOEVENT
  def set_channel(self, ch = 0):
    if type(ch) == str and ch.startswith('+'):
      self.cur_channel += int(ch.lstrip('+'))
    elif type(ch) == str and ch.startswith('-'):
      self.cur_channel -= int(ch.lstrip('-'))
    elif type(ch) == int or type(ch) == float:
      self.cur_channel = ch
    elif not (type(ch) == int or type(ch) == float):
      raise Exception("Proper channel argument required. Got %s" % ch)
    self.stop()
    if self.cur_channel > channels[-1]:
      self.cur_channel = channels[0]
    elif self.cur_channel < channels[0]:
      self.cur_channel = channels[-1]
    self.play()
  def next(self):
    try: self.mpc.next()
    except mpd.ConnectionError:
      self.mpcReconnect()
      self.mpc.next()
  def previous(self):
    try: self.mpc.previous()
    except mpd.ConnectionError:
      self.mpcReconnect()
      self.mpc.previous()
  def prev(self):
    return self.previous()
##### End class musicplayer()

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
    try:
      client.send("Unnamed Python Media Center network control interface\n")
      client.send("Currently only supports sending keypresses, more will come eventually.\n")
      client.send("----------------------------------------------------------------------\n")
    except: pass
    while not clientfile.closed:
      try: client.send('> ')
      except: pass
      data = clientfile.readline()
      if data == '':
        clientfile.close()
      elif data[:-1] == 'quit '+os.uname()[1]:
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        global quit
        quit = True
        clientfile.close()
      elif data[:4] == 'key ':
         if len(data[4:-1]) == 1:
            key = data[4:-1]
         elif len(data[4:-1]) > 1:
           key = data[4:-1].upper()
         if key.isdigit():
           pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'mod': 0, 'key': int(key)}))
           pygame.event.post(pygame.event.Event(pygame.KEYUP, {'mod': 0, 'key': int(key)}))
         elif key in remapped_keys.keys() and 'K_'+remapped_keys[key] in dir(pygame):
           pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'mod': 0, 'key': eval('pygame.K_'+remapped_keys[key]), 'unicode': key}))
           pygame.event.post(pygame.event.Event(pygame.KEYUP, {'mod': 0, 'key': eval('pygame.K_'+remapped_keys[key]), 'unicode': key}))
         elif 'K_'+key in dir(pygame):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'mod': 0, 'key': eval('pygame.K_'+key), 'unicode': key}))
            pygame.event.post(pygame.event.Event(pygame.KEYUP, {'mod': 0, 'key': eval('pygame.K_'+key), 'unicode': key}))
         else:
           try: client.send("Unrecognised key '"+key+"'.\n")
           except: pass
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
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'mod': 0, 'key': eval('pygame.K_'+key), 'unicode': key}))
            pygame.event.post(pygame.event.Event(pygame.KEYUP, {'mod': 0, 'key': eval('pygame.K_'+key), 'unicode': key}))
  pylirc.exit()

def main():
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
  
  global windowed
  resolution = None
  windowed = False
  music_url = None
  global mpd_host
  mpd_host = None
  global channels
  channels = [0]
  global mpd_port
  mpd_port = 6600
  global movie_args
  movie_args = None
  global music_args
  music_args = None
  global rare_options
  rare_options = {None: None}

  if len(sys.argv) > 1:
    options, arguments = getopt.getopt(sys.argv[1:], 'w:m:o:', ["windowed=", "music-url=", "options=", "channels=", "mpd-host=", "mpd-port=", "movie-args=", "music-args="])
    for o, a in options:
      if o == "--windowed" or o == '-w':
        resolution = str(a)
        if resolution == '0x0':
          windowed = False
        else:
          windowed = True
      elif o == "--music-url" or o == '-m':
        music_url = str(a)
      elif o == "--channels":
        channels = range(0, int(a))
      elif o == "--mpd-host":
        mpd_host = str(a)
      elif o == "--mpd-port":
        mpd_host = int(a)
      elif o == "--movie-args":
        movie_args = str(a).split(' ')
      elif o == "music-args":
        music_args = str(a).split(' ')
      elif o == "--options" or o == "-o":
        rare_options = ast.literal_eval(a)
  else:
    options, arguments = ([], [])
  
  if mpd_host == None and not music_url == None:
    mpd_host = urllib2.urlparse.urlparse(music_url)[1].split(':')[0]

  global osd
  osd = osd_thread()
  pygame.register_quit(osd.stop)
  print osd
  
  foundfile = False
  founddir = False
  if len(arguments) > 0:
    for filename in arguments:
      if os.path.isfile(filename):
        foundfile = True
        player = movieplayer(filename)
        mplayer = player.play()
        player.loop()
      elif os.path.isdir(filename):
        founddir = filename
    if foundfile == True:
      osd.stop()
      quit()
  
  global music
  music = None
  if not music_url == None:
    music = musicplayer()
    music.load(music_url)
    if "lirc_amp" in rare_options.keys():
      for _ in xrange(60): music.set_volume('-0.01')
#      subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL-","--count=60"]).wait()
    music.play()
    pygame.register_quit(music.stop)
    osd.update_hook(music.osd_hook)
    for _ in xrange(60): music.set_volume('-0.01')
#    subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"VOL+","--count=20"])
  
  global screen
  if windowed == False and resolution == None:
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # Create a new window.
  else:
    screen = pygame.display.set_mode((int(resolution.split('x')[0]),int(resolution.split('x')[1]))) # Create a new window.
  global background
  try: background = pygame.transform.scale(pygame.image.load(os.path.dirname(sys.argv[0])+'/background.png'), screen.get_size()).convert() # Resize the background image to fill the window.
  except: # Failing that (no background image?) just create a completely blue background.
    background = pygame.Surface(screen.get_size()).convert() 
    background.fill((125,0,0))
  pygame.mouse.set_visible(False)
  screen.blit(background, (0,0)) # Put the background on the window.
  pygame.display.update() # Update the display.

  def terminal():
    term = subprocess.Popen(['x-terminal-emulator'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    return term.wait()

  def steam_big_picture():
    global music
    steam = subprocess.Popen(['steam', '-bigpicture'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    screenbkup = screen.copy()
    surf = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
    surf.fill((0,0,0,225))
    screen.blit(surf, (0,0))
    render_textrect('Steam is still running.\n\nPress back key to kill Steam.', pygame.font.Font(fontname, 63), screen.get_rect(), (255,255,255), screen, 3)
    pygame.display.update()
    music.real_mute()
    while steam.poll() == None:
      try: events = pygame.event.get()
      except KeyboardInterrupt: events = [userquit()]
      for event in events:
        if event.type == pygame.QUIT:
          pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
          pygame.quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          if steam.poll() == None:
            subprocess.Popen(['steam','-shutdown']).wait()
          if steam.poll() == None:
            steam.terminate()
          if steam.poll() == None:
            steam.kill()
    screen.blit(screenbkup, (0,0))
    pygame.display.update()
    return steam.poll()
  
#  menuitems = [('Videos', filemenu), ('Terminal', terminal), ("Steam", steam_big_picture), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
  menuitems = [('Videos', filemenu), ('Terminal', terminal), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
  menu = textmenu(menuitems)
  
  if android:
    os.chdir('/sdcard/Movies')
  elif not founddir == False:
    os.chdir(founddir)
  global rootdir
  rootdir = os.getcwd()
  
  ## These should avoid going through the loop unnecessarily (and wasting resources) when there is events that I'm not going to use anyway.
  pygame.event.set_allowed(None) # This says to not put *any* events into the event queue.
  pygame.event.set_allowed([pygame.QUIT])
  pygame.event.set_allowed([pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.KEYDOWN]) # This says to put the events I want to see into the event queue, this needs to be updated anytime I want to monitor more events.
  global running
  while running == True:
    try: events = pygame.event.get()
    except KeyboardInterrupt: events = [userquit()]
    for event in events:
      if event.type == pygame.QUIT:
        running = False
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
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
      elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_SPACE):
        menu.action()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
        pygame.display.toggle_fullscreen()
      elif not music == None:
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_9) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 5):
          music.set_volume('-0.12')
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
          music.set_volume('+0.12')
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_m):
          music.pause()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
          music.set_channel("+1")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
          music.set_channel("-1")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LESS or (event.key == pygame.K_COMMA and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
          music.prev()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_GREATER or (pygame.K_PERIOD and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
          music.next()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
          osd.toggle()

if __name__ == "__main__":
  try: main()
  except: pygame.quit()
