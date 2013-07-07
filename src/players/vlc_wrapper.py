import vlc
import time

# player.get_meta(vlc.Meta.Title)

NAVIGATE_ENTER = vlc.NavigateMode.activate
NAVIGATE_UP = vlc.NavigateMode.up
NAVIGATE_DOWN = vlc.NavigateMode.down
NAVIGATE_LEFT = vlc.NavigateMode.left
NAVIGATE_RIGHT = vlc.NavigateMode.right

class capabilities:
  movies = True
  music = True
  http = True
  dvd = True

class Player(object):
  volume = 75
  current_spu = -1
  def __init__(self, filename):
    self.start_time = -1
    self.vlc_instance = vlc.Instance("--no-video-title --no-keyboard-events --volume 1")
    self.vlc_player = self.vlc_instance.media_player_new()
    self.vlc_player_em = self.vlc_player.event_manager()
    self.vlc_player.video_set_key_input(0)
    if filename != None:
      self._load(filename)
  def _load(self, filename):
    self.filename = filename
    self.vlc_media = self.vlc_instance.media_new(filename, '--loop')
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
    while self.vlc_player.get_state() == vlc.State.Opening: pass # This is bad.
    self.vlc_player.video_set_spu(1)
    if self.start_time > 0: # VLC won't let me set the time before I start playing, this is a workaround. self.set_time sets this variable if the media stream is not running.
      self.vlc_player.set_time(self.start_time)
      self.start_time = 0
    time.sleep(0.01) # I'd rather not use a delay like this.
    self.set_volume(self.volume)
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
    return self.vlc_player.audio_get_volume()/100.0 # Should I be treating 200% as max or 100% ?
  def set_volume(self, value):
    # Set volume to value.
    # Return current volume.
    self.vlc_player.audio_set_volume(int(value*100.0)) # Should I be treating 200% as max or 100% ?
    self.volume = self.get_volume()
    return self.volume
  def increment_volume(self, value):
    # Increment volume by value.
    # Return current volume.
    return self.set_volume(self.get_volume()+value) # Should I be treating 200% as max or 100% ?
  def get_mute(self):
    # Return current mute state. True = muted, False = not
    return bool(self.vlc_player.audio_get_mute())
  def set_mute(self, value):
    # If value == True, mute. else value == False, unmute.
    # Return current mute state
    if type(value) != bool:
      raise TypeError("value must be a bool")
    self.vlc_player.audio_set_mute(value)
    return self.get_mute()
  def toggle_mute(self):
    # Toggles mute state.
    # Return current mute state.
    self.vlc_player.audio_toggle_mute()
    return self.get_mute()
  def get_audio_track(self):
    # Return current audio track. Don't know how to handle this, probably a tuple including track # and description.
    return self.vlc_player.audio_get_track_description()[self.vlc_player.audio_get_track()]
  def set_audio_track(self, value):
    # Set audio track to value.
    # Return audio track
    if type(value) != int:
      raise TypeError("value must be an int")
    self.vlc_player.audio_set_track(self.vlc_player.audio_get_track_description()[value][0])
    return self.get_audio_track()
  def increment_audio_track(self, value):
    # Set audio track to current audio track + value.
    # Return audio track.
    current_audio_track = self.vlc_player.audio_get_track()
    if self.vlc_player.audio_get_track_count()-1 == 0:
      return (0, "No audio tracks found")
    elif current_audio_track == self.vlc_player.audio_get_track_count()-1 and value > 0:
      self.vlc_player.audio_set_track(1)
    elif current_audio_track == 0 and value < 0:
      self.vlc_player.audio_set_track(self.vlc_player.audio_get_track_count()-1)
    else:
      self.vlc_player.audio_set_track(current_audio_track+value)
    return self.get_audio_track()
  def get_length(self):
    # Return length of media file in seconds.
    return .001 * self.vlc_player.get_length() # Convert milliseconds into seconds
  def get_time(self):
    # Return current time in seconds.
    return .001 * self.vlc_player.get_time() # Convert milliseconds into seconds
  def set_time(self, value):
    # Seek to value seconds.
    # Return current time in seconds.
    vlc_value = long(value * 1000L) # VLC works with milliseconds, I prefer working with seconds.
    if self.vlc_player.get_time() == -1L:
      self.start_time = vlc_value # VLC won't let me set the time before I start playing, this is a workaround. self.play sets the start time to this variable if set.
    else:
      self.vlc_player.set_time(vlc_value)
    return self.get_time()
  def increment_time(self, value):
    # Seek to current time+value seconds.
    # Return current time in seconds
    return self.set_time(self.get_time()+value)
  def get_subtitles_visibility(self):
    # Return subtitles visibility.
    spu = self.vlc_player.video_get_spu()
    if spu == 0 or spu == -1:
      return False
    else:
      self.current_spu = spu
      return True
  def set_subtitles_visibility(self, value):
    # Set subtitles visibility to value.
    # Return subtitles visibility.
    if type(value) != bool:
      raise TypeError("value must be a bool")
    self.get_subtitles_track()
    if value == True and self.current_spu == -1:
      self.vlc_player.video_set_spu(1)
    elif value == True:
      self.vlc_player.video_set_spu(self.current_spu)
    elif value == False:
      self.vlc_player.video_set_spu(0)
    else:
      raise Exception("WTF")
    return self.get_subtitles_visibility()
  def toggle_subtitles_visibility(self):
    # Toggle subtitles visibility.
    # Return subtitles visibility.
    return self.set_subtitles_visibility(self.get_subtitles_visibility() == False)
  def get_subtitles_track(self):
    # Return subtitles track
    spu = self.vlc_player.video_get_spu()
    if spu != 0 and spu != -1:
      self.current_spu = spu
    return self.vlc_player.video_get_spu_description()[self.current_spu]
  def set_subtitles_track(self, value):
    # Set subtitles track to value.
    # Return subtitles track
    if type(value) != int:
      raise TypeError("value must be an int")
    self.vlc_player.video_set_spu(value+1)
    return self.get_subtitles_track()
  def increment_subtitles_track(self, value):
    # Set subtitles track to current subtitles track + value.
    # Return subtitles track.
    current_subtitles = self.vlc_player.video_get_spu()
    if self.vlc_player.video_get_spu_count() == 0:
      return (0, "No subtitles found")
    elif current_subtitles == self.vlc_player.video_get_spu_count() and value > 0:
      self.vlc_player.video_set_spu(0)
    elif current_subtitles == 0 and value < 0:
      self.vlc_player.video_set_spu(self.vlc_player.video_get_spu_count())
    else:
      self.vlc_player.video_set_spu(current_subtitles+value)
    return self.get_subtitles_track()
  def get_stream_title(self):
    return self.vlc_media.get_meta(vlc.Meta.Title)
  def get_now_playing(self):
    try: now_playing = self.vlc_media.get_meta(vlc.Meta.NowPlaying)
    except UnicodeDecodeError as e:
      now_playing = unicode(e.object, sys.getfilesystemencoding(), 'replace')
    return now_playing

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
      if type(key) == type(NAVIGATE_ENTER):
        if key in [NAVIGATE_ENTER, NAVIGATE_UP, NAVIGATE_DOWN, NAVIGATE_LEFT, NAVIGATE_RIGHT]:
          self.vlc_player.navigate(key)
          return True
        else:
          raise ValueError("Key must be one of NAVIGATE_{ENTER,UP,DOWN,LEFT,RIGHT}")
      else:
        raise TypeError("Key must be one of NAVIGATE_{ENTER,UP,DOWN,LEFT,RIGHT}")

  def get_state(self):
    vlc_state = self.vlc_player.get_state()
    if vlc_state == vlc.State.Playing:
      return "Playing"
    elif vlc_state == vlc.State.Paused:
      return "Paused"
    elif vlc_state == vlc.State.Ended:
      return "Ended"
    else:
      return vlc_state
