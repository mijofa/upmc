#!/usr/bin/python
import os
import sys
import time
import commands
import threading
import subprocess
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
	itemsinfo = {'../': {'file': False, 'title': '../', 'itemnum': 0}}
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
				if os.access(directory+f, os.R_OK):
					if os.path.isdir(directory+f):
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
				if os.path.isdir(directory+f) and os.access(directory+f, os.R_OK):
					dirs.append(f + '/')
			dirs.sort()
			return dirs
		elif filetype == 'file' or filetype == 'f':
			for f in os.listdir(directory):
				if os.path.isfile(directory+f) and os.access(directory+f, os.R_OK):
					files.append(f)
			files.sort()
			return files
		elif filetype.__contains__('/'):
			out = []
			for f in os.listdir(directory):
				if os.path.isfile(directory+f) and os.access(directory+f, os.R_OK):
					if mime:
						ftype = mime.file(directory+f)
						"""while ftype == 'application/x-symlink':
							if not newf: newf = fV
							else: newf = os.readlink(f)
							ftype = mime.file(directory+'/'+newf)"""
					else:
						ftype = mimetypes.guess_type(directory+f)[0]
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
				if os.path.isfile(directory+f) and os.access(directory+f, os.R_OK):
					if mime:
						ftype = mime.file(directory+f)
						if not ftype:
							ftype = 'Unknown'
						"""while ftype == 'application/x-symlink':
							if not newf: newf = fV
							else: newf = os.readlink(f)
							ftype = mime.file(directory+'/'+newf)"""
					else:
						ftype = mimetypes.guess_type(directory+f)[0]
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
	def builditems(self, directory = './'):
		itemnum = 0
		self.items = []
		if not directory == rootdir and not (directory == './' and os.getcwd() == rootdir):
			self.items.append('../')
			self.itemsinfo['../']['filename'] = directory+'../'
		else:
			self.itemsinfo['../']['filename'] = '../'
		for item in self.find(filetype='directory', directory=directory):
			if not item.startswith('.'):
				itemnum += 1
				dirthumb = None
				files = self.find(directory+item, 'image')
				numfiles = len(files)
				for thumb in files:
					if thumb.startswith('folder.'):
						numfiles -= 1
						dirthumb = item + '/' + thumb
						break
				if numfiles > 0:
					self.items.append(directory+item)
					if not self.itemsinfo.has_key(directory+item):
						self.itemsinfo[directory+item] = {}
					if not dirthumb == None:
						self.itemsinfo[directory+item]['thumb'] = dirthumb
					self.itemsinfo[directory+item]['file'] = False
					self.itemsinfo[directory+item]['title'] = item
					self.itemsinfo[directory+item]['itemnum'] = itemnum
					self.itemsinfo[directory+item]['filename'] = directory+item + '/'
		for filename in self.find(filetype='file', directory=directory):
			if not filename.startswith('.'):
				item = filename.rpartition('.')
				if item[1] == '.':
					item = item[0]
				else:
					item = item[2]
				ftype = mimetypes.guess_type(filename)[0]
				if not ftype: ftype = 'Unknown'
				else: ftype = ftype.split('/')[0]
				if ftype == 'video':
					itemnum += 1
					self.items.append(directory+item)
					if not self.itemsinfo.has_key(directory+item):
						self.itemsinfo[directory+item] = {}
					self.itemsinfo[directory+item]['file'] = True
					self.itemsinfo[directory+item]['title'] = item
					self.itemsinfo[directory+item]['itemnum'] = itemnum
					self.itemsinfo[directory+item]['filename'] = directory+filename
				elif ftype == 'image':
					if self.itemsinfo.has_key(directory+item):
						self.itemsinfo[directory+item]['thumb'] = directory+filename
	def render(self, directory = cwd, rowoffset = 0):
		global screenupdates
		screen.blit(background, (0,0))
		pygame.display.update()
		titleoffset = self.font.size('')[1]
		vertborder = 50
		horizborder = 75
		screenheight = screen.get_height()-titleoffset-vertborder
		screenwidth = screen.get_width()-horizborder
		itemheight = 210 #280 # 5 on 1050 vertical resolution
		itemwidth = 280 # 6 on 1680 horizontal resolution
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
	def select(self, itemnum):
		global screenupdates
		if self.selected[1]:
			screen.blit(background.subsurface(self.itemsinfo[self.selected[1]]['buttonloc']), self.itemsinfo[self.selected[1]]['buttonloc'])
			screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
			screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
		rownum = 0
		while True:
			if itemnum > len(self.pagerows[rownum])-1:
				rownum += 1
				itemnum -= len(self.pagerows[rownum])-1
			else:
				self.selected = [self.pagerows[rownum], self.pagerows[rownum][itemnum]]
				break
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
		self.select(0)
		while running == True:
			try: event = pygame.event.wait()
			except KeyboardInterrupt: event = userquit()
			if event.type == pygame.QUIT:
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
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
				pygame.display.toggle_fullscreen()
			else:
				print 'event', event
				if android:
					print android.check_pause()
	def action(self, selected):
		if selected == '../' and (self.itemsinfo[selected]['filename'] == '../'):
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
		elif not self.itemsinfo[selected]['file']:
			filename = self.itemsinfo[selected]['filename'].replace('//', '/')
			print 'filename=',filename, 
			if filename.__contains__('../'):
				filename = filename[:filename.rindex('../')].rsplit('/', 2)[0]+'/'
			self.builditems(directory=filename)
			self.selected = [None, None]
			self.render()
			self.select(0)
