from players.vlc_wrapper import capabilities

if capabilities.movies == True and capabilities.dvd == True:
  from players.vlc_wrapper import Player as Movie
