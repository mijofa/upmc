#!/usr/bin/python
import pygame
try: # I would like this to run on Android as well, this section is needed for that to work.
	import android
	android.init() # Usually this and the next line would be put into an if statement after this, I didn't see the point and put it here instead.
	android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
except ImportError: android = None

def quit():
	global running
	running = False
	print 'User quit... Bye.'
	pygame.quit()

## The Pygame modules need to be initialised before they can be used.
### The Pygame docs say to just initialise *everything* at once, I thing this is wasteful and am only initialising the bits I'm using.
#pygame.init()
pygame.font.init()
#pygame.image.init() # Doesn't have an '.init()' funtion.
pygame.display.init()
#pygame.transform.init() # Doesn't have an '.init()' funtion.
#pygame.event.init() # Doesn't have an '.init()' funtion.

global screenupdates
screenupdates = []
global running
running = True

screen = pygame.display.set_mode((640,480)) # Create a new window.
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

class textmenu():
	menuitems = [('Videos', "Videos menu has not been coded yet."), ('Extra item', 'testing'), ('Quit', quit)]
	clickables = {}
	realmenuitems = []
	def __init__(self):
		itemheight = screen.get_height()/len(menuitems)
		itemnum = 0
		for item in self.menuitems:
			itemnum += 1
			text = font.render(item[0], 1, (255,255,255))
			textpos = text.get_rect(centerx=screen.get_width()/2,centery=(itemheight*itemnum)+(itemheight/2))
			self.clickables.update({tuple(textpos[0:4]): itemnum})#(text, item[1])})
			self.realmenuitems.append((text, item[1], textpos))
			screen.blit(text, textpos)
			screenupdates.append(textpos)
		pygame.display.update(screenupdates)
		screenupdates = []
		pygame.event.set_allowed([pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.KEYDOWN,pygame.KEYUP])
	