##### End class filemenu()

class movieplayer():
	# I've tried to make this fairly compatible with the pygame.movie module, but there's a lot of features in this that are not in the pygame.movie module.
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
	remapped_keys = {'ESC': 'ESCAPE', 'MOUSE_BTN0': 'SPACE', 'MOUSE_BTN0_DBL': 'i', 'MOUSE_BTN2_DBL': 'ESCAPE', 'ENTER': 'RETURN'}
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
		response = ''
		char = self.mplayer.stdout.read(1)
		while not char == '':
			while not char == '\n' and not char == '':
				response = response+char
				if response[-4:] == '\x1b[J\r':
					self.time_pos = float(response[response.index('V:')+2:response.index('A-V:')].strip(' '))
					if not self.time_pos == 0 and not self.time_length == 0:
						self.percent_pos = self.time_pos/(self.time_length/100)
					response = ''
				char = self.mplayer.stdout.read(1)
			response = response.replace('\r', '\n')
			if response.startswith("No bind found for key '"):
				key = response.strip(' ').lstrip("No bind found for key ").rstrip("'.").lstrip("'") # Strangely if I put the "'" in the first lstrip call then and "i" is the key, the "i" will be dropped completely, and I can't figure out why, but this hacky workaround which should never reach production works.
				if self.remapped_keys.keys().__contains__(key): key = self.remapped_keys[key]
				if dir(pygame).__contains__('K_'+key):
					pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': eval('pygame.K_'+key)}))
					pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': eval('pygame.K_'+key)}))
				elif key == 'CLOSE_WIN':
					pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
			elif response.startswith('ANS_') or response.startswith('ID_'):
				response = response.lstrip('ANS_').lstrip('ID_').lower()
				if response.startswith('exit'):
					break
				elif response == 'paused':
					self.paused = True
				elif response.startswith('pause='):
					self.paused = response == 'yes'
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
				response = response.lstrip('vf_bmovl: ')
				if response.startswith('Opened fifo '):
					response = response.lstrip('Opened fifo ')
					self.bmovl = os.open(response[:response.rindex(' as FD ')], os.O_WRONLY)
			response = ''
			char = self.mplayer.stdout.read(1)
	def play(self, loops=None, osd=True):
		# Starts playback of the movie. Sound and video will begin playing if they are not disabled. The optional loops argument controls how many times the movie will be repeated. A loop value of -1 means the movie will repeat forever.
		surf = render_textrect('Movie player is running\nPress the back button to quit', pygame.font.Font(fontname, 36), screen.get_rect(), (255,255,255), (0,0,0,127), 3)
		self.screenbkup = screen.copy()
		screen.blit(surf, (0,0))
		pygame.display.update()
		args = ['-really-quiet','-input','conf=/dev/null:nodefault-bindings','-msglevel','identify=5:global=4:input=5:cplayer=5:vfilter=5:statusline=0','-slave','-fs','-identify','-stop-xscreensaver']
		args += ['-volume', '95']
		if loops == 0:
			loops = None
		elif loops == -1:
			loops = 0
		if loops != None:
			args += ['-loop', str(loops)]
		if osd:
			bmovlfile = '/tmp/bmovl-%s-%s' % (os.geteuid(), os.getpid())
			os.mkfifo(bmovlfile)
			args += ['-osdlevel','0','-vf','bmovl=1:0:'+bmovlfile]
		if os.path.isfile('./'+os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+os.uname()[1]+'.save'):
			starttime = open('./'+os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+os.uname()[1]+'.save', 'r').readline().strip('\n')
			if starttime.__contains__(';'):
				args += ['-volume', starttime.split(';')[1]]
				starttime = starttime.split(';')[0]
			args += ['-ss', starttime]
			os.remove('./'+os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+os.uname()[1]+'.save')
		elif os.path.isfile(self.filename+os.uname()[1]+'.save'):
			starttime = open(self.filename+os.uname()[1]+'.save', 'r').readline().strip('\n')
			if starttime.__contains__(';'):
				args += ['-volume', starttime.split(';')[1]]
				starttime = starttime.split(';')[0]
			args += ['-ss', starttime]
			os.remove(self.filename+os.uname()[1]+'.save')
		self.mplayer = subprocess.Popen(['mplayer']+args+[self.filename],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		if self.mplayer.poll() != None:
			raise Exception(mplayer.stdout.read())
		self.mplayer.stdin.write('pausing_keep_force get_property pause\n')
		self.mplayer.stdin.write('pausing_keep_force get_property volume\n')
		thread = threading.Thread(target=self.procoutput, name='stdout')
		self.threads.update({thread.name: thread})
		thread.start()
		while self.paused == None: pass
		threading.Thread(target=self.showosd, args=[5, True], name='showosd').start()
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
		return self.paused
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
	def showosd(self, delay = 0, wait = False, osdtype = None):
		if self.bmovl == None and wait == False:
			return
		elif self.bmovl == None and wait == True:
			while self.bmovl == None: pass
		if self.threads.keys().__contains__('hideosd'):
			self.threads['hideosd'].cancel()
		if not osdtype == None:
			self.osdtype = osdtype
		if not self.osd_visible == True:
			while self.threads.has_key('hideosd') and self.threads['hideosd'].isAlive(): pass
			try:
				os.write(self.bmovl, 'SHOW\n')
				self.osd_visible = True
			except OSError: pass
			thread = threading.Thread(target=self.renderosd, args=[True], name='renderosd')
			self.threads.update({thread.name: thread})
			thread.start()
		if delay > 0:
			thread = threading.Timer(delay, self.hideosd)
			thread.name = 'hideosd'
			self.threads.update({thread.name: thread})
			thread.start()
	def hideosd(self, wait = False):
		if self.bmovl == None and wait == True:
			while self.bmovl == None: pass
		elif self.bmovl == None and wait == False:
			return
		if not self.osd_visible == False:
			self.osd_visible = False
			try:
				os.write(self.bmovl, 'HIDE\n')
			except OSError: pass
		self.osdtype = 'time'
		if self.threads.keys().__contains__('hideosd'):
			self.threads['hideosd'].cancel()
	def updateosd(self, wait = False):
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
		if self.bmovl == None and wait == False:
			return
		elif self.bmovl == None and wait == True:
			while self.bmovl == None: pass
		width, height = self.video_resolution
		more = self.font.render('...', 1, (255,255,255,255))
		if not self.osd:
			self.osd_rect = pygame.rect.Rect((240,22*3,width-240-15,15))
			self.osd = pygame.surface.Surface(self.osd_rect[0:2], pygame.SRCALPHA)
			self.osd.fill((25,25,25,157))
			title = self.font.render(os.path.basename(self.filename).rpartition('.')[0], 1, (255,255,255,255))
			if title.get_width() > self.osd.get_width():
				self.osd.blit(title.subsurface((0,0,self.osd.get_width()-more.get_width(),title.get_height())), (0,0))
				self.osd.blit(more, (self.osd.get_width()-more.get_width(), title.get_height()-more.get_height()))
			else:
				self.osd.blit(title, (0,0))
			self.updateosd()
		curtime = self.font.render(time.strftime('%I:%M %p '), 1, (255,255,255,255))
		if self.osdtype == 'time' and (not self.osd_time_pos == int(self.get_time()) or not int(self.percent_pos) == self.osd_percentage):
			subosd = self.osd.subsurface([0,22,240,44])
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
			perc = pygame.surface.Surface((subosd.get_width()/100*self.percent_pos, 22), pygame.SRCALPHA)
			perc.fill((127,127,127,255))
			subosd.blit(perc, (0,pos.get_height()))
			percnum = self.font.render(str(int(self.percent_pos))+'%', 1, (255,255,255,255))
			subosd.blit(percnum, ((subosd.get_width()/2)-(percnum.get_width()-2),pos.get_height()))
			self.osd_percentage = int(self.percent_pos)
			self.osd_time_pos = int(self.time_pos)
			self.updateosd()
			self.osd_last_run == int(time.time())
		elif self.osdtype == 'volume' and not int(self.volume) == self.osd_percentage:
			subosd = self.osd.subsurface([0,22,240,44])
			subosd.fill((25,25,25,157))
			voltext = self.font.render('%s%% volume' % self.volume, 1, (255,255,255,255))
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
			subosd.blit(percnum, ((subosd.get_width()/2)-(percnum.get_width()-2),voltext.get_height()))
			self.osd_percentage = int(self.volume)
			self.updateosd()
			self.osd_last_run == int(time.time())
		elif not self.osd_last_run == int(time.time()):
			subosd = self.osd.subsurface([self.osd.get_width()-curtime.get_width(),22,curtime.get_width(),22])
			subosd.fill((25,25,25,157))
			subosd.blit(curtime, (0,0))
			self.osd_last_run == int(time.time())
		screen.blit(self.osd, self.osd.get_rect(center=screen.get_rect().center))
		pygame.display.update()
		if self.osd_visible == True:
			thread = threading.Thread(target=self.renderosd, name='renderosd')
			self.threads.update({thread.name: thread})
			thread.start()
	def poll(self):
		status = self.mplayer.poll()
		if status != None:
			self.stop()
		return status
	def stop(self):
		if self.osd_visible:
			self.hideosd()
		try:
			self.mplayer.stdin.write('quit\n')
			self.mplayer.stdin.close()
		except:
			try: self.mplayer.kill()
			except OSError: pass
		try:
			os.close(self.bmovl)
			os.unlink('/tmp/bmovl-%s-%s' % (os.geteuid(), os.getpid()))
		except: pass
		if self.mplayer.poll() != None:
			response = self.mplayer.wait()
		else:
			response = self.mplayer.poll()
		screen.blit(self.screenbkup, (0,0))
		pygame.display.update()
		return response
	def loop(self):
		while self.poll() == None:
			try: events = pygame.event.get()
			except KeyboardInterrupt: event = userquit()
			for event in events:
				if event.type == pygame.QUIT:
					running = False
					try: self.stop()
					except: break
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					self.stop()
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
					self.pause()
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
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
					if self.osd_visible:
						self.hideosd()
					else:
						self.showosd(5, osdtype='time')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
					self.mplayer.stdin.write('step_property fullscreen\n')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
					self.mplayer.stdin.write('step_property sub_visibility\n')
					self.mplayer.stdin.write('get_property sub_visibility\n')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
					save_pos = self.get_time()-10
					save_hrs = int(save_pos/60.0/60.0)
					save_mins = int((save_pos-(save_hrs*60*60))/60)
					save_secs = int(save_pos-((save_hrs*60*60)+(save_mins*60)))
					open('./'+os.path.dirname(self.filename)+'/.'+os.path.basename(self.filename)+os.uname()[1]+'.save', 'w').write('%s;%s\n# This line and everything below is ignored, it is only here so that you don\'t need to understand ^ that syntax.\nTime: %02d:%02d:%02d\nVolume: %d%%\n' % (save_pos, self.volume, save_hrs, save_mins, save_secs, self.volume))
					self.mplayer.stdin.write('osd_show_text "Saved position: %02d:%02d:%02d"\n' % (save_hrs, save_mins, save_secs))
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_9:
					self.showosd(5, osdtype='volume')
					self.set_volume('-0.02')
				elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
					self.showosd(5, osdtype='volume')
					self.set_volume('+0.02')
		self.stop()
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
	if sys.argv[1] == '--windowed' or sys.argv[1] == '-w':
		screen = pygame.display.set_mode((800,600)) # Create a new window.
	else:
		screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
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
	player = movieplayer(sys.argv[1])
	mplayer = player.play()
	player.loop()
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
	elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
		pygame.display.toggle_fullscreen()
	else:
		pass

