__module_name__ = 'Spoti.py' 
__module_version__ = '0.0.2' 
__module_description__ = 'Spotify controller'
__module_author__ = 'Scout @ irc.geekshed.net/codecrew'

print '\0034',__module_name__, __module_version__,'has been loaded\003'

# We need this stuff
import xchat, commands
import dbus, re

# Set our var
spotify = None
connected = False

#### Helper functions
def spotiCheck():
    # Cheap way to make our changes stick
    global spotify, connected
    # Gain control!
    if dbus.SessionBus().name_has_owner('com.spotify.qt') == False:
        print 'Spotify is not running'
        connected = False
        return False
    elif connected == False:
        spotify = dbus.SessionBus().get_session().get_object('com.spotify.qt','/')
        connected = True
    return True

def getMeta():
    # No need to check if loaded here, will only get here if passed already
    metaData = spotify.GetMetadata()
    info = dict()
    mapList = {'artist':'xesam:artist', 'album':'xesam:album', 'title':'xesam:title', 'url':'xesam:url'}
    # Run the data against our map. Don't get lost
    for key, value in mapList.items():
        if not value in metaData:
            continue
        piece = metaData[value]
        if isinstance(piece, list):
            piece = ', '.join(piece)
        info[key] = piece.encode('utf-8')
    return info

# thanks to http://xchatdata.net/Scripting/TextFormatting
def colorDecode(word):
   _B = re.compile('%B', re.IGNORECASE)
   _C = re.compile('%C', re.IGNORECASE)
   _R = re.compile('%R', re.IGNORECASE)
   _O = re.compile('%O', re.IGNORECASE)
   _U = re.compile('%U', re.IGNORECASE)
   return _B.sub('\002', _C.sub('\003', _R.sub('\026', _O.sub('\017', _U.sub('\037', word)))))

#### Startup
spotiCheck()

#### Commands
def spNext(word, word_eol, userdata):
    # Are we loaded?
    if spotiCheck() == False:
        return
    # Skip the song
    spotify.Next()
    return xchat.EAT_XCHAT

def spPrev(word, word_eol, userdata):
    if spotiCheck() == False:
        return
    # Mark the song
    prevSong = getMeta()['title']
    # Go to previous song
    spotify.Previous()
    # Mark the current song again
    curSong = getMeta()['title']
    # Check to see if we actually went back a song
    if prevSong == curSong:
        # This should change it now
        spotify.Previous()
    return xchat.EAT_XCHAT

def spToggleplay(word, word_eol, userdata):
    if spotiCheck() == False:
        return
    # Function to both play and pause current song
    spotify.PlayPause()
    return xchat.EAT_XCHAT

def spNowPlaying(word, word_eol, userdata):
    if spotiCheck() == False:
        return
    info = getMeta()
    # Should always have these, but lets not make assumptions
    if info.has_key('title') and info.has_key('artist'):
        msg = 'is listening to %U' + info['title'] +  '%O by %B' + info['artist'] + '%O - http://open.spotify.com/track/' + info['url'].split(':')[2]
        xchat.command('ME %s' % colorDecode(msg))
    return xchat.EAT_XCHAT

xchat.hook_command('skip', spNext)
xchat.hook_command('prev', spPrev)
xchat.hook_command('play', spToggleplay)
xchat.hook_command('pause', spToggleplay)
xchat.hook_command('np', spNowPlaying)
