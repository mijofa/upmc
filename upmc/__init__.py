#!/usr/bin/python
import os
import sys
import ast
import time
import cairo
import Queue
import getopt
import select
import socket
import string
import urllib2
import datetime
import mimetypes
import threading
import subprocess
import ConfigParser

import aosd
import pylirc

import pygame

import upmc.movie
import upmc.music

#UPMC_DATADIR = os.getcwd()
UPMC_DATADIR = '/usr/share/upmc/'

mimetypes.add_type('video/divx', '.divx')
mimetypes.add_type('video/ogm', '.ogm')
mimetypes.add_type('video/dvd', '.dvd')

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

def human_readable_seconds(seconds):
  hrs = int(seconds/60.0/60.0)
  mins = int((seconds-(hrs*60*60))/60)
  secs = int(seconds-((hrs*60*60)+(mins*60)))
  if not hrs == 0:
    return "%02d:%02d:%02d" % (hrs,mins,secs)
  elif not secs == 0:
    return "%02d:%02d" % (mins,secs)
  elif not secs == 0:
    return "%02d" % (secs)
  else:
    return "00"

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
      # No, do it anyway and let the word fall off the end.
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
      elif command == 'real_hide':
        self.osdvisible = False
      elif command == "hide":
        if not self.hook == None:
          hook_data = self.hook('hide')
        self.aosd.hide()
        self.aosd.loop_once()
        self.queue.put('real_hide')
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
        time.sleep(0.01)
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
  cwd = os.getcwd()
  rowoffset = 0
  def __init__(self):
    self.font = pygame.font.Font(fontname, 45)
    self.builditems()
    self.render()
    self.loop()
  def customsortkey(self, item):
    newitem = item
    itemHasDigit = False
    if os.path.isdir(item) and not item.lower().endswith('.dvd'):
      newitem = '       ' + newitem # I want directories to be at the start of the list, I think ' ' is the first ASCII character and will get sorted before the others.
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
    if directory == './':
      directory = os.getcwd()
    elif not directory.startswith('/'):
      directory = os.getcwd()+'/'+directory
    if not directory.endswith('/'):
      directory = directory+'/'
    self.items = []
    if not directory.rstrip('/') == rootdir.rstrip('/') and not os.getcwd() == '/':
      self.items.append('../')
      self.itemsinfo['../']['filename'] = directory+'../'
    else:
      self.itemsinfo['../']['filename'] = '../'
    dirlist = []
    for item in os.listdir(directory):
      if not item.startswith('.') and os.access(directory+item, os.R_OK):
        dirlist.append(item)
    dirlist.sort(key=self.customsortkey)
    for filename in dirlist:
      item = filename.rpartition('.')
      if item[1] == '.':
        item = item[0]
      else:
        item = item[2]
      if not self.itemsinfo.has_key(directory+item):
        self.itemsinfo[directory+item] = {}
      try: ftype = mimetypes.guess_type(filename)[0].partition('/')[0]
      except AttributeError: ftype = 'Unknown'
      if ftype == 'video':
        if not directory+item in self.items:
          self.items.append(directory+item)
        self.itemsinfo[directory+item]['file'] = True
        self.itemsinfo[directory+item]['title'] = item
        self.itemsinfo[directory+item]['itemnum'] = self.items.index(directory+item)
        self.itemsinfo[directory+item]['filename'] = directory+filename
      elif ftype == 'image':
        self.itemsinfo[directory+item]['thumb'] = directory+filename
      elif filename[-5:] == '.info':
        self.itemsinfo[directory+item]['info'] = directory+filename
        if not 'filename' in self.itemsinfo[directory+item]:
          iteminfo = movieinfo(self.itemsinfo[directory+item])
          if 'filename' in iteminfo:
            if not directory+item in self.items:
              self.items.append(directory+item)
            self.itemsinfo[directory+item]['file'] = True
            self.itemsinfo[directory+item]['title'] = item
            self.itemsinfo[directory+item]['itemnum'] = self.items.index(directory+item)
            self.itemsinfo[directory+item]['filename'] = iteminfo['filename']
      elif ftype == 'Unknown' and os.path.isdir(filename):
        self.items.append(directory+item)
        self.itemsinfo[directory+item] = {}
        self.itemsinfo[directory+item]['file'] = False
        self.itemsinfo[directory+item]['title'] = item
        self.itemsinfo[directory+item]['itemnum'] = self.items.index(directory+item)
        self.itemsinfo[directory+item]['filename'] = directory+item + '/'
        if not self.itemsinfo[directory+item].has_key('thumb'):
          for extension in ['.jpg', '.png', '.jpeg', '.gif']:
            for filename in ['folder'+extension, '.folder'+extension, 'folder'+extension.upper(), '.folder'+extension.upper()]:
              if os.path.isfile(directory + item +'/'+ filename) and os.access(directory + item +'/'+ filename, os.R_OK):
                self.itemsinfo[directory+item]['thumb'] = directory + item +'/'+ filename
                break
    if directory.rstrip('/') == rootdir.rstrip('/'):
      self.items.append('dvd://')
      if not self.itemsinfo.has_key('dvd://'):
        self.itemsinfo['dvd://'] = {'file': True, 'filename': 'dvd://', 'thumb': UPMC_DATADIR+'/dvd.jpg', 'title': "Play DVD"}
        self.itemsinfo['dvd://']['itemnum'] = self.items.index('dvd://')
  def render(self, rowoffset = 0):
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
      try: events = pygame.event.get()
      except KeyboardInterrupt: events = [userquit()]
      if not music == None:
        new_track = music.get_now_playing()
        if music.old_track != new_track:
          music.old_track = new_track
          osd.show(2)
        elif music.get_state() == "Ended":
          music.reconnect()
      for event in events:
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
          print self.itemsinfo[self.selected[1]]
          info = movieinfo(self.itemsinfo[self.selected[1]])
          info.action()
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_SPACE):
  #        print self.itemsinfo[self.selected[1]]
  #        info = movieinfo(self.itemsinfo[self.selected[1]])
  #        info.action()
          self.action(self.selected[-1])
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
            osd.show(5)
            music.increment_volume(-0.02)
          elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
            osd.show(5)
            music.increment_volume(+0.02)
          elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_m):
            osd.show(5)
            music.toggle_mute()
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
            music.increment_channel(+1)
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
            music.increment_channel(-1)
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_LESS or (event.key == pygame.K_COMMA and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
            music.previous_track()
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_GREATER or (pygame.K_PERIOD and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
            music.next_track()
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
      screenbkup = screen.copy()
      info = movieinfo(self.itemsinfo[selected])
      info.display()
      info.loop()
      screen.blit(screenbkup, (0,0))
      pygame.display.update()
    elif not self.itemsinfo[selected]['file']:
      self.select(None)
      filename = self.itemsinfo[selected]['filename'].replace('//', '/')
      if filename.endswith('../'):
        filename = filename.rsplit('/', 3)[0]
#      if '../' in filename:
#        filename = filename[:filename.rindex('../')].rsplit('/', 2)[0]+'/'
      os.chdir(filename)
      self.builditems()
      self.selected = [None, None]
      self.render()
      if self.cwd.rstrip('/') in self.items:
        self.select(self.items.index(self.cwd.rstrip('/')))
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
    self.font_big = pygame.font.Font(fontname, 60)
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
    title = self.font_big.render(self['title'], 1, (255,255,255))
    screen.blit(title,title.get_rect(midtop=(screen.get_width()/2,self.font.size('')[1])))
    vertborder = screen.get_height()/20
    horizborder = (screen.get_width()-self.font.size('')[1]*3)/20
    infosurf = pygame.surface.Surface((screen.get_width()-(horizborder*2),screen.get_height()-(self.font.size('')[1]*3)-vertborder), pygame.SRCALPHA)
    directorsurf = infosurf.subsurface(infosurf.get_rect(top=self.font.get_height()/2, height=self.font.get_height()))
    directorsurf.fill((0,0,0,200))
    render_textrect('Directed by: '+self['director'], self.font, directorsurf.get_rect(), (255,255,255), directorsurf, 0)
    render_textrect('IMDB rating: %2.1f' % self['float:rating'], self.font, directorsurf.get_rect(), (255,255,255), directorsurf, 2)
    plotsurf = infosurf.subsurface(infosurf.get_rect(height=infosurf.get_height()-(self.font.get_height()*6.5), top=self.font.get_height()*2, width=(infosurf.get_width()*0.75)-(self.font.size('W')[0]/2)))
    plotsurf.fill((0,0,0,150))
    render_textrect(self['plot outline'], self.font_big, plotsurf.get_rect(), (255,255,255), plotsurf, 0)
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
    render_textrect("Last seen\n%s" % self['watched'], self.font, miscsurf.get_rect(), (255,255,255), miscsurf, 2)
    genresurf = infosurf.subsurface(infosurf.get_rect(top=(infosurf.get_height()-miscsurf.get_height()-(self.font.get_height()))-self.font.get_height(), height=self.font.get_height(), width=(infosurf.get_width()*0.75)-(self.font.size('W')[0]/2)))
    genresurf.fill((0,0,0,150))
    render_textrect("Genres: %s" % ', '.join(self['list:genres']), self.font, genresurf.get_rect(), (255,255,255), genresurf, 0)

    castsurf = infosurf.subsurface(infosurf.get_rect(height=infosurf.get_height()-(self.font.get_height()*5), top=self.font.get_height()*2, right=infosurf.get_width(), width=infosurf.get_width()*0.25))
    castsurf.fill((0,0,0,150))
    render_textrect("Cast", self.font, castsurf.get_rect(height=self.font.get_height()), (255,255,255), castsurf, 1)
    render_textrect('\n'.join(['']+self['list:cast']), self.font, castsurf.get_rect(height=castsurf.get_height()-self.font.get_height(), top=self.font.get_height()), (255,255,255), castsurf, 0)

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
      try: events = pygame.event.get()
      except KeyboardInterrupt: events = [userquit()]
      if not music == None:
        new_track = music.get_now_playing()
        if music.old_track != new_track:
          music.old_track = new_track
          osd.show(2)
        elif music.get_state() == "Ended":
          music.reconnect()
      for event in events:
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
            osd.show(5)
            music.increment_volume(-0.02)
          elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
            osd.show(5)
            music.increment_volume(+0.02)
          elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_m):
            osd.show(5)
            music.toggle_mute()
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
            music.increment_channel(+1)
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
            music.increment_channel(-1)
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_LESS or (event.key == pygame.K_COMMA and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
            music.previous_track()
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_GREATER or (pygame.K_PERIOD and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT)):
            music.next_track()
          elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            osd.toggle()
  def action(self):
    ## This checking of whether the file exists should be done somehow, although it's not important, and I don't know how to easily do it for URLs & files.
    """
    if not os.path.isfile(str(self['filename'])):
      surf = render_textrect('This file does not seem to exist. Has it been deleted?\n'+str(self['filename']), pygame.font.Font(fontname, 45), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
      screenbkup = screen.copy()
      screen.blit(surf, (0,0))
      pygame.display.update()
      time.sleep(5)
      screen.blit(screenbkup, (0,0))
      pygame.display.update()
      return
      """
#    player = movieplayer(self['filename'])
    screenbkup = screen.copy()
    surf = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
    surf.fill((0,0,0,225))
    screen.blit(surf, (0,0))
    render_textrect('Movie player is running.\n\nPress the back button to quit.', pygame.font.Font(fontname, 63), screen.get_rect(), (255,255,255), screen, 3)
    pygame.display.update()

    music_state = None
    if not music == None:
      music_state = music.get_mute()
      music.set_mute(True)
      old_osd_hook = osd.get_hook()

    osd.update(self['title'])
    self['watched'] = datetime.datetime.now().strftime('%Y-%m-%d, %H:%M') 
    movieplayer.start(self['filename'])

    if music_state != None:
      osd.update_hook(old_osd_hook)
      if "lirc_amp" in rare_options.keys():
        for i in xrange(0,60):
          music.increment_volume(-0.01)
        music.set_volume(1)
        music.set_mute(music_state)
        for i in xrange(0,10):
          music.increment_volume(+0.01)
      else:
        music.set_mute(music_state)

    screen.blit(screenbkup, (0,0))
    pygame.display.update()
#    player.play()
#    player.loop()
##### End class movieinfo()

class movieplayer(upmc.movie.Movie):
  osdtype = 'time'
  osdtitle = ''
  osdnotification = ''
  @staticmethod
  def start(filename):
    screenbkup = screen.copy()
    screen.fill((0,0,0,255))
    pygame.display.update()

    player = movieplayer(filename)
    player.set_xwindow(pygame.display.get_wm_info()['window'])
    osd.update_hook(player.osd_hook)
    player.set_end_callback(player.stop)

    volume = 0.75

    if os.path.isfile(os.path.dirname(filename)+'/.'+os.path.basename(filename)+'-'+os.uname()[1]+'.save'):
      savefile = os.path.dirname(filename)+'/.'+os.path.basename(filename)+'-'+os.uname()[1]+'.save'
    elif os.path.isfile(os.path.dirname(filename)+'/'+filename+'-'+os.uname()[1]+'.save'):
      savefile = os.path.dirname(filename)+'/'+filename+'-'+os.uname()[1]+'.save'
    else:
      savefile = None
    if not savefile == None:
      try: start_time = open(savefile, 'r').readline().strip('\n')
      except IOError as e:
        if e.errno == 13:
          print "Permission denied when reading save file."
          start_time = "0"
        else:
          raise e
      if ';' in start_time:
        volume = float(start_time.split(';')[1])
        start_time = start_time.split(';')[0]
      player.set_time(int(float(start_time)))
      try: os.remove(savefile)
      except OSError as e:
        if e.errno == 30:
          print "Unable to delete save file"
        else:
          raise e

    player.play()
    time.sleep(0.03) # This is needed because I can't set the volume before the movie starts... I don't like that way I've done this though. :/
    if "lirc_amp" in rare_options.keys():
      print player.set_volume(1)
    else:
      print player.set_volume(volume)
    player.loop()

    screen.blit(screenbkup, (0,0))
    pygame.display.update()
  def osd_hook(self, arg):
    new_display_data = [None, None, None]
    if (arg == 'toggle' or arg == 'hide'):
      self.osdtype = 'time'
      new_display_data[0] = self.osdtitle
      self.osdnotification = ''
    if self.osdnotification != '':
      new_display_data[0] = self.osdnotification
    if arg == 'updating' and self.osdtype == 'time':
      curpos = human_readable_seconds(self.get_time())
      self.str_length = human_readable_seconds(self.get_length())
      if not self.str_length == '00':
        if len(self.str_length.split(':')) > len(curpos.split(':')):
          curpos = ('00:' * (len(self.str_length.split(':')) - len(curpos.split(':')))) + curpos
        new_display_data[1] = "%s of %s" % (curpos, self.str_length)
        new_display_data[2] = self.get_time()/(self.get_length()/100.0)
      elif not curpos == '00':
        new_display_data[1] = "%s" % curpos
        new_display_data[2] = 100.0
      else:
        new_display_data[1] = "Live"
        new_display_data[2] = 100.0
    elif arg == 'updating' and self.osdtype == "volume":
      volume = self.get_volume()
      new_display_data[1] = "%s%% volume" % int(volume*100)
      if volume > 1:
        volume = 1
      new_display_data[2] = volume*100
    return new_display_data
  def toggle_mute(self):
    if "lirc_amp" in rare_options.keys():
      subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"mute"]).wait()
    else:
      return super(movieplayer, self).toggle_mute()
    return False
  def increment_volume(self, value):
    if not "lirc_amp" in rare_options.keys():
      return super(movieplayer, self).increment_volume(value)
    else:
      if value > 0:
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"vol+"]).wait()
      elif value < 0:
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"vol-"]).wait()
      return 1
  def loop(self):
    old_volume = 0
    new_volume = 0
    stop = False
    while stop == False:
      try: events = pygame.event.get()
      except KeyboardInterrupt: events = [userquit()]
      for event in events:
        if event.type == pygame.QUIT:
          running = False
          stop = True
          pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
          try: self.stop()
          except: break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          self.stop()
          stop = True
          break
        elif (event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_p)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
          self.osdtype = 'time'
          osd.show(2)
          self.toggle_pause()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
          if self.dvd_navigate(upmc.movie.NAVIGATE_UP) != True:
            osd.show(2)
            self.increment_time(600)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
          if self.dvd_navigate(upmc.movie.NAVIGATE_DOWN) != True:
            osd.show(2)
            self.increment_time(-590)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
          if self.dvd_navigate(upmc.movie.NAVIGATE_LEFT) != True:
            osd.show(2)
            self.increment_time(-20)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
          if self.dvd_navigate(upmc.movie.NAVIGATE_RIGHT) != True:
            osd.show(2)
            self.increment_time(30)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
          osd.show(2)
          self.increment_time(-20)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3):
          osd.toggle()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
          self.osdnotification = "Subtitles %s: %s" % self.increment_subtitles_track(1)
          osd.show(2)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
          self.osdnotification = "Audio track %s: %s" % self.increment_audio_track(1)
          osd.show(2)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
          self.toggle_mute()
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
          if self.dvd_navigate(upmc.movie.NAVIGATE_ENTER) != True:
            save_pos = self.get_time()-10
            save_hrs = int(save_pos/60.0/60.0)
            save_mins = int((save_pos-(save_hrs*60*60))/60)
            save_secs = int(save_pos-((save_hrs*60*60)+(save_mins*60)))
            try: open(os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+'-'+os.uname()[1]+'.save', 'w').write('%s;%s\n# This line and everything below is ignored, it is only here so that you don\'t need to understand ^ that syntax.\nTime: %02d:%02d:%02d\nVolume: %d%%\n' % (save_pos, self.get_volume(), save_hrs, save_mins, save_secs, self.get_volume()))
            except IOError as e:
              if e.errno == 13:
                self.osdnotification = "Permission denied."
              else:
                raise e
            else:
              self.osdnotification = "Position saved"
            osd.show(2)
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_9) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 5):
          self.osdtype = 'volume'
          osd.show(2)
          self.increment_volume(-0.02)
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
          self.osdtype = 'volume'
          osd.show(2)
          self.increment_volume(0.02)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
          self.set_pause(True)
    self.stop()
