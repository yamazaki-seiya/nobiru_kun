import os
import random
import re

from slackbot.bot import listen_to

GCP_TOKEN = os.getenv('GCP_TOKEN')
OWM_TOKEN = os.getenv('OWM_TOKEN')


def add_bot_message_subtype(message):
    """ ボットのメッセージだとわかるように判別をつける """
    message.body['subtype'] = 'bot_message'
    return message


def validation_bot_subtype(message):
    """ ボットのメッセージか判定する """
    if 'subtype' in message.body and message.body['subtype'] == 'bot_message':
        return True
    return False


@listen_to(r'.*@.*@.*')
def divede_mention(message):
    """ 複数メンション時にメンションを個々に分けてメッセージを投下 """

    if validation_bot_subtype(message):
        return None

    message = add_bot_message_subtype(message)

    # メンション(@hoge.hoge など) は slackID(<@〇〇>)に自動で変換される
    m = re.compile(r'<@.*>')
    text = message.body['text']
    # コピペした場合は' ',スラックでメンションを連続して入力する場合には'\xa0'が引っかかる
    text_list = re.split('[\xa0| |,|;]', text)
    # print(text_list)
    for i in text_list:
        mo = m.match(i)
        if mo is not None:
            mnsmsg = mo.group()
            message.send(mnsmsg)


@listen_to(r'.*@.*')
def homeru_post(message):
    """
    メンション付きの投稿がされた場合に、メッセージ内のメンションされた人をほめる機能
    """

    # メンションが入っている投稿がされた場合

    # TODO: ほめる君自身の投稿には反応しない仕様にする

    # TODO: スレッド内の投稿を拾うかを決める
    # TODO: 拾う場合：スレッド内でからむ
    # TODO: 拾わない場合：拾わない仕様にする

    # ほめる言葉を作成する
    # TODO:ほめる言葉＋アイコンにする

    homeru_message_list = ('すごいぞ', 'sugoizo', 'ohayou', 'おほほほ')
    homeru_message = random.choice(homeru_message_list)

    # ほめる言葉を送信する
    message.send(homeru_message)
