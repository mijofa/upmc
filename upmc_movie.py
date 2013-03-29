import vlc
import pygame
#MovieType = pygame.movie.MovieType

VLC_NAVIGATE_ENTER = 0
VLC_NAVIGATE_UP = 1
VLC_NAVIGATE_DOWN = 2
VLC_NAVIGATE_LEFT = 3
VLC_NAVIGATE_RIGHT = 4


class Movie():
  def end_callback(self, vlcEvent, pygameEvent):
    pygame.event.post(pygame.event.Event(pygameEvent, {'userevent': "movie end reached" ,'vlcEvent': vlcEvent}))
  def __init__(self, filename):
    """
    In [13]: i=vlc.Instance()

    In [14]: p=i.media_player_new()

    In [15]: m=i.media_new('/home/mike/Videos/Video/Test AC3 v2.0.avi')

    In [16]: p.set_media(m)

    In [17]: p.play()
    Out[17]: 0

    In [18]: p.stop()
    """
    self.vlc_instance = vlc.Instance("--no-video-title --no-keyboard-events")
    self.vlc_player = self.vlc_instance.media_player_new()
    self.vlc_player.video_set_key_input(0)
    self.event_manager = self.vlc_player.event_manager()
    self.skipTo = -1
    self.vlc_media = self.vlc_instance.media_new(filename)
    self.vlc_player.set_media(self.vlc_media)
  def play(self, loops = 0):
    self.vlc_player.play()
    self.vlc_player.video_set_spu(1)
    if self.skipTo > 0:
      self.vlc_player.set_time(self.skipTo)
  def stop(self):
    self.vlc_player.stop()
    self.vlc_instance.release()
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
  def render_frame(self, frame_number):
    # I could probably do this in some really hacky way by taking a screenshot then rendering that with PyGame. Not useful enough to matter.
    ## Can't figure out how to grab a specific frame anyway.
    return None
  def get_frame(self):
    return .001 * self.vlc_player.get_time() * self.vlc_player.get_fps()
  def get_time(self):
    return .001 * self.vlc_player.get_time()
  def get_busy(self):
    return self.vlc_player.get_state() == vlc.State.Playing
  def get_length(self):
    return .001 * self.vlc_player.get_length()
  def get_size(self):
    return (self.vlc_player.video_get_width(),self.vlc_player.video_get_height())
  def has_video(self):
    # Useless for now, can't be bothered finding a VLC equivalent binding
    ## Looks like I can't get this info until after I've started the movie playing, making it even less useful
    return True
  def has_audio(self):
    # Useless for now, can't be bothered finding a VLC equivalent binding
    return True
  def set_volume(self, newVolume):
    self.vlc_player.audio_set_volume(int(newVolume*100.0))
  def set_display(self, Surface, rect = None):
    # I'm not sure I can actually do this properly. Not useful enough for it's difficulty.
    ## I can't even find a way to tell VLC not to render at all, so I can't do what pygame does when Surface = None
    # I'm just going to make this set the X window VLC displays to, if the Surface value is an int then use it as the windowid if it's a surface then grab the pygame.display windowid
    if type(Surface) == int:
      x_window_id = Surface
    elif type(Surface) == pygame.surface.SurfaceType:
      x_window_id = pygame.display.get_wm_info()['window']
    self.vlc_player.set_xwindow(x_window_id)
    return None
  def set_endevent(self, eventType = None):
    print "SETTING ENDEVENT", eventType
    if not eventType == None:
      self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.end_callback, eventType)
    else:
      self.event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
  def get_endevent(self):
    return self.event_manager._callbacks.values()[0][1][0]
  def dvd_navigate(self, key):
    if self.vlc_player.get_title() != 0 or self.vlc_player.get_title_count() == 0:
      return False
    else:
      if key == pygame.K_RETURN:
        key = VLC_NAVIGATE_ENTER
      elif key == pygame.K_UP:
        key = VLC_NAVIGATE_UP
      elif key == pygame.K_DOWN:
        key = VLC_NAVIGATE_DOWN
      elif key == pygame.K_LEFT:
        key = VLC_NAVIGATE_LEFT
      elif key == pygame.K_RIGHT:
        key = VLC_NAVIGATE_RIGHT = 4
      print self.vlc_player.navigate(key)
      return True
