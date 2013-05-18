import pygame.mixer
import threading
import urllib2
import time
import os

BUFFER_LENGTH = 1024

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

class music_thread(threading.Thread):
  icy_name = ''
  icy_info = {}
  channel_num = 0
  new_channel_num = None
  channel_urls = [
      "http://music/ch00.mp3",
      "http://music/ch01.mp3",
      "http://music/ch02.mp3",
      "http://music/ch03.mp3",
      "http://music/ch04.mp3",
      "http://music/ch05.mp3",
  ]
  def get_metaint(self):
    headers = True
    while headers:
      line = self.readline()
      print line.rstrip('\r\n')
      if line[0:12] == "icy-metaint:":
        self.icy_interval = int(line[12:])
      if line[0:9] == "icy-name:":
        self.icy_name = line[10:].rstrip('\r\n')
      elif line == "\r\n":
        headers = False
  def change_channel(self, new_channel_num):
    self.new_channel_num = new_channel_num
  def connect(self):
    url = self.channel_urls[self.channel_num]
    retry = True
    while retry == True:
      try:
        self.http_request = urllib2.Request(url)
        self.http_request.add_header('Icy-MetaData','1')
        self.http_opener = urllib2.build_opener(MyHTTPRedirectHandler)
        self.http_response = self.http_opener.open(self.http_request)
        retry = False
      except RedirectException as e:
        url = e.newurl
        retry = True
    self.get_metaint()
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
  def read(self, chunk_size):
    if chunk_size == 0:
      return ''
    data = self.http_response.read(chunk_size)
    if data != '':
      return data
    self.reconnect()
    raise CustomHTTPError("Reconnected")
  def readline(self):
    data = self.http_response.readline()
    if data != '':
      return data
    self.reconnect()
    raise CustomHTTPError("Reconnected")
  def process_icy(self):
    len = ord(self.read(1))*16
    if len != 0:
      icy_data = self.read(len).rpartition(';')
      self.icy_info.clear()
      for pair in icy_data[0].split(';'):
        if not '=' in pair:
          key = pair
          value = None
        else:
          key = pair.split('=', 1)[0]
          value = pair.split('=', 1)[1].strip("'\"")
        self.icy_info.update({key: value})
      print 'info', self.icy_info
      leftover = icy_data[1]
      return leftover # Supposedly these "leftovers" are empty bytes and should be dropped. I'm not seeing empty bytes here though, so I'm assuming they're part of the MP3 stream and passing them on to PyGame.
                      # I'm using MPD as the streaming server, perhaps that doesn't properly follow the spec here?
    return ''
  def run(self):
    self.buffer_filename = os.tmpnam()+'.mp3'
    os.mkfifo(self.buffer_filename)
    self.stream_buffer = open(self.buffer_filename, 'w+') # Opening this read-write is wrong, I only want to write to it. But I can't figure out how to open one side of a FIFO without opening the other side yet.
    self.connect()
    global BUFFER_LENGTH
    if self.icy_interval < BUFFER_LENGTH:
      BUFFER_LENGTH = self.icy_interval
    data = self.read(BUFFER_LENGTH)
    self.stream_buffer.write(data)
    pygame.mixer.music.load(self.buffer_filename)
    pygame.mixer.music.play()
    offset = BUFFER_LENGTH
    while True:
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
        if e.message == "Reconnected":
          offset = 0
        else:
          raise e

class music(object):
  def go(self, url):
    http = http_thread()
    buffer_filename = http.connect(url)
    http.start()
    return http

def m():
  a = music_thread()#"http://music/ch05.mp3")
  a.start()
  data = ''
  while data != None:
    data = raw_input('blah? ')
    print a.icy_name, '-', data
    try: print eval(data)
    except EOFError: break
    except Exception as e: print e
