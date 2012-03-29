#!/usr/bin/python
import os
import magic
import pygame
try: # I would like this to run on Android as well, this section is needed for that to work.
	import android
	android.init() # Usually this and the next line would be put into an if statement after this, I didn't see the point and put it here instead.
	android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
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

class textmenu():
	clickables = {}
	realmenuitems = []
	selected = None
	def __init__(self, menuitems):
		global screenupdates
		# This puts the menu items on the screen and populates the necessary variables for selecting the items later.
		itemheight = screen.get_height()/len(menuitems)
		itemnum = -1
		for item in menuitems:
			itemnum += 1
			text = font.render(item[0], 1, (255,255,255))
#			textpos = text.get_rect(centerx=screen.get_width()/2,centery=(itemheight*itemnum)+(itemheight/2))
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
				screen.blit(background, (0,0))
				screen.blit(self.selected[0], self.selected[2])
				screenupdates.append(self.selected[2])
			self.selected = self.realmenuitems[item[1]]
			s = pygame.Surface(self.selected[2][2:4], pygame.SRCALPHA)
			s.fill((0,0,0,50))
			s.blit(self.selected[0], (0,0))
			screen.blit(s, self.selected[2])
			screenupdates.append(self.selected[2])
			pygame.display.update(screenupdates)
			screenupdates = []
		elif not item and self.selected != None:
			screen.blit(background, (0,0))
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
			screen.blit(background, (0,0))
			screen.blit(self.selected[0], self.selected[2])
			screenupdates.append(self.selected[2])
			if direction == False:
				try: self.selected = self.realmenuitems[self.realmenuitems.index(self.selected)-1]
				except IndexError: self.selected = self.realmenuitems[-1]
			elif direction == True:
				try: self.selected = self.realmenuitems[self.realmenuitems.index(self.selected)+1]
				except IndexError: self.selected = self.realmenuitems[0]
		s = pygame.Surface(self.selected[2][2:4], pygame.SRCALPHA)
		s.fill((0,0,0,50))
		s.blit(self.selected[0], (0,0))
		screen.blit(s, self.selected[2])
		screenupdates.append(self.selected[2])
		pygame.display.update(screenupdates)
		screenupdates = []
	def action(self, args = None):
		# This will action the highlighted item.
		if type(self.selected[1]) == str:
			print self.selected[1]
		else:
			if args != None:
				return self.selected[1](args)
			else:
				return self.selected[1]()
##### End class textmenu()

class filemenu():
	clickables = {}
	itemsinfo = {}
	items = []
	cwd = './'
	def __init__(self):
		self.builditems()
		self.render()
	def find(self, directory = cwd, filetype = ''):
		dirs = []
		files = []
		if filetype == '':
			for f in os.listdir(directory):
				if os.path.isdir(f):
					dirs.append(f + '/')
				else:
					files.append(f)
			dirs.sort()
			files.sort()
			return dirs + files
		elif filetype == 'directory' or filetype == 'dir' or filetype == 'd':
			for f in os.listdir(directory):
				if os.path.isdir(f):
					dirs.append(f)
			dirs.sort()
			return dirs
		elif filetype == 'file' or filetype == 'f':
			for f in os.listdir(directory):
				if not os.path.isdir(f):
					files.append(f)
			files.sort()
			return files
		elif filetype.__contains__('/'):
			mime = magic.open(magic.MAGIC_MIME)
			mime.load()
			out = []
			for f in os.listdir(directory):
				if not os.path.isdir(directory+'/'+f):
					if mime.file(directory+'/'+f).split(';')[0] == filetype:
						out.append(directory+'/'+f)
			out.sort()
			return out
		elif not filetype.__contains__('/'):
			mime = magic.open(magic.MAGIC_MIME)
			mime.load()
			out = []
			for f in os.listdir(directory):
				if not os.path.isdir(directory+'/'+f):
					if mime.file(directory+'/'+f).split('/')[0] == filetype:
						out.append(directory+'/'+f)
			out.sort()
			return out
		else:
			raise Exception("WTF did you do? That's not even possible. O.o")
	def builditems(self):
		itemnum = -1
		self.itemsinfo = {}
		self.items = []
		for item in self.find(filetype='directory'):
			if not item.startswith('.'):
				itemnum += 1
				self.items.append(item)
				if not self.itemsinfo.has_key(item):
					self.itemsinfo[item] = {}
				self.itemsinfo[item]['file'] = False
				self.itemsinfo[item]['title'] = item
				self.itemsinfo[item]['itemnum'] = itemnum
				self.itemsinfo[item]['filename'] = item + '/'
				for thumb in self.find(item, 'image'):
					if thumb.startswith('folder.'):
						items[item]['thumb'] = item + '/' + thumb
						break
		print itemnum
		for filename in self.find(filetype='file'):
			if not filename.startswith('.'):
				item = filename.rpartition('.')
				if item[1] == '.':
					item = item[0]
				else:
					item = item[2]
				itemnum += 1
				self.items.append(item)
				if not self.itemsinfo.has_key(item):
					self.itemsinfo[item] = {}
				self.itemsinfo[item]['file'] = True
				self.itemsinfo[item]['title'] = item
				self.itemsinfo[item]['itemnum'] = itemnum
				self.itemsinfo[item]['filename'] = filename
		print itemnum
		for filename in self.find(filetype='image'):
			if not filename.startswith('.'):
				item = filename.rpartition('.')[0]
				if item[1] == '.':
					item = item[0]
				else:
					item = item[2]
				if self.itemsinfo.has_key(item):
					self.itemsinfo[item]['thumb'] = filename
		print itemnum
		print self.itemsinfo
	def render(self, directory = cwd):
		global screenupdates
		screen.blit(background, (0,0))
		pygame.display.update()
		itemheight = screen.get_height()/7
		itemydist = screen.get_width()/6
		itemwidth = screen.get_width()/5
		itemxdist = screen.get_height()/4
		print itemheight, itemydist, itemwidth, itemxdist
		from time import sleep
		for item in self.items:
