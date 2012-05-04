#!/usr/bin/python
import os
import sys
import pygame
import socket
import threading
try: # I would like this to run on Android as well, this section is needed for that to work.
	import android
	android.init() # Usually this and the next line would be put into an if statement after this, I didn't see the point and put it here instead.
	android.map_key(4, pygame.K_ESCAPE)
	print android.KEYCODE_BACK, pygame.K_ESCAPE
except ImportError: android = None
except AttributeError: # I have a module on my desktop called "android" I suspect this is part of the SDK and meant for testing, I dont really care at the moment.
	del android
	android = None

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
	screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # Create a new window.
else:
	if len(sys.argv) >= 3 and (sys.argv[1] == '--windowed' or sys.argv[1] == '-w'):
		screen = pygame.display.set_mode((int(sys.argv[2].split('x')[0]),int(sys.argv[2].split('x')[1]))) # Create a new window.
		if len(sys.argv) >= 4:
			hostname = sys.argv[3]
			if len(sys.argv) >= 5:
				portnum = sys.argv[4]
			else:
				portnum = 6546
		else:
			hostname = "localhost"
			portnum = 6546
	else:
		if len(sys.argv) >= 2:
			hostname = sys.argv[1]
			if len(sys.argv) >= 3:
				portnum = int(sys.argv[2])
			else:
				portnum = 6546
		else:
			hostname = "localhost"
			portnum = 6546
		screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)#|pygame.NOFRAME)
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

server = socket.socket()
server.connect((hostname, portnum))
server.send("Unnamed Python Media Center network control client "+os.uname()[1]+"\n")
server.send("---------------------------------------------------"+'-'*len(os.uname()[1])+"\n")

def recievehandler(server):
	serverfile = server.makefile('r')
	while not serverfile.closed:
		data = serverfile.readline()
		if data == '':
			pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
			serverfile.close()
		else:
			sys.stdout.write(data)

recvthread = threading.Thread(target=recievehandler, args=[server], name='recievehandler')
recvthread.setDaemon(True)
recvthread.start()

stdbutton = pygame.Surface((screen.get_width()/3,screen.get_height()/3), pygame.SRCALPHA)
stdbutton.fill((0,0,0,100), stdbutton.get_rect(width=stdbutton.get_width()-5, height=stdbutton.get_height()-5))
font = pygame.font.Font(fontname, 36)
keys = {(0, 0, stdbutton.get_width(), stdbutton.get_height()): 'escape', (screen.get_width()/3, 0, stdbutton.get_width(), stdbutton.get_height()): 'up', (screen.get_width()/3, (screen.get_height()/3)*2, stdbutton.get_width(), stdbutton.get_height()): 'down', (0, screen.get_height()/3, stdbutton.get_width(), stdbutton.get_height()): 'left', ((screen.get_width()/3)*2, screen.get_height()/3, stdbutton.get_width(), stdbutton.get_height()): 'right', (screen.get_width()/3, screen.get_height()/3, stdbutton.get_width(), stdbutton.get_height()): 'return', (0, (screen.get_height()/3)*2, stdbutton.get_width(), stdbutton.get_height()): 'space', ((screen.get_width()/3)*2, (screen.get_height()/3)*2, stdbutton.get_width(), stdbutton.get_height()): 'kp_enter'}
for keyloc in keys.keys():
	screen.blit(stdbutton, keyloc)
	screen.blit(font.render(keys[keyloc], 1, (255,255,255)), keyloc)

pygame.display.update()

## These should avoid going through the loop unnecessarily (and wasting resources) when there is events that I'm not going to use anyway.
pygame.event.set_allowed(None) # This says to not put *any* events into the event queue.
pygame.event.set_allowed([pygame.QUIT])
pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN,pygame.KEYDOWN]) # This says to put the events I want to see into the event queue, this needs to be updated anytime I want to monitor more events.

running = True
preselected = None
while running == True:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			running = False
			pygame.quit()
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			item = pygame.Rect(event.pos[0],event.pos[1],0,0).collidedict(keys)
			if not preselected == None:
				screen.blit(preselected[0], preselected[1])
			if not item == None:
				preselected = (screen.subsurface(item[0]).copy(), item[0])
				server.send("key "+item[1]+"\n")
				screen.blit(stdbutton, item[0])
			else:
				preselected = None
			pygame.display.update()
		elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
		elif event.type == pygame.KEYDOWN:
			server.send("key "+str(event.key)+"\n")
