import commands

def itunes_command(command):
    if not command:
        return 'Unknown command'
    return commands.getoutput("osascript -e 'tell application \"iTunes\" to {0}'".format(command))

def get_itunes_info():
    status = itunes_command('player state as string')
    version = itunes_command('version as string')
    volume = itunes_command('sound volume as string')

    output = '\n'
    output += '*iTunes v{0}*\n'.format(version)
    output += '*Status:* {0}\n'.format(status)
    output += '*Volume:* {0}\n'.format(volume)
    return output

def get_track_info():
    artist = itunes_command('artist of current track as string')
    track = itunes_command('name of current track as string')
    album = itunes_command('album of current track as string')
    album_year = itunes_command('year of current track')
    track_time = itunes_command('time of current track as string')

    output = '\n'
    output += '*Track:* {0} - {1} [{2}]\n'.format(artist, track, track_time)
    output += '*Album:* {0} [{1}]\n'.format(album, album_year)
    return output

def set_volume(volume):
    try:
        if int(volume) >= 0 and int(volume) <= 100:
            return itunes_command('set sound volume to ' + volume)
    except:
        return 'Unknown volume value.'

def start_play():
    return itunes_command('play')

def pause_play():
    return itunes_command('pause')

def next_track():
    return itunes_command('next track')

def previous_track():
    return itunes_command('previous track')