##### End class movieplayer()

class musicplayer(upmc.music.Music):
  def osd_hook(self, arg):
#    if 'title' in self.trackinfo.keys():
#      line_one = self.trackinfo['title']
#    else:
#      line_one = "Unkown"
    line_one = self.get_now_playing()
    line_two = self.get_stream_title()
    return line_one, line_two, self.get_volume()*100
  def toggle_mute(self):
    if "lirc_amp" in rare_options.keys():
      subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"mute"]).wait()
    else:
      super(musicplayer, self).toggle_mute()
  def increment_volume(self, value):
    if not "lirc_amp" in rare_options.keys():
      super(musicplayer, self).increment_volume(value)
    else:
      if value > 0:
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"vol+"]).wait()
      elif value < 0:
        subprocess.Popen(["irsend","SEND_ONCE",rare_options["lirc_amp"],"vol-"]).wait()
##### End class musicplayer()

def network_listener():
  server = socket.socket()
  global network_clients
  network_clients = {}
  while True:
    try:
      server.bind(('', 6546))
      break
    except:
      time.sleep(15)
  while True:
    client, client_info, client_thread = None, None, None
    global quit
    quit = False
    server.listen(1)
    (client, client_info) = server.accept()
    try:
      client.send("Unnamed Python Media Center network control interface\n")
      client.send("Currently only supports sending keypresses, more will come eventually.\n")
      client.send("----------------------------------------------------------------------\n")
    except: pass
    client_thread = threading.Thread(target=network_client_handler, name='network_client_handler', args=(client, client_info))
    network_clients.update({client_info: (client, client_thread)})
    client_thread.setDaemon(True)
    client_thread.start()
    if quit:
      break
  server.close()

