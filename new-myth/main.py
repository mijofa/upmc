#!/usr/bin/python
from time import sleep
import os
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
	android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
except ImportError: android = None
except AttributeError: # I have a module on my desktop called "android" I suspect this is part of the SDK and meant for testing, I dont really care at the moment.
	del android
	android = None

global screenupdates
screenupdates = []
global running
running = True
rootdir = os.getcwd()

def userquit():
	pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
	return pygame.event.Event(pygame.QUIT, {})

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

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
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
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
                    if font.size(word)[0] >= rect.width:
                        wrappedword = word[0]
                        for character in word:
                            print character
                            for character in word[1:]:
                                test_word = wrappedword + character
                                if font.size(wrappedword)[0] < rect.width:
                                    wrappedword = test_word
                                else:
                                    final_lines.append(wrappedword)
                                    wrappedword = ""
                        print ' '
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
    for line in final_lines: 
#        if accumulated_height + font.size(line)[1] >= rect.height:
#            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
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
				text = font.render(item[0], 1, (255,255,255))
#				textpos = text.get_rect(centerx=screen.get_width()/2,centery=(itemheight*itemnum)+(itemheight/2))
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
			surf = pygame.Surface(self.selected[2][2:4], pygame.SRCALPHA)
			surf.fill((0,0,0,50))
			surf.blit(self.selected[0], (0,0))
			screen.blit(surf, self.selected[2])
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
		surf = pygame.Surface(self.selected[2][2:4], pygame.SRCALPHA)
		surf.fill((0,0,0,50))
		surf.blit(self.selected[0], (0,0))
		screen.blit(surf, self.selected[2])
		screenupdates.append(self.selected[2])
		pygame.display.update(screenupdates)
		screenupdates = []
	def action(self, args = None):
		# This will action the highlighted item.
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
		self.builditems()
		self.render()
		self.loop()
	def find(self, directory = cwd, filetype = ''):
		dirs = []
		files = []
		if filetype == '' or filetype == 'all':
			for f in os.listdir(directory):
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
				if os.path.isdir(f):
					dirs.append(f + '/')
			dirs.sort()
			return dirs
		elif filetype == 'file' or filetype == 'f':
			for f in os.listdir(directory):
				if not os.path.isdir(f):
					files.append(f)
			files.sort()
			return files
		elif filetype.__contains__('/'):
			out = []
			for f in os.listdir(directory):
				if not os.path.isdir(directory+'/'+f):
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
				if not os.path.isdir(directory+'/'+f):
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
		self.itemsinfo = {}
		self.items = []
		if os.getcwd() != rootdir:
			self.items.append('../')
			self.itemsinfo['../'] = {}
			self.itemsinfo['../']['file'] = False
			self.itemsinfo['../']['title'] = '../'
			self.itemsinfo['../']['itemnum'] = 0
			self.itemsinfo['../']['filename'] = '../'
#		dirs, files = self.find(filetype='all')
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
		screenheight = screen.get_height()
		screenwidth = screen.get_width()
		itemheight = 190 #280 = 5 on 1050 vertical resolution
		itemwidth = 120 #210 = 6 on 1680 horizontal resolution
		numcols = screenwidth/itemwidth
		numrows = screenheight/itemheight
		self.pagerows = []
		rowspace = (screenheight-(numrows*itemheight))/numrows
		colspace = (screenwidth-(numcols*itemwidth))/numcols
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
#								thumb = font.render(self.itemsinfo[item]['title'], 1, (255,255,255))
								rect = pygame.Rect((0,0,itemwidth,itemheight))
#								surf = pygame.Surface((itemwidth,itemheight), pygame.SRCALPHA)
#								surf.fill((0,0,0,50))
#								thumb = drawText(surf, self.itemsinfo[item]['title'], (255,255,255), rect, font)
								surf = render_textrect(self.itemsinfo[item]['title'], font, rect, (255,255,255), (0,0,0,50))
