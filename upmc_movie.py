import vlc
from pygame.movie import MovieType
import pygame

vlc_instance = vlc.Instance("--no-video-title --no-keyboard-events")
vlc_player = vlc_instance.media_player_new()
vlc_player.video_set_key_input(0)
event_manager = vlc_player.event_manager()

class Movie():
  def end_callback(self, vlcEvent, pygameEvent):
    pygame.event.post(pygame.event.Event(pygameEvent, {'userevent': "movie end reached" ,'vlcEvent': vlcEvent}))
  def __init__(self, filename):
    self.skipTo = -1
    self.vlc_media = vlc_instance.media_new(filename)
    vlc_player.set_media(self.vlc_media)
  def play(self, loops = 0):
    vlc_player.play()
    if self.skipTo > 0:
      vlc_player.set_time(self.skipTo)
  def stop(self):
    vlc_player.stop()
  def pause(self):
    vlc_player.pause()
  def skip(self, seconds):
    milliseconds = seconds * 1000L # VLC works with milliseconds, PyGame works with seconds
    if vlc_player.get_time() == -1L:
      self.skipTo = milliseconds
    else:
      vlc_player.set_time(vlc_player.get_time()+milliseconds)
  def rewind(self):
    self.skipTo = 0
    vlc_player.set_time(0)
    vlc_player.play()
  def render_frame(self, frame_number):
    # I could probably do this in some really hacky way by taking a screenshot then rendering that with PyGame. Not useful enough to matter.
    ## Can't figure out how to grab a specific frame anyway.
    return None
  def get_frame(self):
    return .001 * vlc_player.get_time() * vlc_player.get_fps()
  def get_time(self):
    return .001 * vlc_player.get_time()
  def get_busy(self):
    return vlc_player.get_state() == vlc.State.Playing
  def get_length(self):
    return .001 * vlc_player.get_length()
  def get_size(self):
    return (vlc_player.video_get_width(),vlc_player.video_get_height())
  def has_video(self):
    # Useless for now, can't be bothered finding a VLC equivalent binding
    ## Looks like I can't get this info until after I've started the movie playing, making it even less useful
    return True
  def has_audio(self):
    # Useless for now, can't be bothered finding a VLC equivalent binding
    return True
  def set_volume(self, newVolume):
    vlc_player.audio_set_volume(int(newVolume*100.0))
  def set_display(self, Surface, rect = None):
    # I'm not sure I can actually do this properly. Not useful enough for it's difficulty.
    ## I can't even find a way to tell VLC not to render at all, so I can't do what pygame does when Surface = None
    # I'm just going to make this set the X window VLC displays to, if the Surface value is an int then use it as the windowid if it's a surface then grab the pygame.display windowid
    if type(Surface) == int:
      x_window_id = Surface
    elif type(Surface) == pygame.surface.SurfaceType:
      x_window_id = pygame.display.get_wm_info()['window']
    vlc_player.set_xwindow(x_window_id)
    return None
  def set_endevent(self, eventType = None):
    print "SETTING ENDEVENT", eventType
    if not eventType == None:
      event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.end_callback, eventType)
    else:
      event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
  def get_endevent(self):
    return event_manager._callbacks.values()[0][1][0]
