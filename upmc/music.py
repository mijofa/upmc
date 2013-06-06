from players.vlc_wrapper import capabilities

mpd_host = "music"
mpd_zero_port = 6600

channel_urls = [
    "http://music/ch00.mp3",
    "http://music/ch01.mp3",
    "http://music/ch02.mp3",
    "http://music/ch03.mp3",
    "http://music/ch04.mp3",
    "http://music/ch05.mp3",
    ]

if capabilities.music == True and capabilities.http == True:
  from players.vlc_wrapper import *

import mpd

print Player, dir(Player)

class Music(Player):
  old_track = None
  channel_num = 0
  def __init__(self, channel_num = 0):
    print 'init', channel_num
    super(Music, self).__init__(None)
    self.mpc = mpd.MPDClient()
    self.connect(channel_num)
  def reconnect(self):
    super(Music, self).stop()
    super(Music, self).play()
  def connect(self, channel_num = 0):
    self.channel_num = channel_num
    url = channel_urls[self.channel_num]
    super(Music, self)._load(url)
    self.mpc.connect(mpd_host, mpd_zero_port+channel_num)
  def stop(self):
    try: self.mpc.disconnect()
    except mpd.ConnectionError as e:
      if e.message != "Not connected":
        raise e
    super(Music, self).stop()
  def get_channel(self):
    return self.channel_num
  def set_channel(self, value):
    if value > 0 and value < len(channel_urls):
      self.stop()
      self.connect(value)
      self.play()
  def increment_channel(self, value):
    new_channel_num = self.channel_num+value
    while not (new_channel_num >= 0 and new_channel_num < len(channel_urls)):
      if new_channel_num < 0:
        new_channel_num += len(channel_urls)
      elif new_channel_num >= len(channel_urls):
        new_channel_num -= len(channel_urls)
    return self.set_channel(new_channel_num)
  def next_track(self):
    return self.mpc.next()
  def previous_track(self):
    return self.mpc.previous()
  prev_track = previous_track
