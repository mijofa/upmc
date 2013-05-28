"""
import threading
import urllib2
import time
import mpd
import sys
import os

BUFFER_LENGTH = 1024

class music(threading.Thread):
  channel_num = 0
  new_channel_num = None
  channels = [
      ("http://music/ch00.mp3", ("music", 6600)),
      ("http://music/ch01.mp3", ("music", 6601)),
      ("http://music/ch02.mp3", ("music", 6602)),
      ("http://music/ch03.mp3", ("music", 6603)),
      ("http://music/ch04.mp3", ("music", 6604)),
      ("http://music/ch05.mp3", ("music", 6605)),
  ]
  def __init__(self):
    self.instance = vlc.Instance("--no-video-title --no-keyboard-events")
    self.player = self.instance.media_player_new()
    self.player.video_set_key_input(0)
    self.player_event_manager = self.player.event_manager()
"""
pygame.mixer.init(buffer=1024*7) # Buffer size likely needs more fine tuning, I might drop the quality on the server. Coincidentally at current quality it's about 1024 per second.

class CustomHTTPError(Exception):
  def __init__(self, message):
    self.message = message
class RedirectException(Exception):
  def __init__(self, newurl):
    self.newurl = newurl

class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
  def redirect_request(self, req, fp, code, msg, hdrs, newurl):
    raise RedirectException(newurl)

