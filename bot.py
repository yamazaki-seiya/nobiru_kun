from typing import Any
import os

from slack_bolt import App, Say
from slack_bolt.adapter.socket_mode.builtin import SocketModeHandler

from plugins.botmodule import homeru_post

app = App(token=os.environ.get('SLACK_BOT_TOKEN'))


@app.message(r'.*@.*')
def homeru_kun(message: dict[str, Any], say: Say):
    homeru_post(message, say)


if __name__ == '__main__':
    SocketModeHandler(app, os.environ['SLACK_APP_TOKEN']).start()