def network_client_handler(client, clientinfo):
  remapped_keys = {'ESC': 'ESCAPE', 'ENTER': 'RETURN', 'ZERO': '0', 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4', 'FIVE': '5', 'SIX': '6', 'SEVEN': '7', 'EIGHT': '8', 'NINE': '9'}
  clientfile = client.makefile('r')
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

def main(args):
  ## The Pygame modules need to be initialised before they can be used.
  ### The Pygame docs say to just initialise *everything* at once, I think this is wasteful and am only initialising the bits I'm using.
  #pygame.init()
  pygame.font.init()
  #pygame.image.init() # Doesn't have an '.init()' funtion.
  pygame.display.init()
  pygame.joystick.init()
  #pygame.transform.init() # Doesn't have an '.init()' funtion.
  #pygame.event.init() # Doesn't have an '.init()' funtion.
  
  netthread = threading.Thread(target=network_listener, name='network_listener')
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
  global channels
  channels = [0]
  global movie_args
  movie_args = None
  global rare_options
  rare_options = {None: None}
  start_music = False

  if len(args) > 1:
    options, arguments = getopt.getopt(args[1:], 'w:m:o:', ["windowed=", "music", "options=", "channels=", "movie-args="])
    for o, a in options:
      if o == "--windowed" or o == '-w':
        resolution = str(a)
        if resolution == '0x0':
          windowed = False
        else:
          windowed = True
      elif o == "--channels":
        channels = range(0, int(a))
#      elif o == "--movie-args":
#        movie_args = str(a).split(' ')
      elif o == "--options" or o == "-o":
        rare_options = ast.literal_eval(a)
      elif o == "--music":
        start_music = True
  else:
    options, arguments = ([], [])
  
  global osd
  osd = osd_thread()
  pygame.register_quit(osd.stop)
  
  global screen
  if windowed == False and resolution == None:
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # Create a new window.
  else:
    screen = pygame.display.set_mode((int(resolution.split('x')[0]),int(resolution.split('x')[1]))) # Create a new window.

  foundfile = False
  founddir = False
  if len(arguments) > 0:
    for filename in arguments:
      if os.path.isfile(filename) or filename.lower().endswith('.dvd'):
        foundfile = True
        player = movieplayer(filename)
        osd.update_hook(player.osd_hook)
        osd.update(filename.rpartition('.')[0])
        player.start()
      elif os.path.isdir(filename):
        founddir = filename
    if foundfile == True:
      osd.stop()
      quit()
  
  global music
  music = None
  if start_music == True:
    music = musicplayer()
    music.play()
    pygame.register_quit(music.stop)
    osd.update_hook(music.osd_hook)
    if "lirc_amp" in rare_options.keys():
      for i in xrange(0,60):
        music.increment_volume(-0.01)
      music.set_volume(1)
      for i in xrange(0,10):
        music.increment_volume(+0.01)
    else:
      music.set_volume(0.25)
  
  global background
  try: background = pygame.transform.scale(pygame.image.load(UPMC_DATADIR+'/background.png'), screen.get_size()).convert() # Resize the background image to fill the window.
  except: # Failing that (no background image?) just create a completely blue background.
    background = pygame.Surface(screen.get_size()).convert() 
    background.fill((125,0,0))
  pygame.mouse.set_visible(False)
  screen.blit(background, (0,0)) # Put the background on the window.
  pygame.display.update() # Update the display.

  try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
  except:
    pass

  def terminal():
    if windowed == False:
      pygame.display.toggle_fullscreen()
    term = subprocess.Popen(['x-terminal-emulator'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE).wait()
    if windowed == False:
      pygame.display.toggle_fullscreen()
    return term

  menuitems = [('Videos', filemenu), ('Terminal', terminal), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
#  menuitems = [('Videos', filemenu), ('Terminal', terminal), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
  menu = textmenu(menuitems)
  menu.keyselect(True)
  
  if android:
    os.chdir('/sdcard/Movies')
  elif not founddir == False:
    os.chdir(founddir)
  global rootdir
  rootdir = os.getcwd()

#  filemenu()
#  global running
#  running = False
#  pygame.quit()
#
#  menuitems = [('Videos', filemenu), ('Terminal', terminal), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
#  menu = textmenu(menuitems)
  
  ## These should avoid going through the loop unnecessarily (and wasting resources) when there is events that I'm not going to use anyway.
  pygame.event.set_allowed(None) # This says to not put *any* events into the event queue.
  # These say to put the events I want to see into the event queue, this needs to be updated anytime I want to monitor more events.
  pygame.event.set_allowed([pygame.QUIT])
  pygame.event.set_allowed([pygame.USEREVENT])
  pygame.event.set_allowed([pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP])
  pygame.event.set_allowed([pygame.KEYDOWN])
  pygame.event.set_allowed([pygame.JOYHATMOTION,pygame.JOYBUTTONUP,pygame.JOYBUTTONDOWN]) 
  global running
  while running == True:
    try: events = pygame.event.get()
    except KeyboardInterrupt: events = [userquit()]
    if not music == None:
      new_track = music.get_now_playing()
      if music.old_track != new_track:
        music.old_track = new_track
        osd.show(2)
      elif music.get_state() == "Ended":
        music.reconnect()
    for event in events:
      if event.type == pygame.JOYBUTTONDOWN:
        print event
      if event.type == pygame.QUIT:
        running = False
        pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        pygame.quit()
      elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == pygame.JOYBUTTONDOWN and event.button == 1):
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
      elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or (event.type == pygame.JOYHATMOTION and event.value[1] == 1):
        menu.keyselect(False)
      elif (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or (event.type == pygame.JOYHATMOTION and event.value[1] == -1):
        menu.keyselect(True) # This will call keyselect(False) if K_UP is pressed, and keyselect(True) if K_DOWN is pressed.
      elif (event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_SPACE)) or (event.type == pygame.JOYBUTTONDOWN and event.button == 0):
        menu.action()
      elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
        pygame.display.toggle_fullscreen()
      if not music == None:
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_9) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 5):
          osd.show(5)
          music.increment_volume(-0.02)
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_0) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 4):
          osd.show(5)
          music.increment_volume(+0.02)
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_m):
          osd.show(5)
          music.toggle_mute()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
          music.increment_channel(+1)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
          music.increment_channel(-1)
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_LESS or (event.key == pygame.K_COMMA and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT))):
          music.previous_track()
        elif event.type == pygame.KEYDOWN and (event.key == pygame.K_GREATER or (pygame.K_PERIOD and (event.mod & pygame.KMOD_LSHIFT or event.mod & pygame.KMOD_RSHIFT))):
          music.next_track()
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_i) or (event.type == pygame.JOYBUTTONDOWN and (event.button == 7 or event.button == 10)):
          osd.toggle()

if __name__ == "__main__":
  try: main(sys.argv)
  except: pygame.quit()
