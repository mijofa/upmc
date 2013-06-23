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

import subprocess
import time


class Music(Player):
  old_track = None
  channel_num = 0
  volume = 0
  mpd_port = mpd_zero_port
  mpc_opts = ["--quiet"]
  def __init__(self, channel_num = 0):
    super(Music, self).__init__(None)
    self.connect(channel_num)
  def connect(self, channel_num = 0):
    self.channel_num = channel_num
    url = channel_urls[self.channel_num]
    super(Music, self)._load(url)
    self.mpd_port = mpd_zero_port+channel_num
  def reconnect(self):
    super(Music, self)._load(channel_urls[self.channel_num])
  def get_channel(self):
    return self.channel_num
  def set_channel(self, value):
    if value >= 0 and value < len(channel_urls):
      self.stop()
      self.connect(value)
      self.play()
  def get_volume(self):
    ret_value = super(Music, self).get_volume()
    self.volume = ret_value
    return ret_value
  def increment_channel(self, value):
    new_channel_num = self.channel_num+value
    while not (new_channel_num >= 0 and new_channel_num < len(channel_urls)):
      if new_channel_num < 0:
        new_channel_num += len(channel_urls)
      elif new_channel_num >= len(channel_urls):
        new_channel_num -= len(channel_urls)
    ret_value = self.set_channel(new_channel_num)
    self.set_volume(self.volume)
    return ret_value
  def next_track(self):
    print subprocess.check_output(["mpc"]+self.mpc_opts+["--host", str(mpd_host), "--port", str(self.mpd_port), "next"])
#    return self.mpc.next()
  def previous_track(self):
    print subprocess.check_output(["mpc"]+self.mpc_opts+["--host", str(mpd_host), "--port", str(self.mpd_port), "prev"])
#    return self.mpc.previous()
  prev_track = previous_track
