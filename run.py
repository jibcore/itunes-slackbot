from slackbot import SlackBot
from config import LOG_FILE
import logging

logging.basicConfig(filename=LOG_FILE)
slackbot = SlackBot()
slackbot.read_messages_while()