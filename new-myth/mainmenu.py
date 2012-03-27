#!/usr/bin/python

screenupdates = []
clickables = {}
running = True
selected = None
realmenuitems = []

import pygame
try:
	import android
	android.init()
	android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
except ImportError: android = None

#pygame.init() # I'm supposed to do this to initialise *all* of pygame, but I'd rather just initialise the bits I'll actually use.
pygame.font.init()
#pygame.image.init()
pygame.display.init()
#pygame.transform.init()

screen = pygame.display.set_mode((640,480))
try: background = pygame.transform.scale(pygame.image.load('Retro/ui/background.png'), screen.get_size()).convert() # Might want to use a different background.
except:
	background = pygame.Surface(screen.get_size()).convert()
	background.fill((0,0,255))
screen.blit(background, (0,0))
pygame.display.update()

# This should be done better, possibly pack a font with the program?
## Pygame on Android doesn't seem to have a "default" font, and since I would rather use the system fonts whereever possible I have told this to first check if there is a system font before using a biult-in Android one
if android:
	font = pygame.font.Font('/system/fonts/DroidSans.ttf', 36)
else:
	font = pygame.font.Font(pygame.font.match_font(u'trebuchetms'), 36) # Might want to use a different font.

def quit():
	global running
	running = False
	print 'User quit... Bye.'
	pygame.quit()

menuitems = [('Videos', "Videos menu has not been coded yet."), ('Extra item', 'testing'), ('Quit', quit)]

itemheight = screen.get_height()/len(menuitems)

itemnum = -1
for item in menuitems:
	itemnum += 1
	text = font.render(item[0], 1, (255,255,255))
	textpos = text.get_rect(centerx=screen.get_width()/2,centery=(itemheight*itemnum)+(itemheight/2))
	clickables.update({tuple(textpos[0:4]): itemnum})#(text, item[1])})
	realmenuitems.append((text, item[1], textpos))
	screen.blit(text, textpos)
	screenupdates.append(textpos)

pygame.display.update(screenupdates)
screenupdates = []

pygame.event.set_allowed(None)
pygame.event.set_allowed([pygame.QUIT,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.KEYDOWN,pygame.KEYUP,pygame.MOUSEMOTION])
while running == True:
	event = pygame.event.wait()
	if event.type == pygame.QUIT:
		running = 0
		pygame.quit()
	elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
		released = False
		button = pygame.Rect(event.pos[0],event.pos[1],0,0).collidedict(clickables)
		if button:
			while released != True:
				event = pygame.event.wait()
				if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
					released = True
					if pygame.Rect(event.pos[0],event.pos[1],0,0).colliderect(button[0]):
						if type(realmenuitems[button[1]][1]) == str:
							print realmenuitems[button[1]][1]
						else:
							realmenuitems[button[1]][1]()
					else:
						print 'User changed their mind and released the button elsewhere.'
	elif event.type == pygame.MOUSEMOTION:
		mouserect = pygame.Rect(event.pos[0],event.pos[1],0,0)
		button = mouserect.collidedict(clickables)
		if button and realmenuitems[button[1]] != selected:
			if selected:
				screen.blit(background, (0,0))
				screen.blit(selected[0], selected[2])
				screenupdates.append(selected[2])
			selected = realmenuitems[button[1]]
			s = pygame.Surface(selected[2][2:4], pygame.SRCALPHA)
			s.fill((0,0,0,50))
			s.blit(selected[0], (0,0))
			screen.blit(s, selected[2])
			screenupdates.append(selected[2])
			pygame.display.update(screenupdates)
			screenupdates = []
		elif not button and selected != None:
			screen.blit(background, (0,0))
			screen.blit(selected[0], selected[2])
			screenupdates.append(selected[2])
			pygame.display.update(screenupdates)
			screenupdates = []
			selected = None
	elif event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_DOWN):
		if not selected:
			if event.key == pygame.K_UP:
				selected = realmenuitems[-1]
			elif event.key == pygame.K_DOWN:
				selected = realmenuitems[0]
		else:
			screen.blit(background, (0,0))
			screen.blit(selected[0], selected[2])
			screenupdates.append(selected[2])
			itemnum = realmenuitems.index(selected)
			if event.key == pygame.K_UP:
				try: selected = realmenuitems[itemnum-1]
				except IndexError: selected = realmenuitems[-1]
			elif event.key == pygame.K_DOWN:
				try: selected = realmenuitems[itemnum+1]
				except IndexError: selected = realmenuitems[0]
		s = pygame.Surface(selected[2][2:4], pygame.SRCALPHA)
		s.fill((0,0,0,50))
		s.blit(selected[0], (0,0))
		screen.blit(s, selected[2])
		screenupdates.append(selected[2])
		pygame.display.update(screenupdates)
		screenupdates = []
	elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and selected:
		if type(selected[1]) == str:
			print selected[1]
		elif selected[1]:
			selected[1]()
	elif event.type == pygame.KEYUP:
		if event.key == pygame.K_ESCAPE:
			quit()
		pass
	else:
		print event
