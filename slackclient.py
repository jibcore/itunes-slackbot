import json
import time
import slacker
from ssl import SSLError

from websocket import (
    create_connection, WebSocketException
)

class SlackClient(object):
    def __init__(self, token, bot_icon=None, bot_emoji=None, connect=True):
        self.token = token
        self.bot_icon = bot_icon
        self.bot_emoji = bot_emoji
        self.username = None
        self.domain = None
        self.login_data = None
        self.websocket = None
        self.users = {}
        self.channels = {}
        self.connected = False
        self.webapi = slacker.Slacker(self.token)

        if connect:
            self.rtm_connect()

    def rtm_connect(self):
        reply = self.webapi.rtm.start().body
        time.sleep(1)
        self.parse_slack_login_data(reply)

    def parse_channel_data(self, channel_data):
        self.channels.update({c['id']: c for c in channel_data})

    def parse_slack_login_data(self, login_data):
        self.login_data = login_data
        self.domain = self.login_data['team']['domain']
        self.username = self.login_data['self']['name']
        self.users = dict((u['id'], u) for u in login_data['users'])
        self.parse_channel_data(login_data['channels'])
        self.parse_channel_data(login_data['groups'])
        self.parse_channel_data(login_data['ims'])

        self.websocket = create_connection(self.login_data['url'])
        self.websocket.sock.setblocking(0)

    def send_to_websocket(self, data):
        data = json.dumps(data)
        self.websocket.send(data)

    def ping(self):
        return self.send_to_websocket({'type': 'ping'})

    def websocket_safe_read(self):
        data = ''
        while True:
            try:
                data += '{0}\n'.format(self.websocket.recv())
            except WebSocketException:
                self.reconnect()
            except Exception as e:
                if isinstance(e, SSLError) and e.errno == 2:
                    pass
            return data.rstrip()

    def rtm_read(self):
        json_data = self.websocket_safe_read()
        data = []
        if json_data != '':
            for d in json_data.split('\n'):
                data.append(json.loads(d))
        return data

    def send_message(self, channel, message, username = None, attachments=None, as_user=True):
        if username is None:
            username = self.login_data['self']['name']
        else:
            as_user = False

        self.webapi.chat.post_message(
                channel,
                message,
                username=username,
                icon_url=self.bot_icon,
                icon_emoji=self.bot_emoji,
                attachments=attachments,
                as_user=as_user)

    def find_channel_by_name(self, channel_name):
        for channel_id, channel in self.channels.items():
            try:
                name = channel['name']
            except KeyError:
                name = self.users[channel['user']]['name']
            if name == channel_name:
                return channel_id