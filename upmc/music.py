from players.vlc_wrapper import capabilities

if capabilities.music == True and capabilities.http == True:
  from players.vlc_wrapper import Player as Music
