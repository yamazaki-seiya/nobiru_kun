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

    homeru_message_list = [
        'のことほんま尊敬するわ:star:',
        '相変わらずすごいやつやな:rose:',
        'ほんとめっちゃ助かってるで',
        'いつもさんきゅーやで',
    ]

    # TODO:メンションされたユーザー名を取り出す
    text = message.body['text']
    print(text)

    m = re.compile(r'<@.*>')

    text_list = re.split('[\xa0| |,|;]', text)

    for i in text_list:

        mo = m.match(i)

        if mo is not None:

            num = random.randint(0, len(homeru_message_list) - 1)
            homeru_message = homeru_message_list.pop(num)

            mnsmsg = mo.group()
            if message.body['thread_ts']:
                message.send(f'{mnsmsg} {homeru_message}', thread_ts=message.body['thread_ts'])
            else:
                message.send(f'{mnsmsg} {homeru_message}')

    # TODO: ほめる君自身の投稿には反応しない仕様にする→# 知らない言葉を聞いた時のデフォルトの応答で対応

    # TODO: スレッド内の投稿を拾うかを決める(デフォルトはチャネル内返信)

    # TODO: 拾う場合：スレッド内でからむ

    # TODO: 拾わない場合：拾わない仕様にする

    # ほめる言葉を作成する
    # TODO:ほめる言葉＋アイコンにする

    # homeru_message_list = (
    #     'のことほんま尊敬するわ:star:',
    #     '相変わらずすごいやつやな:rose:',
    #     'ほんとめっちゃ助かってるで',
    #     'いつもさんきゅーやで',
    # )
    # homeru_message = random.choice(homeru_message_list)

    # # TODO: メンション付きのほめる言葉を作成

    # # ほめる言葉を送信する
    # message.send(homeru_message)
