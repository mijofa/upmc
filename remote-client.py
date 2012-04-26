import pygame

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
	if len(sys.argv) > 1 and (sys.argv[1] == '--windowed' or sys.argv[1] == '-w'):
		screen = pygame.display.set_mode((int(sys.argv[2].split('x')[0]),int(sys.argv[2].split('x')[1]))) # Create a new window.
	else:
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


