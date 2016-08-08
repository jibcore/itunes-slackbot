import itunes
import time
from slackclient import SlackClient
from config import SLACK_API_TOKEN, BOT_CHANNEL, MESSAGE_READ_TIMEOUT, BOT_NAME

class SlackBot:
    def __init__(self):
        self.slack_client = SlackClient(SLACK_API_TOKEN)
        self.bot_commands = {
            '!help': { 'desc': 'Commands list', 'callback': self.help_callback },
            '!itunes': { 'desc': 'iTunes info', 'callback': self.itunes_info_callback },
            '!track': { 'desc': 'Current track info', 'callback': self.track_info_callback },
            '!volume': { 'desc': 'Set volume [0-100]', 'callback': self.change_volume_callback },
            '!next': { 'desc': 'Next track', 'callback': self.next_track_callback },
            '!previous': {'desc': 'Previous track', 'callback': self.previous_track},
            '!startplay' : { 'desc': 'Start playing', 'callback': self.start_play_callback },
            '!pauseplay' : { 'desc': 'Pause playing', 'callback': self.pause_play_callback },
        }

#region Command Callback's
    def help_callback(self):
        output = '\n*Bot Commands:*\n'
        for command, command_info in self.bot_commands.iteritems():
            output += '*{0}* - {1}\n'.format(command, command_info['desc'])
        self.send_message(output)

    def itunes_info_callback(self):
        self.send_message(itunes.get_itunes_info())

    def track_info_callback(self):
        self.send_message(itunes.get_track_info())

    def change_volume_callback(self, value):
        itunes.set_volume(value)

    def start_play_callback(self):
        itunes.start_play()

    def pause_play_callback(self):
        itunes.pause_play()

    def next_track_callback(self):
        itunes.next_track()

    def previous_track(self):
        itunes.previous_track()
#endregion

    def exec_bot_command(self, command, command_arg=None):
        if command in self.bot_commands:
            command_callback = self.bot_commands[command]['callback']
            if not command_arg:
                command_callback()
            else:
                command_callback(command_arg)

    def parse_message(self, message):
        if message and message[0] == '!':
            command_data = message.split(' ', 1)
            if len(command_data) == 1:
              self.exec_bot_command(command_data[0])
            else:
              self.exec_bot_command(command_data[0], command_data[1])

    def send_message(self, message):
        if message:
            self.slack_client.send_message(BOT_CHANNEL, message, BOT_NAME)

    def read_messages_while(self):
        while True:
            event_data = self.slack_client.rtm_read()
            if len(event_data) == 1:
                if event_data[0]['type'] == 'message' and event_data[0]['channel'] == BOT_CHANNEL:
                    self.parse_message(event_data[0]['text'])
            time.sleep(MESSAGE_READ_TIMEOUT)