class music(threading.Thread):
  volume = 0.25
  title = ''
  track_info = {}
  channel_num = 0
  channel_name = ''
  new_channel_num = None
  channels = [
      ("http://music/ch00.mp3", ("music", 6600)),
      ("http://music/ch01.mp3", ("music", 6601)),
      ("http://music/ch02.mp3", ("music", 6602)),
      ("http://music/ch03.mp3", ("music", 6603)),
      ("http://music/ch04.mp3", ("music", 6604)),
      ("http://music/ch05.mp3", ("music", 6605)),
  ]
  muted = False
  new_track_hook = None
  def __init__(self):
    super(music, self).__init__()
    self.mpc = mpd.MPDClient()
    self._stop = threading.Event()
    pygame.mixer.music.set_volume(self.volume)
  def stop(self):
    self._stop.set()
  def connect(self):
    url = self.channels[self.channel_num][0]
    retry = True
    while retry == True:
      try:
        self.http_request = urllib2.Request(url)
        self.http_request.add_header('Icy-MetaData','1')
        self.http_opener = urllib2.build_opener(MyHTTPRedirectHandler)
        self.http_response = self.http_opener.open(self.http_request)
        try: self.mpc.disconnect()
        except: pass
        self.mpc.connect(*self.channels[self.channel_num][1])
        retry = False
      except RedirectException as e:
        url = e.newurl
        retry = True
    self.get_metaint()
  def disconnect(self):
    try: self.mpc.disconnect()
    except mpd.ConnectionError as e:
      if e.message != "Not connected":
        raise e
    self.http_opener.close()
    self.http_response.fp.close()
  def get_metaint(self):
    headers = True
    while headers:
      line = self.readline()
      print line.rstrip('\r\n')
      if line[0:12] == "icy-metaint:":
        self.icy_interval = int(line[12:])
      if line[0:9] == "icy-name:":
        self.title = line[10:].rstrip('\r\n')
      elif line == "\r\n":
        headers = False
  def read(self, chunk_size):
    if chunk_size == 0:
      return ''
    data = self.http_response.read(chunk_size)
    if data != '':
      return data
    raise CustomHTTPError("Connection lost")
  def readline(self):
    data = self.http_response.readline()
    if data != '':
      return data
    raise CustomHTTPError("Connection lost")
  def reconnect(self):
    no_conn = True
    tries = 0
    while no_conn == True and tries < 10:
      try:
        self.http_response = self.http_opener.open(self.http_request)
        no_conn = False
      except:
        tries += 1
    if no_conn == True:
      raise CustomHTTPError("Can't connect to HTTP stream")
    self.get_metaint()
  def process_icy(self):
    len = ord(self.read(1))*16
    if len != 0:
      icy_data = self.read(len).rpartition(';')
      self.track_info.clear()
      for pair in icy_data[0].split(';'):
        if not '=' in pair:
          key = pair
          value = None
        else:
          key = pair.split('=', 1)[0]
          value = pair.split('=', 1)[1].strip("'\"")
        self.track_info.update({key: value})
      self.track_info.update(self.mpc.currentsong())
      print time.ctime(), self.track_info
      leftover = icy_data[1]
      if self.new_track_hook != None:
        self.new_track_hook()
      return leftover # Supposedly these "leftovers" are empty bytes and should be dropped. I'm not seeing empty bytes here though, so I'm assuming they're part of the MP3 stream and passing them on to PyGame.
                      # I'm using MPD as the streaming server, perhaps that doesn't properly follow the spec here?
    return ''
  def run(self):
    buffer_filename = os.tmpnam()+'.mp3'
    os.mkfifo(buffer_filename)
    self.stream_buffer = open(buffer_filename, 'w+') # Opening this read-write is wrong, I only want to write to it. But I can't figure out how to open one side of a FIFO without opening the other side yet.
    self.connect()
    global BUFFER_LENGTH
    if self.icy_interval < BUFFER_LENGTH:
      BUFFER_LENGTH = self.icy_interval
    data = self.read(BUFFER_LENGTH)
    self.stream_buffer.write(data)
    pygame.mixer.music.load(buffer_filename)
    pygame.mixer.music.play()
    offset = BUFFER_LENGTH
    while not self._stop.is_set():
      try:
        if self.new_channel_num != None:
          self.http_response.close()
          self.channel_num = self.new_channel_num
          self.connect()
          self.new_channel_num = None
          offset = 0
        if self.icy_interval - offset < BUFFER_LENGTH:
          data = self.read(self.icy_interval - offset)
          leftover = self.process_icy()
          data += leftover
          offset = 0
          self.stream_buffer.write(data)
        else:
          data = self.read(BUFFER_LENGTH)
          offset += BUFFER_LENGTH
          if data != '':
            self.stream_buffer.write(data)
          else:
            self.reconnect()
      except CustomHTTPError as e:
        if e.message == "Connection lost":
          self.reconnect()
          offset = 0
        else:
          raise e
    pygame.mixer.music.stop()
    self.disconnect()
    self.stream_buffer.close()
    os.remove(buffer_filename)
  def set_mute(self, value):
    print "Setting mute"
    if type(value) == bool:
      print "bool"
      if value == True:
        print "True"
        self.volume = pygame.mixer.music.get_volume()
        print "Got volume"
        pygame.mixer.music.set_volume(0)
        print "set volume"
        self.muted = True
        print "Set muted"
      elif value == False:
        print "False"
        pygame.mixer.music.set_volume(self.volume)
        print "Set volume"
        self.muted = False
        print "Set muted"
      else:
        raise Exception("WTF?!?!?!?")
    else:
      raise TypeError("set_mute() argument must be a bool, not %s" % type(value))
  def toggle_mute(self):
    self.set_mute(self.muted==False)
  def set_volume(self, value):
    pygame.mixer.music.set_volume(value)
    self.volume = pygame.mixer.music.get_volume()
    return self.volume
  def increment_volume(self, value):
    return self.set_volume(self.volume+value)
  def get_volume(self):
    return self.volume
  def set_channel(self, new_channel_num):
    self.new_channel_num = new_channel_num
    return self.new_channel_num
  def increment_channel(self, new_channel_increment):
    new_channel_num = self.channel_num+new_channel_increment
    while not (new_channel_num >= 0 and new_channel_num < len(self.channels)):
      if new_channel_num < 0:
        new_channel_num += len(self.channels)
      elif new_channel_num >= len(self.channels):
        new_channel_num -= len(self.channels)
    return self.set_channel(new_channel_num)
  def next(self):
    return self.mpc.next()
  def previous(self):
    return self.mpc.previous()
  prev = previous

def m():
  p = music()#"http://music/ch05.mp3")
  p.start()
  data = ''
  while data != None:
    try: data = raw_input('> ')
    except EOFError: break
    print p.title , '-', data
    try: print eval(data)
    except Exception as e: print e
  print "EOF detected: Shutting down."
  p.stop()