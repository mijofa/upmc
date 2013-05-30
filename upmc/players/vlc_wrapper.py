import vlc
#import pygame
#MovieType = pygame.movie.MovieType

# player.get_meta(vlc.Meta.Title)

NAVIGATE_ENTER = 0
NAVIGATE_UP = 1
NAVIGATE_DOWN = 2
NAVIGATE_LEFT = 3
NAVIGATE_RIGHT = 4

class Movie():
  def __init__(self, filename):
    self.start_time = -1
    self.vlc_instance = vlc.Instance("--no-video-title --no-keyboard-events")
    self.vlc_player = self.vlc_instance.media_player_new()
    self.vlc_player_em = self.vlc_player.event_manager()
    self.vlc_player.video_set_key_input(0)
    self.vlc_media = self.vlc_instance.media_new(filename)
    self.vlc_media_em = self.vlc_media.event_manager()
    self.vlc_player.set_media(self.vlc_media)
  def set_xwindow(self, windowid):
    # windowid = pygame.display.get_wm_info()['window']
    if type(windowid) == int:
      self.vlc_player.set_xwindow(windowid)
    else:
      raise TypeError("windowid must be an int.")
  def play(self):
    self.vlc_player.play()
    self.vlc_player.video_set_spu(1)
    if self.start_time > 0: # VLC won't let me set the time before I start playing, this is a workaround. self.set_time sets this variable if the media stream is not running.
      self.vlc_player.set_time(self.start_time)
      self.start_time = 0
  def stop(self):
    self.vlc_player.stop()
  def get_pause(self):
    # Return pause state. True = paused. False = playing
    return self.vlc_player.get_state() == vlc.State.Paused
  def set_pause(self, value):
    # If value == True, pause. else value == False, unpause.
    # Returns current paused state.
    if type(value) != bool:
      raise TypeError("value must be a bool")
    if value != self.get_pause():
      return self.toggle_pause()
    return self.get_pause()
  def toggle_pause(self):
    # Toggles paused state.
    # Returns current paused state.
    self.vlc_player.pause()
    return self.get_pause()
  def get_volume(self):
    # Return current volume. 1.0 = 100% 0.5 = 50%
    ## FIXME
    raise NotImplementedError
  def set_volume(self, value):
    # Set volume to value.
    # Return current volume.
    self.vlc_player.audio_set_volume(int(value*100.0)) # Should I be treating 200% as max or 100% ?
    return self.get_volume()
  def increment_volume(self, value):
    # Increment volume by value.
    # Return current volume.
    return self.set_volume(self.get_volume()+value) # Should I be treating 200% as max or 100% ?
  def get_mute(self):
    # Return current mute state. True = muted, False = not
    ## FIXME
    raise NotImplementedError
  def set_mute(self, value):
    # If value == True, mute. else value == False, unmute.
    # Return current mute state
    ## FIXME
    raise NotImplementedError
    if type(value) != bool:
      raise TypeError("value must be a bool")
    return self.get_mute()
  def toggle_mute(self):
    # Toggles mute state.
    # Return current mute state.
    return self.set_mute(!self.get_mute())
  def get_audio_track(self):
    # Return current audio track. Don't know how to handle this, probably a tuple including track # and description.
    ## FIXME
    raise NotImplementedError
  def set_audio_track(self, value):
    # Set audio track to value.
    # Return audio track
    ## FIXME
    raise NotImplementedError
    return self.get_audio_track()
  def increment_audio_track(self, value):
    # Set audio track to current audio track + value.
    # Return audio track.
    return self.set_audio_track(self.get_audio_track()+value)
  def get_length(self):
    # Return length of media file in seconds.
    return .001 * self.vlc_player.get_length() # Convert milliseconds into seconds
  def get_time(self):
    # Return current time in seconds.
    return .001 * self.vlc_player.get_time() # Convert milliseconds into seconds
  def set_time(self, value):
    # Seek to value seconds.
    # Return current time in seconds.
    vlc_value = value * 1000L # VLC works with milliseconds, I prefer working with seconds.
    if self.vlc_player.get_time() == -1L:
      self.start_time = vlc_value # VLC won't let me set the time before I start playing, this is a workaround. self.play sets the start time to this variable if set.
    else:
      self.vlc_player.set_time(self.vlc_player.get_time()+vlc_value)
    return self.get_time()
  def increment_time(self, value):
    # Seek to current time+value seconds.
    # Return current time in seconds
    return self.set_time(self.get_time()+value)
  def get_subtitles_visibility(self):
    # Return subtitles visibility.
    ## FIXME
    raise NotImplementedError
  def set_subtitles_visibility(self, value):
    # Set subtitles visibility to value.
    # Return subtitles visibility.
    ## FIXME
    raise NotImplementedError
    if type(value) != bool:
      raise TypeError("value must be a bool")
    return self.get_subtitles_visibility()
  def toggle_subtitles_visibility(self):
    # Toggle subtitles visibility.
    # Return subtitles visibility.
    ## FIXME
    raise NotImplementedError
    return self.set_subtitles_visibility(!self.get_subtitles_visibility())
  def get_subtitles_track(self):
    # Return subtitles track
    ## FIXME
    raise NotImplementedError
  def set_subtitles_track(self, value):
    # Set subtitles track to value.
    # Return subtitles track
    ## FIXME
    raise NotImplementedError
    return self.get_subtitles_track()
  def increment_subtitles_track(self, value):
    # Set subtitles track to current subtitles track + value.
    # Return subtitles track.
    ## FIXME
    raise NotImplementedError
    return self.set_subtitles_track(self.get_subtitles_track()+value)

  def set_end_callback(self, callback = None, args = None):
    # The callback should probably do something like trigger a pygame event.
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
      return False # Should almost certainly raise an exception here instead.
    else:
      if type(key) != type(NAVIGATE_ENTER):
        if key in [NAVIGATE_ENTER, NAVIGATE_UP, NAVIGATE_DOWN, NAVIGATE_LEFT, NAVIGATE_RIGHT]:
          self.vlc_player.navigate(key)
          return True
        else:
          raise ValueError("Key must be one of NAVIGATE_{ENTER,UP,DOWN,LEFT,RIGHT}")
      else:
        raise TypeError("Key must be one of NAVIGATE_{ENTER,UP,DOWN,LEFT,RIGHT}")

  def get_busy(self): # Stupid name.
    return self.vlc_player.get_state() == vlc.State.Playing # This treats paused & stopped the same.