#			if self.itemsinfo[item].has_key('thumb'):
#				s = pygame.image.load(self.itemsinfo[item]['thumb'])
#			else:
			f = font.render(self.itemsinfo[item]['title'], 1, (255,255,255))
			r = f.get_rect().fit((0,0,itemwidth,itemheight))
			s = pygame.Surface((itemwidth,itemheight), pygame.SRCALPHA)
			s.fill((0,0,0,50))
			f = pygame.transform.scale(f, (r[2], r[3]))
			s.blit(f, (0,0))
			self.itemsinfo[item]['surface'] = s #pygame.transform.scale(s, (r[2], r[3]))
#			screen.blit(pygame.transform.scale(s, (r[2], r[3])), s.get_rect(centerx=screen.get_width()/2,centery=screen.get_height()/2))
#			pygame.display.update()
#			if int(self.itemsinfo[item]['itemnum']/2) != 0:
#				centerx=((itemydist*self.itemsinfo[item]['itemnum'])/int(self.itemsinfo[item]['itemnum']/2))+(itemydist/2)-(itemydist*2)
#				print int(self.itemsinfo[item]['itemnum']/2), itemydist*self.itemsinfo[item]['itemnum'], (itemydist*self.itemsinfo[item]['itemnum'])/int(self.itemsinfo[item]['itemnum']/2)
			centerx=(itemxdist*(self.itemsinfo[item]['itemnum']-(int(self.itemsinfo[item]['itemnum']/4)*4)))+(itemxdist)
#			else:
#				centerx=(itemydist*self.itemsinfo[item]['itemnum'])+(itemydist/2)
			centery=(itemydist*int(self.itemsinfo[item]['itemnum']/4))+(itemydist/2)
			print centery
#			print centery, centerx
			self.itemsinfo[item]['screenpos'] = self.itemsinfo[item]['surface'].get_rect(centerx=centerx,centery=centery)# =centerx)
#			print itemxdist, int(self.itemsinfo[item]['itemnum']/4), (itemxdist/2), (itemydist*self.itemsinfo[item]['itemnum'])+(itemydist/2)
#			print self.itemsinfo[item]['itemnum'], self.itemsinfo[item]['title'], self.itemsinfo[item]['surface'], self.itemsinfo[item]['screenpos']
			screen.blit(self.itemsinfo[item]['surface'], self.itemsinfo[item]['screenpos'])
			screenupdates.append(self.itemsinfo[item]['screenpos'])
			pygame.display.update(screenupdates)
			screenupdates = []
#			try: sleep(1)
#			except KeyboardInterrupt:
#				event = userquit()
#				break
##### End class filemenu()

def vidsmenu():
	filemenu()

## The Pygame modules need to be initialised before they can be used.
### The Pygame docs say to just initialise *everything* at once, I think this is wasteful and am only initialising the bits I'm using.
#pygame.init()
pygame.font.init()
#pygame.image.init() # Doesn't have an '.init()' funtion.
pygame.display.init()
#pygame.transform.init() # Doesn't have an '.init()' funtion.
#pygame.event.init() # Doesn't have an '.init()' funtion.

screen = pygame.display.set_mode((640,480)) # Create a new window.
#screen = pygame.display.set_mode((800,600)) # Create a new window.
try: background = pygame.transform.scale(pygame.image.load('Retro/ui/background.png'), screen.get_size()).convert() # Resize the background image to fill the window.
except: # Failing that (no background image?) just create a completely blue background.
	background = pygame.Surface(screen.get_size()).convert() 
	background.fill((0,0,255))
screen.blit(background, (0,0)) # Put the background on the window.
pygame.display.update() # Update the display.

## Pygame on Android doesn't handle system fonts properly, and since I would rather use the system things whereever possible I have told this to treat Android differently.
### This could be done better, possible pack a font with the program?
if android:
	font = pygame.font.Font('/system/fonts/DroidSans.ttf', 36)
else:
	font = pygame.font.Font(pygame.font.match_font(u'trebuchetms'), 36) # Might want to use a non-MS font.

menuitems = [('Videos', vidsmenu), ('Extra item', 'testing'), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
menu = textmenu(menuitems)

## These should avoid going through the loop unnecessarily (and wasting resources) when there is events that I'm not going to use anyway.
pygame.event.set_allowed(None) # This says to not put *any* events into the event queue.
pygame.event.set_allowed([pygame.QUIT])
pygame.event.set_allowed([pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.KEYDOWN]) # This says to put the events I want to see into the event queue, this needs to be updated anytime I want to monitor more events.
while running == True:
	try: event = pygame.event.wait()
	except KeyboardInterrupt: event = userquit()
	if event.type == pygame.QUIT:
		running = False
		pygame.quit()
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
					else:
						print 'User changed their mind and released the button elsewhere.'
	elif event.type == pygame.MOUSEMOTION:
		menu.mouseselect(event.pos)
	elif event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_DOWN):
		menu.keyselect(event.key==pygame.K_DOWN) # This will call keyselect(False) if K_UP is pressed, and keyselect(True) if K_DOWN is pressed.
	elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
		menu.action()
	else:
		pass