#								thumb = pygame.transform.smoothscale(thumb.convert_alpha(), (rect[2], rect[3]))
#								print thumb
								surf.blit(surf, ((itemwidth-rect[2])/2, (itemheight-rect[3])/2))
							self.itemsinfo[item]['surface'] = surf
						top = (rownum*itemheight)+(rownum*rowspace)+(rowspace/2)
						left = (colnum*itemwidth)+(colnum*colspace)+(colspace/2)
						self.itemsinfo[item]['buttonloc'] = self.itemsinfo[item]['surface'].get_rect(top=top, left=left)
						self.clickables.update({tuple(self.itemsinfo[item]['buttonloc'][0:4]): item})
						col = item
						screen.blit(self.itemsinfo[item]['surface'], self.itemsinfo[item]['buttonloc'])
						pygame.display.update(self.itemsinfo[item]['buttonloc'])
						row.append(col)
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
				screen.blit(background, (0,0))
				screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
				screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
			self.selected = [None, item]
			butbg = pygame.Surface(self.itemsinfo[item]['buttonloc'][2:4], pygame.SRCALPHA)
			butbg.fill((0,0,0,50))
			surf = pygame.Surface(self.itemsinfo[item]['buttonloc'][2:4], pygame.SRCALPHA)
			surf.blit(self.itemsinfo[item]['surface'], (0,0))
			surf.blit(butbg, (0,0))
			screen.blit(surf, self.itemsinfo[item]['buttonloc'])
			screenupdates.append(self.itemsinfo[item]['buttonloc'])
			pygame.display.update(screenupdates)
			screenupdates = []
			return self.selected[1]
		elif item == self.selected[1]:
			return self.selected[1]
	def keyselect(self, direction):
		global screenupdates
		if self.selected[1]:
			screen.blit(background, (0,0))
			screen.blit(self.itemsinfo[self.selected[1]]['surface'], self.itemsinfo[self.selected[1]]['buttonloc'])
			screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
		if not self.selected[0] or not self.selected[1]:
			if direction == 0:
				self.selected = [self.pagerows[-1], self.pagerows[-1][0]]
			elif direction == 1:
				self.selected = [self.pagerows[0], self.pagerows[0][0]]
			elif direction == 2:
				self.selected = [self.pagerows[-1], self.pagerows[-1][-1]]
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
					except ValueError: self.selected[0] = self.pagerows[0]
				try: self.selected[1] = self.selected[0][colnum]
				except IndexError: self.selected[1] = self.selected[0][-1]
			elif direction == 2:
				if self.selected[0].index(self.selected[1]) == 0:
					if self.pagerows.index(self.selected[0]) == 0:
						self.scroll(0,1)
						try: self.selected[0] = self.pagerows[self.pagerows.index(self.selected[0])-1]
						except ValueError: self.selected[0] = self.pagerows[-1]
						self.selected[1] = self.selected[0][-1]
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
						except ValueError: self.selected[0] = self.pagerows[0]
					self.selected[1] = self.selected[0][0]
		butbg = pygame.Surface(self.itemsinfo[self.selected[1]]['buttonloc'][2:4], pygame.SRCALPHA)
		butbg.fill((0,0,0,50))
		surf = pygame.Surface(self.itemsinfo[self.selected[1]]['buttonloc'][2:4], pygame.SRCALPHA)
		surf.blit(self.itemsinfo[self.selected[1]]['surface'], (0,0))
		surf.blit(butbg, (0,0))
		screen.blit(surf, self.itemsinfo[self.selected[1]]['buttonloc'])
		screenupdates.append(self.itemsinfo[self.selected[1]]['buttonloc'])
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
				item = self.mouseselect(event.pos)
				if item:
					while released != True:
						event = pygame.event.wait()
						if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
							released = True
							if self.mouseselect(event.pos) == item:
								self.action(self.selected[1])
			elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
				self.scroll(event.button==5, 1)
	def action(self, selected):
		if selected == '../' and not self.itemsinfo.has_key(selected):
			return pygame.QUIT
		elif self.itemsinfo[selected]['file']:
			extprogram = subprocess.Popen(['file',self.itemsinfo[selected]['filename']])
			extprogram.wait()
		elif not self.itemsinfo[selected]['file']:
			os.chdir(self.itemsinfo[selected]['filename'])
			self.selected = [None, None]
			self.builditems()
			self.render()
##### End class filemenu()

## The Pygame modules need to be initialised before they can be used.
### The Pygame docs say to just initialise *everything* at once, I think this is wasteful and am only initialising the bits I'm using.
#pygame.init()
pygame.font.init()
#pygame.image.init() # Doesn't have an '.init()' funtion.
pygame.display.init()
#pygame.transform.init() # Doesn't have an '.init()' funtion.
#pygame.event.init() # Doesn't have an '.init()' funtion.

#screen = pygame.display.set_mode((640,480)) # Create a new window.
screen = pygame.display.set_mode((800,600)) # Create a new window.
try: background = pygame.transform.scale(pygame.image.load('background.png'), screen.get_size()).convert() # Resize the background image to fill the window.
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

menuitems = [('Videos', filemenu), ('Extra item', 'testing'), ('Quit', userquit)] # Update this with extra menu items, this should be a list containing one tuple per item, the tuple should contain the menu text and the function that is to be run when that option gets selected.
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

