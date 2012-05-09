#!/usr/bin/python
class os:
  from os import path
class sys:
  import sys
  reload(sys).setdefaultencoding("utf8")
  del sys
  from sys import argv
  from sys import stdout
import urllib
import imdb #Needs a newer version of imdbpy module, get it from http://imdbpy.sourceforge.net/development.html (imdbpy, not the other ones).
import ConfigParser
Config = ConfigParser.ConfigParser()

tv = False
forceimdb = False
forceposter = False
n = 1
while n < len(sys.argv):
  if sys.argv[n] == '--force' or sys.argv[n] == '-f':
    sys.argv.pop(n)
    forceimdb = True
    forceposter = True
  elif sys.argv[n] == '--television' or sys.argv[n] == '-tv':
    sys.argv.pop(n)
    tv = True
  else:
    n += 1

title = '.'.join(sys.argv[1].split('/')[-1].split('.')[:-1])
path = os.path.dirname(sys.argv[1])
if path == '':
  path = '.'

sys.stdout.write('Processing '+path+'/'+title+', ')
sys.stdout.flush()

if forceimdb == False and os.path.isfile('.'.join(sys.argv[1].split('.')[:-1])+'.info'):
  sys.stdout.write('.info file already exists, ')
  sys.stdout.flush()
  Config.read(path+'/'+title+'.info')
else:
  sys.stdout.write('IMDB info, ')
  sys.stdout.flush()
  Config.add_section('IMDB')
  IMDB = imdb.IMDb('http')
  if tv == True:
    showname = None
    seasonnum = 0
    episodenum = 0
    if path.split('/')[-1].lstrip('S').isdigit():
      showname = path.split('/')[-2]
      seasonnum = int(path.split('/')[-1].lstrip('S'))
    elif path.split('/')[-1].startswith('Season ') and ' '.join(path.split('/')[-1].split(' ')[1:]).isdigit():
      showname = path.split('/')[-2]
      seasonnum = int(' '.join(path.split('/')[-1].split(' ')[1:]))
    else:
      showname = path.split('/')[-1]
    if title.lstrip('E').isdigit():
      episodenum = int(title.lstrip('E'))
    elif title.startswith('S') and title.lstrip('S').split('E')[0].isdigit():
      seasonnum = int(title.lstrip('S').split('E')[0])
      if title.split('E')[1].split(' ')[0].isdigit():
        episodenum = int(title.split('E')[1].split(' ')[0])
    if showname == None:
      raise Exception, 'Unable to determine TV show name.'
    else:
      search = IMDB.search_movie(showname)
      for result in search:
        if result['kind'] == 'tv series':
          show = IMDB.get_movie(result.getID())
          IMDB.update(show, 'episodes')
          try: movie = show['episodes'][seasonnum][episodenum]
          except KeyError: raise KeyError, imdb.__file__+': unable to find episode S%02dE%02d' % (seasonnum,episodenum)
          if not Config.has_section('local'): Config.add_section('local')
          Config.set('local', 'title', ' - '.join([showname, 'S%02dE%02d'%(seasonnum,episodenum), movie['title']]))
          print Config.get('local', 'title')
          break
#    raise Exception, "random"
  else:
    search = IMDB.search_movie(title)
    movie = IMDB.get_movie(search[0].getID())
#  if sys.argv[2] == '-tv':
#    print movie.get('episodes')
#    raise Exception, "testing"
  Config.set('IMDB', 'ID', search[0].getID())
  for key in movie.keys():
    item = movie[key]
    if type(item) == list:
      itemstring = ''
      for listitem in item:
  #     try:
        if not listitem == '':
          itemstring += str(listitem)+' | '
  #     except:
  #       print type(listitem), dir(listitem), listitem.encode('utf8')
  #       raise Exception, "Bye bye"
      if not itemstring.rstrip(', ') == '':
        Config.set('IMDB',key,itemstring.rstrip(', '))
    elif not str(item) == '':
      Config.set('IMDB',key,str(item))
  infofile = open(path+'/'+title+'.info','w')
  Config.write(infofile)
  infofile.flush()
  infofile.close()

if (forceposter == True or not os.path.isfile(path+'/'+title+'.jpg')) and Config.has_option('IMDB', 'full-size cover url'):
  sys.stdout.write('poster.')
  sys.stdout.flush()
  postersock = urllib.urlopen(Config.get('IMDB', 'full-size cover url'))
  posterdata = postersock.read()
  if not posterdata == None:
    posterfile = open(path+'/'+title+'.jpg', 'wb')
    posterfile.write(posterdata)
    posterfile.flush()
    posterfile.close()
else:
  if os.path.isfile(path+'/'+title+'.jpg'):
    sys.stdout.write('poster already done.')
    sys.stdout.flush()
  else:
    sys.stdout.write('IMDB has no full-size cover URL.')
    sys.stdout.flush()

sys.stdout.write('\n')
