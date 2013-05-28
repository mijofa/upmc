import vlc
import pygame.display, pygame.event
#import pygame
#MovieType = pygame.movie.MovieType

# player.get_meta(vlc.Meta.Title)

NAVIGATE_ENTER = 0
NAVIGATE_UP = 1
NAVIGATE_DOWN = 2
NAVIGATE_LEFT = 3
NAVIGATE_RIGHT = 4

class Movie():
  def end_callback(self, vlcEvent, pygameEvent):
    pygame.event.post(pygame.event.Event(pygameEvent, {'userevent': "movie end reached" ,'vlcEvent': vlcEvent}))
  def __init__(self, filename):
    self.skipTo = -1
    self.vlc_instance = vlc.Instance("--no-video-title --no-keyboard-events")
    self.vlc_player = self.vlc_instance.media_player_new()
    self.vlc_player_em = self.vlc_player.event_manager()
    self.vlc_player.video_set_key_input(0)
    self.vlc_media = self.vlc_instance.media_new(filename)
    self.vlc_meda_em = self.vlc_media.event_manager()
    self.vlc_player.set_media(self.vlc_media)
  def set_xwindow(self, windowid):
    # windowid = pygame.display.get_wm_info()['window']
    if type(windowid) == int:
      self.vlc_player.set_xwindow(windowid)
    else:
      raise TypeError("windowid must be an int.")
  def play(self, loops = 0):
    self.vlc_player.play()
    self.vlc_player.video_set_spu(1)
    if self.skipTo > 0:
      self.vlc_player.set_time(self.skipTo)
  def stop(self):
    self.vlc_player.stop()
  def pause(self):
    self.vlc_player.pause()
  def skip(self, seconds):
    milliseconds = seconds * 1000L # VLC works with milliseconds, PyGame works with seconds
    if self.vlc_player.get_time() == -1L:
      self.skipTo = milliseconds
    else:
      self.vlc_player.set_time(self.vlc_player.get_time()+milliseconds)
  def rewind(self):
    self.skipTo = 0
    self.vlc_player.set_time(0)
    self.vlc_player.play()
  def get_time(self):
    return .001 * self.vlc_player.get_time()
  def get_busy(self):
    return self.vlc_player.get_state() == vlc.State.Playing
  def get_length(self):
    return .001 * self.vlc_player.get_length()
  def set_volume(self, newVolume):
    self.vlc_player.audio_set_volume(int(newVolume*100.0))
  def set_end_callback(self, callback = None, args = None):
    if callback == None:
      self.vlc_player_em.event_detach(vlc.EventType.MediaPlayerEndReached)
    elif args == None:
      self.vlc_player_em.event_attach(vlc.EventType.MediaPlayerEndReached, callback)
    else:
      self.vlc_player_em.event_attach(vlc.EventType.MediaPlayerEndReached, callback, args)
  def get_end_callback(self):
    return self.vlc_player_em._callbacks.values()[0][1][0]
  def dvd_navigate(self, key):
    if self.vlc_player.get_title() != 0 or self.vlc_player.get_title_count() <= 1:
      return False
    else:
      if type(key) != type(NAVIGATE_ENTER):
        if key in [NAVIGATE_ENTER, NAVIGATE_UP, NAVIGATE_DOWN, NAVIGATE_LEFT, NAVIGATE_RIGHT]
          self.vlc_player.navigate(key)
          return True
        else:
          raise ValueError("Key must be one of NAVIGATE_{ENTER,UP,DOWN,LEFT,RIGHT}")
      else:
        raise TypeError("Key must be one of NAVIGATE_{ENTER,UP,DOWN,LEFT,RIGHT}")

