import vlc
class pygame:
  class display:
    from pygame.display import get_wm_info
  class surface:
    from pygame.surface import SurfaceType

class movie:
  class Movie():
    def __init__(self, filename):
      self.skipTo = -1
      self.vlcInstance = vlc.Instance()
      self.media = self.vlcInstance.media_new(filename)
      self.player = self.vlcInstance.media_player_new()
      self.player.set_media(self.media)
    def play(self, loops = 0):
      self.player.play()
      if self.skipTo > 0:
        self.player.set_time(self.skipTo)
    def stop(self):
      self.player.stop()
    def pause(self):
      self.player.pause()
    def skip(self, seconds):
      milliseconds = seconds * 1000.0 # VLC works with milliseconds, PyGame works with seconds
      if self.player.get_time() == -1L:
        self.skipTo = milliseconds
      else:
        self.player.set_time(self.player.get_time()+milliseconds)
    def rewind(self):
      self.skipTo = 0
      self.player.set_time(0)
      self.player.play()
    def render_frame(self, frame_number):
      # I could probably do this in some really hacky way by taking a screenshot then rendering that with PyGame. Not useful enough to matter.
      ## Can't figure out how to grab a specific frame anyway.
      return None
    def get_frame(self):
      return .001 * self.player.get_time() * self.player.get_fps()
    def get_time(self):
      return .001 * self.player.get_time()
    def get_busy(self):
      return self.player.get_state() == vlc.State.Playing
    def get_length(self):
      return .001 * self.player.get_length()
    def get_size(self):
      return (self.player.video_get_width(),self.player.video_get_height())
    def has_video(self):
      # Useless for now, can't be bothered finding a VLC equivalent binding
      ## Looks like I can't get this info until after I've started the movie playing, making it even less useful
      return True
    def has_audio(self):
      # Useless for now, can't be bothered finding a VLC equivalent binding
      return True
    def set_volume(self, newVolume):
      self.player.audio_set_volume(newVolume*100.0)
    def set_display(self, Surface, rect = None):
      # I'm not sure I can actually do this properly. Not useful enough for it's difficulty.
      ## I can't even find a way to tell VLC not to render at all, so I can't do what pygame does when Surface = None
      # I'm just going to make this set the X window VLC displays to, if the Surface value is an int then use it as the windowid if it's a surface then grab the pygame.display windowid
      if type(Surface) == int:
        XWindowID = Surface
      elif type(Surface) == pygame.surface.SurfaceType:
        XWindowID = pygame.display.get_wm_info()['window']
      self.player.set_xwindow(XWindowID)
      return None
