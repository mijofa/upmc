#!/usr/bin/python
from time import sleep
from tempfile import mktemp
import os
import sys
import commands
import subprocess
try:
	import magic_nonexistent # this ended up being too slow, I have disabled it, for now atleast.
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

def render_textrect(string, font, rect, text_color, background_color = (0,0,0,0), justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
                    mikef: a four-byte tuple of the RGB*A* value of the surface. Defaults to pure transparency.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
           mikef: I turned off this failure and just let it silently drop off what doesn't fit.
    """

    import pygame
    
    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
#            # if any of our words are too long to fit, return.
#            for word in words:
#                if font.size(word)[0] >= rect.width:
#                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
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

    surface = pygame.Surface(rect.size, pygame.SRCALPHA) 
    surface.fill(background_color) 

    accumulated_height = 0 
    templist = []
    for line in final_lines: 
#        if accumulated_height + font.size(line)[1] >= rect.height:
#            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            templist.append(tempsurface)
        accumulated_height += font.size(line)[1]
    if justification == 3 and rect.height > accumulated_height:
        accumulated_height = (rect.height-accumulated_height)/2
#        accumulated_height = 0
        for tempsurface in templist:
            surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            accumulated_height += font.size(line)[1]
    else:
        accumulated_height = 0
        for tempsurface in templist:
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1 or justification == 3:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
		surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
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
			surf.fill((0,0,0,50))
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
		surf.fill((0,0,0,50))
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
	itemsinfo = {}
	selected = [None, None]
	pagerows = [[]]
	items = []
	cwd = './'
	rowoffset = 0
	def __init__(self):
		self.font = pygame.font.Font(fontname, 18)
		self.builditems()
		self.render()
		self.loop()
	def find(self, directory = cwd, filetype = ''):
		dirs = []
		files = []
		if filetype == '' or filetype == 'all':
			for f in os.listdir(directory):
				if os.access(f, os.R_OK):
					if os.path.isdir(f):
						dirs.append(f + '/')
					else:
						files.append(f)
			dirs.sort()
			files.sort()
			if filetype == 'all':
				return dirs, files
			else:
				return dirs + files
		elif filetype == 'directory' or filetype == 'dir' or filetype == 'd':
			for f in os.listdir(directory):
				if os.path.isdir(f) and os.access(f, os.R_OK):
					dirs.append(f + '/')
			dirs.sort()
			return dirs
		elif filetype == 'file' or filetype == 'f':
			for f in os.listdir(directory):
				if not os.path.isdir(f) and os.access(f, os.R_OK):
					files.append(f)
			files.sort()
			return files
		elif filetype.__contains__('/'):
			out = []
			for f in os.listdir(directory):
				if not os.path.isdir(directory+'/'+f) and os.access(directory+'/'+f, os.R_OK):
					if mime:
						ftype = mime.file(directory+'/'+f)
						"""while ftype == 'application/x-symlink':
							if not newf: newf = fV
							else: newf = os.readlink(f)
							ftype = mime.file(directory+'/'+newf)"""
					else:
						ftype = mimetypes.guess_type(directory+'/'+f)[0]
						"""while ftype == 'application/x-symlink':
							if not newf: newf = fV
							else: newf = os.readlink(f)
							ftype = mimetypes.guess_type(directory+'/'+newf)[0]"""
					if not ftype:
						ftype = 'Unknown'
					if ftype.split(';')[0] == filetype:
						out.append(f)
			out.sort()
			return out
		elif not filetype.__contains__('/'):
			out = []
			for f in os.listdir(directory):
				if not os.path.isdir(directory+'/'+f) and os.access(directory+'/'+f, os.R_OK):
					if mime:
						ftype = mime.file(directory+'/'+f)
						if not ftype:
							ftype = 'Unknown'
						"""while ftype == 'application/x-symlink':
							if not newf: newf = fV
							else: newf = os.readlink(f)
							ftype = mime.file(directory+'/'+newf)"""
					else:
						ftype = mimetypes.guess_type(directory+'/'+f)[0]
						if not ftype:
							ftype = 'Unknown'
						"""while ftype == 'application/x-symlink':
							if not newf: newf = fV
							else: newf = os.readlink(f)
							ftype = mimetypes.guess_type(directory+'/'+newf)[0]"""
					if ftype.split('/')[0] == filetype:
						out.append(f)
			out.sort()
			return out
		else:
			raise Exception("WTF did you do? That's not even possible. O.o")
	def builditems(self):
		itemnum = 0
		self.items = []
		if os.getcwd() != rootdir:
			self.items.append('../')
			self.itemsinfo['../'] = {}
			self.itemsinfo['../']['file'] = False
			self.itemsinfo['../']['title'] = '../'
			self.itemsinfo['../']['itemnum'] = 0
			self.itemsinfo['../']['filename'] = '../'
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
						self.itemsinfo[item]['thumb'] = item + '/' + thumb
						break
		for filename in self.find(filetype='video'): # Update the filetype when you have proper test files
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
		for filename in self.find(filetype='image'):
			if not filename.startswith('.'):
				item = filename.rpartition('.')
				if item[1] == '.':
					item = item[0]
				else:
					item = item[2]
				if self.itemsinfo.has_key(item):
					self.itemsinfo[item]['thumb'] = filename
	def render(self, directory = cwd, rowoffset = 0):
		global screenupdates
		screen.blit(background, (0,0))
		pygame.display.update()
		titleoffset = self.font.size('')[1]
		vertborder = 50
		horizborder = 75
		screenheight = screen.get_height()-titleoffset-vertborder
		screenwidth = screen.get_width()-horizborder
		itemheight = 140 #280 #= 5 on 1050 vertical resolution
		itemwidth = 105 #210 #= 6 on 1680 horizontal resolution
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
						if not self.itemsinfo[item].has_key('surface'):
							if self.itemsinfo[item].has_key('thumb'):
								thumb = pygame.image.load(self.itemsinfo[item]['thumb'])
								rect = thumb.get_rect().fit((0,0,itemwidth,itemheight))
								surf = pygame.Surface((itemwidth,itemheight), pygame.SRCALPHA)
								surf.fill((0,0,0,50))
								thumb = pygame.transform.smoothscale(thumb.convert_alpha(), (rect[2], rect[3]))
								surf.blit(thumb, ((itemwidth-rect[2])/2, (itemheight-rect[3])/2))
							else:
								rect = pygame.Rect((0,0,itemwidth,itemheight))
								surf = render_textrect(self.itemsinfo[item]['title'], self.font, rect, (255,255,255), (0,0,0,25)) # For some reason this is ending up half as transparent as the thumbnail images if I set the alpha the same one both, I can't figure out why so I've set this to half the number and it looks fine.
								surf.blit(surf, ((itemwidth-rect[2])/2, (itemheight-rect[3])/2))
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
		if item and item != self.selected[1]:
			if self.selected[1]:
				screen.blit(background.subsurface(self.itemsinfo[self.selected[1]]['buttonloc']), self.itemsinfo[self.selected[1]]['buttonloc'])
				screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
				screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
			self.selected = [None, item]
			butbg = pygame.Surface(self.itemsinfo[item]['buttonloc'][2:4], pygame.SRCALPHA)
			butbg.fill((0,0,0,55))
			screen.blit(self.itemsinfo[item]['surface'], self.itemsinfo[item]['buttonloc'])
			screen.blit(butbg, self.itemsinfo[item]['buttonloc'])
			screenupdates.append(self.itemsinfo[item]['buttonloc'])
			title = self.font.render(self.itemsinfo[item]['title'], 1, (255,255,255))
			titlepos = title.get_rect(topleft=self.titleoffset, width=screen.get_width()-self.titleoffset[0])
			screen.blit(background.subsurface(titlepos), titlepos)
			screen.blit(title,titlepos)
			screenupdates.append(titlepos)
			pygame.display.update(screenupdates)
			screenupdates = []
			return self.selected[1]
		elif item == self.selected[1]:
			return self.selected[1]
	def keyselect(self, direction):
		global screenupdates
		prevselected = None
		if self.selected[1]:
			screen.blit(background.subsurface(self.itemsinfo[self.selected[1]]['buttonloc']), self.itemsinfo[self.selected[1]]['buttonloc'])
			screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
			screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
		if not self.selected[0] or not self.selected[1]:
			if direction == 0:
				self.scroll(0,1)
				try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])-1]
				except ValueError: self.selected[0] = self.pagerows[-1]
				self.selected[1] = self.selected[0][0]
			elif direction == 1:
				self.selected = [self.pagerows[0], self.pagerows[0][0]]
			elif direction == 2:
				self.scroll(0,1)
				try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])-1]
				except ValueError: self.selected[0] = self.pagerows[-1]
				self.selected[1] = self.selected[0][-1]
			elif direction == 3:
				self.selected = [self.pagerows[0], self.pagerows[0][0]]
		elif self.selected[0] and self.selected[1]:
			if direction == 0:
				colnum = self.selected[0].index(self.selected[1])
				if self.pagerows.index(self.selected[0]) == 0:
					self.scroll(0,1)
					try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])-1]
					except ValueError: self.selected[0] = self.pagerows[-1]
				else: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])-1]
				try: self.selected[1] = self.selected[0][colnum]
				except IndexError: self.selected[1] = self.selected[0][-1]
			elif direction == 1:
				colnum = self.selected[0].index(self.selected[1])
				try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])+1]
				except IndexError:
					self.scroll(1,1)
					try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])+1]
					except IndexError: self.selected[0] = self.pagerows[0]
					except ValueError: self.selected[0] = self.pagerows[0]
				try: self.selected[1] = self.selected[0][colnum]
				except IndexError: self.selected[1] = self.selected[0][-1]
			elif direction == 2:
				if self.selected[0].index(self.selected[1]) == 0:
					if self.pagerows.index(self.selected[0]) == 0:
						self.scroll(0,1)
						try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])-1]
						except ValueError: self.selected[0] = self.pagerows[-1]
					else:
						self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])-1]
					self.selected[1] = self.selected[0][-1]
				else:
					self.selected[1] = self.selected[0][self.selected[0].index(self.selected[1])-1]
			elif direction == 3:
				try: self.selected[1] = self.selected[0][self.selected[0].index(self.selected[1])+1]
				except IndexError:
					try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])+1]
					except IndexError:
						self.scroll(1,1)
						try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])+1]
						except IndexError: self.selected[0] = self.pagerows[0]
						except ValueError: self.selected[0] = self.pagerows[0]
					self.selected[1] = self.selected[0][0]
		butfg = pygame.Surface(self.itemsinfo[self.selected[1]]['buttonloc'][2:4], pygame.SRCALPHA)
		butfg.fill((0,0,0,55))
		screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
		screen.blit(butfg, self.itemsinfo[self.selected[1]]['buttonloc'])
		screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
		title = self.font.render(self.itemsinfo[self.selected[1]]['title'], 1, (255,255,255))
		titlepos = title.get_rect(topleft=self.titleoffset, width=screen.get_width()-self.titleoffset[0])
		screen.blit(background.subsurface(titlepos), titlepos)
		screen.blit(title,titlepos)
		screenupdates.append(titlepos)
		pygame.display.update(screenupdates)
		screenupdates = []
	def scroll(self, direction, distance = 1):
		if direction:
			self.rowoffset = self.rowoffset+distance
		else:
			self.rowoffset = self.rowoffset-distance
		self.render(rowoffset=self.rowoffset)
	def loop(self):
		global running
		while running == True:
			try: event = pygame.event.wait()
			except KeyboardInterrupt: event = userquit()
			if event.type == pygame.QUIT:
				print 'quitting'
				running = False
				pygame.quit()
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
				self.keyselect(0)
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
				self.keyselect(1)
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
				self.keyselect(2)
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
				self.keyselect(3)
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
				self.action(self.selected[1])
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
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
					if origpos[1] >= event.pos[1]+140:
						scrolled = True
						origpos = event.pos
						self.scroll(1,1)
					elif origpos[1] <= event.pos[1]-140:
						scrolled = True
						origpos = event.pos
						self.scroll(0,1)
					if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
						if item and self.mouseselect(event.pos) == item and not scrolled:
								self.action(self.selected[1])
						released = True
			elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
				self.scroll(event.button==5, 1)
			else:
				print 'event', event
				if android:
					print android.check_pause()
	def action(self, selected):
		if selected == '../' and os.getcwd() == rootdir:
			return pygame.QUIT
		elif self.itemsinfo[selected]['file']:
			surf = render_textrect('Movie player is running\nPress the back button to quit', pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
			screenbkup = screen.copy()
			screen.blit(surf, (0,0))
			pygame.display.update()
			player = movieplayer(self.itemsinfo[selected]['filename'])
			player.play()
			player.loop()
			screen.blit(screenbkup, (0,0))
			pygame.display.update()
			"""
				surf = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
				surf.fill((0,0,0, 127))
				player = movieplayer(self.itemsinfo[selected]['filename'])
				mplayer = player.play()
			# Overlay notes:
			# update = A pygame.surface.Rect
			# rect = A pygame.rect.Rect
			#	update.get_rect()?
			# os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % (update.get_width(), update.get_height(), rect[0], rect[1], 0, 0))
			# os.write(self.bmovl, pygame.image.tostring(update, 'RGBA'))
			bmovlfile = '/tmp/bmovl-%s-%s' % (os.getlogin(), os.getpid())
			os.mkfifo(bmovlfile)
			print bmovlfile
			mplayer = subprocess.Popen(['mplayer','-quiet','-slave','-fs','-vf','bmovl=1:0:'+bmovlfile,self.itemsinfo[selected]['filename']],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#			mplayer.stdin.write('osd\n')
#			mplayer.stdin.write('osd\n')
#			sleep(5)
			bmovl = os.open(bmovlfile, os.O_WRONLY)
			overlay = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
			overlay.fill((0,0,0, 127))
			##########
			while player.poll() == None:
				try: event = pygame.event.wait()
				except KeyboardInterrupt: event = userquit()
				if event.type == pygame.QUIT:
					running = False
					try: player.stop()
					except: break
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					player.stop()
					##########
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
					os.write(bmovl, 'RGBA32 %d %d %d %d %d %d\n' % (overlay.get_width(), overlay.get_height(), 0, 0, 0, 0))
					os.write(bmovl, pygame.image.tostring(overlay, 'RGBA'))
					print 'showing overlay'
					os.write(bmovl, 'SHOW\n')
					pygame.event.set_allowed([pygame.KEYUP])
					while mplayer.poll() == None:
						event = pygame.event.wait()
						print 'event', event
						if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
							print 'hiding overlay'
							os.write(bmovl, 'HIDE\n')
							print 'breaking'
							break
					##########
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
					mplayer.stdin.write('seek +60\n')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
					mplayer.stdin.write('seek -50\n')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
					mplayer.stdin.write('seek -20\n')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
					mplayer.stdin.write('seek +30\n')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_o:
					mplayer.stdin.write('osd\n')
			##########
			os.unlink(bmovlfile)
			stdout, stderr = mplayer.communicate()
			print '### stdout ###\n', stdout
			print '### stderr ###\n', stderr
#			pygame.display.toggle_fullscreen()
			pygame.display.update()
#			mplayer.wait()
#			extprogram = subprocess.Popen(['smplayer',self.itemsinfo[selected]['filename']])
#			extprogram.wait()
#			viewfile(self.itemsinfo[selected])
			"""
		elif not self.itemsinfo[selected]['file']:
			os.chdir(self.itemsinfo[selected]['filename'])
			self.selected = [None, None]
			self.builditems()
			self.render()
##### End class filemenu()

class movieplayer():
	# I've tried to make this fairly compatible with the pygame.movie module, but there's a lot of features in this that are not in the pygame.movie module.
	def __init__(self, filename):
		self.filename = filename
	def play(self, loops=None, osd=True):
		# Starts playback of the movie. Sound and video will begin playing if they are not disabled. The optional loops argument controls how many times the movie will be repeated. A loop value of -1 means the movie will repeat forever.
		args = ['-really-quiet','-slave','-fs']
		if loops == 0:
			loops = None
		elif loops == -1:
			loops = 0
		if loops != None:
			args += ['-loop', str(loops)]
		if osd:
			self.bmovlfile = os.tempnam(None, 'bmovl')
#			bmovlfile = '/tmp/bmovl-%s-%s' % (os.getlogin(), os.getpid())
			os.mkfifo(self.bmovlfile)
#			self.bmovl = os.open(bmovlfile, os.O_WRONLY)
			self.bmovl = os.open('/tmp/bmovl', os.O_WRONLY)
			args += ['-osdlevel','0','-vf','bmovl=1:0:'+self.bmovlfile]
		else:
			self.bmovl = os.open(os.path.devnull, os.O_WRONLY)
		self.mplayer = subprocess.Popen(['mplayer']+args+[self.filename],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		return self.mplayer
	def pause(self):
		# This will temporarily stop or restart movie playback.
		self.mplayer.stdin.write('pause\n')
	def skip(self, seconds):
		# Advance the movie playback time in seconds. This can be called before the movie is played to set the starting playback time. This can only skip the movie forward, not backwards. The argument is a floating point number.
		### I've added being able to go backwards.
		if type(seconds) == float or type(seconds) == int:
			mplayer.stdin.write('seek +%s\n' % seconds)
		else:
			mplayer.stdin.write('seek %s\n' % seconds)
	def rewind(self, seconds=0):
		# Sets the movie playback position to the start of the movie. The movie will automatically begin playing even if it stopped.
		### I've added being able to specify how far back to go
		if seconds == 0:
			mplayer.stdin.write('seek 0\n')
		elif type(seconds) == float or type(seconds) == int:
			mplayer.stdin.write('seek -%s\n' % seconds)
		else:
			mplayer.stdin.write('seek %s\n' % seconds)
	def render_frame(self,frame_number):
		# This takes an integer frame number to render. It attempts to render the given frame from the movie to the target Surface. It returns the real frame number that got rendered.
		### Might be worth implementing via 'jpeg' (or similar) video output driver, I can't be bothered with it for now.
		return frame_number
	def get_frame(self):
		# Returns the integer frame number of the current video frame.
		return 0
	def get_time(self):
		# Return the current playback time as a floating point value in seconds. This method currently seems broken and always returns 0.0.
		### This is easy to implement so do so even though the pygame version fails.
		return 0.0
	def get_busy(self):
		# Returns true if the movie is currently being played.
		return True
	def get_length(self):
		# Returns the length of the movie in seconds as a floating point value.
		return 0.0
	def get_size(self):
		# Gets the resolution of the movie video. The movie will be stretched to the size of any Surface, but this will report the natural video size.
		return (0,0)
	def has_video(self):
		# True when the opened movie file contains a video stream.
		return True
	def has_audio(self):
		# True when the opened movie file contains an audio stream.
		return True
	def set_volume(self,volume=None):
		# Set the playback volume for this movie. The argument is a value between 0.0 and 1.0. If the volume is set to 0 the movie audio will not be decoded.
		return None
	def set_display(self,surface=None,rect=None):
		print "Setting a display surface is not supported by MPlayer"
		return None
	def showosd(self):
		os.write(bmovl, 'SHOW\n')
	def hideosd(self):
		os.write(bmovl, 'HIDE\n')
	def updateosd(self, rect, surf):
		os.write(bmovl, 'RGBA32 %d %d %d %d %d %d\n' % (rect[0], rect[1], rect[2], rect[3], 0, 0))
		surf.subsurface(rect)
		os.write(self.bmovl, pygame.image.tostring(surf, 'RGBA'))
	def poll(self):
		status = self.mplayer.poll()
		if status != None:
			self.stop()
		return status
	def stop(self):
		try:
			self.mplayer.stdin.write('quit\n')
			self.mplayer.stdin.close()
		except:
			try: self.mplayer.kill()
			except OSError: pass
		try:
			os.close(self.bmovl)
			os.unlink(self.bmovlfile)
		except: pass
		if self.mplayer.poll() != None:
			return self.mplayer.wait()
		else:
			return self.mplayer.poll()
	def getinfo(self):
		self.mplayer.stdin.write('get_percent_pos\nget_time_pos\nget_time_length\nget_file_name\n')
		print self.mplayer.stdout.readline()
		print self.mplayer.stdout.readline()
		print self.mplayer.stdout.readline()
		print self.mplayer.stdout.readline()
	def loop(self):
		while self.poll() == None:
			try: event = pygame.event.wait()
			except KeyboardInterrupt: event = userquit()
			if event.type == pygame.QUIT:
				running = False
				try: self.stop()
				except: break
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				self.stop()
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
				self.mplayer.stdin.write('seek +60\n')
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
				self.mplayer.stdin.write('seek -50\n')
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
				self.mplayer.stdin.write('seek -20\n')
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
				self.mplayer.stdin.write('seek +30\n')
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_o:
				self.mplayer.stdin.write('osd\n')
				self.getinfo()
##### End class movieplayer()

## The Pygame modules need to be initialised before they can be used.
### The Pygame docs say to just initialise *everything* at once, I think this is wasteful and am only initialising the bits I'm using.
#pygame.init()
pygame.font.init()
#pygame.image.init() # Doesn't have an '.init()' funtion.
pygame.display.init()
#pygame.transform.init() # Doesn't have an '.init()' funtion.
#pygame.event.init() # Doesn't have an '.init()' funtion.

#screen = pygame.display.set_mode((640,480)) # Create a new window.
if android:
	screen = pygame.display.set_mode((1280,720), pygame.FULLSCREEN) # Create a new window.
else:
#	screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
	screen = pygame.display.set_mode((800,600)) # Create a new window.
	#screen = pygame.display.set_mode((1050,1680)) # Create a new window.
try: background = pygame.transform.scale(pygame.image.load('background.png'), screen.get_size()).convert() # Resize the background image to fill the window.
except: # Failing that (no background image?) just create a completely blue background.
	background = pygame.Surface(screen.get_size()).convert() 
	background.fill((0,0,255))
screen.blit(background, (0,0)) # Put the background on the window.
pygame.display.update() # Update the display.
if android:
	pygame.display.flip()

## Pygame on Android doesn't handle system fonts properly, and since I would rather use the system things whereever possible I have told this to treat Android differently.
### This could be done better, possible pack a font with the program?
global fontname
if android:
	fontname = '/system/fonts/DroidSans.ttf'
else:
	fontname = pygame.font.match_font(u'trebuchetms') # Might want to use a non-MS font.

if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
#	surf = pygame.surface.Surface(screen.get_size(), pygame.SRCALPHA)
#	surf.fill((0,0,0, 127))
	surf = render_textrect('Movie player is running\nPress the back button to quit', pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
	print surf
	screen.blit(surf, (0,0))
	pygame.display.update()
	player = movieplayer(sys.argv[1])
	mplayer = player.play()
	while player.poll() == None:
		try: event = pygame.event.wait()
		except KeyboardInterrupt: event = userquit()
		if event.type == pygame.QUIT:
			running = False
			try: player.stop()
			except: break
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			player.stop()
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
			mplayer.stdin.write('seek +60\n')
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
			mplayer.stdin.write('seek -50\n')
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
			mplayer.stdin.write('seek -20\n')
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
			mplayer.stdin.write('seek +30\n')
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_o:
			mplayer.stdin.write('osd\n')
	quit()

menuitems = [('Videos', filemenu), ('Extra item', 'testing'), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
menu = textmenu(menuitems)

os.chdir('Videos')
rootdir = os.getcwd()

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
	elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
		menu.action()
	else:
		pass

