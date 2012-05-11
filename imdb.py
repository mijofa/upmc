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
noforceimdb = False
forceposter = False
n = 1
while n < len(sys.argv):
  if sys.argv[n] == '--force-poster' or sys.argv[n] == '-f':
    sys.argv.pop(n)
    forceposter = True
  if sys.argv[n] == '--no-overwrite':
    sys.argv.pop(n)
    noforceimdb = True
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

if os.path.isfile(path+'/'+title+'.info'):
  Config.read(path+'/'+title+'.info')

if noforceimdb == True and (Config.has_section('IMDB') and not Config.options('IMDB') == ['id']):
  sys.stdout.write("'.info' file already exists, ")
  sys.stdout.flush()
else:
  sys.stdout.write('IMDB info, ')
  sys.stdout.flush()
  IMDBid = 0
  if Config.has_section('local') and Config.has_option('local', 'imdb id'):
    IMDBid = Config.getint('local', 'imdb id')
  elif Config.has_section('IMDB') and Config.has_option('IMDB', 'id'):
    IMDBid = Config.getint('IMDB', 'id')
  if Config.has_section('IMDB'): Config.remove_section('IMDB')
  Config.add_section('IMDB')
  IMDB = imdb.IMDb('http')
  if not IMDBid == 0:
    movie = IMDB.get_movie(IMDBid)
  elif tv == True:
    showname = None
    seasonnum = None
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
    elif ' - ' in title:
      showname = title.split(' - ')[0]
      temptitle = title.split(' - ')[1]
      if temptitle.lstrip('E').isdigit():
        episodenum = int(temptitle.lstrip('E'))
      elif temptitle.startswith('S') and temptitle.lstrip('S').split('E')[0].isdigit():
        seasonnum = int(temptitle.lstrip('S').split('E')[0])
        if temptitle.split('E')[1].split(' ')[0].isdigit():
          episodenum = int(temptitle.split('E')[1].split(' ')[0])
    if showname == None:
      raise Exception, 'Unable to determine TV show name.'
    else:
      if path.split('/')[-1].lstrip('S').isdigit() or (path.split('/')[-1].startswith('Season ') and ' '.join(path.split('/')[-1].split(' ')[1:]).isdigit()):
        showrootpath = '/'.join(path.split('/')[:-1])
      else:
        showrootpath = path
      if os.path.isfile(showrootpath+'/'+'.IMDBid.txt'):
        show = IMDB.get_movie(int(open(showrootpath+'/'+'.IMDBid.txt', 'r').readline()))
      else:
        search = IMDB.search_movie(showname)
        for result in search:
          if result['kind'] == 'tv series':
            show = IMDB.get_movie(result.getID())
            open(showrootpath+'/'+'.IMDBid.txt', 'w').write(str(result.getID()+'\n'))
            break
      grabshowposter = True
      for extension in ['.jpg', '.png', '.jpeg', '.gif']:
        if (os.path.isfile(showrootpath+'/'+'folder'+extension) or os.path.isfile(showrootpath+'/'+'folder'+extension.upper())) or (os.path.isfile(showrootpath+'/'+'.folder'+extension) or os.path.isfile(showrootpath+'/'+'.folder'+extension.upper())):
          grabshowposter = False
          break
      if grabshowposter == True:
        if show.has_key('full-size cover url'):
          showposterurl = '.'.join(show['full-size cover url'].split('.')[:-1])+'._V1_SX560_SY420.jpg'
          showpostersock = urllib.urlopen(showposterurl)
          showposterdata = showpostersock.read()
          if not showposterdata == None:
            showposterfile = open(showrootpath+'/'+'.folder.jpg', 'wb')
            showposterfile.write(showposterdata)
            showposterfile.flush()
            showposterfile.close
      IMDB.update(show, 'episodes')
      if seasonnum == None:
        try: movie = IMDB.get_movie(show['episodes'][episodenum].getID())
        except KeyError: raise KeyError, imdb.__file__+': unable to find episode S%02dE%02d' % (seasonnum,episodenum)
      else:
        try: movie = IMDB.get_movie(show['episodes'][seasonnum][episodenum].getID())
        except KeyError: raise KeyError, imdb.__file__+': unable to find episode S%02dE%02d' % (seasonnum,episodenum)
      if not Config.has_section('local'): Config.add_section('local')
      if not Config.has_option('local', 'title'): Config.set('local', 'title', ' - '.join([showname, 'S%02dE%02d'%(seasonnum,episodenum), movie['title']]))
  else:
    search = IMDB.search_movie(title)
    movie = IMDB.get_movie(search[0].getID())
  Config.set('IMDB', 'id', movie.getID())
  for key in movie.keys():
    item = movie[key]
    if type(item) == list:
      itemstring = ''
      for listitem in item:
        if not listitem == '':
          itemstring += str(listitem)+' | '
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
  posterurl = '.'.join(Config.get('IMDB', 'full-size cover url').split('.')[:-1])+'._V1_SX560_SY420.jpg'
  postersock = urllib.urlopen(posterurl)
  posterdata = postersock.read()
  if not posterdata == None:
    posterfile = open(path+'/'+title+'.jpg', 'wb')
    posterfile.write(posterdata)
    posterfile.flush()
    posterfile.close()
else:
  if not Config.has_option('IMDB', 'full-size cover url'):
    sys.stdout.write('IMDB has no full-size cover URL.')
    sys.stdout.flush()
  elif os.path.isfile(path+'/'+title+'.jpg'):
    sys.stdout.write('poster already done.')
    sys.stdout.flush()
  else:
    sys.stdout.write('unknown issue with grabbing poster.')
    sys.stdout.flush()

sys.stdout.write('\n')
