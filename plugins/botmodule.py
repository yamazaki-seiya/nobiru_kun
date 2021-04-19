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


@listen_to(r'.*@.*')
def homeru_post(message):
    """
    メンション付きの投稿がされた場合に、メッセージ内のメンションされた人をほめる機能
    """

    # TODO: validationする

    HOMERU_MESSAGE_LIST = [
        'のことほんま尊敬するわ:star:',
        '相変わらずすごいやつやな:rose:',
        'ほんとめっちゃ助かってるで:smiling_face_with_3_hearts:',
        'いつもさんきゅーやで:four_leaf_clover:',
        'のおかげで今の俺らがあるんやわ:bird:',
        'お前がおらんかったら無理やったで:Hello:',
    ]

    text = message.body['text']
    print(text)

    m = re.compile(r'<@.*>')
    # TODO: コピペした場合は' ',スラックでメンションを連続して入力する場合には'\xa0'が引っかかる
    text_list = re.split('[\xa0| |,|;]', text)

    for i in text_list:

        mo = m.match(i)

        if mo is not None:

            # 複数ユーザーに同じメッセージを送らない仕様にする
            num = random.randint(0, len(HOMERU_MESSAGE_LIST) - 1)
            homeru_message = HOMERU_MESSAGE_LIST.pop(num)

            mnsmsg = mo.group()

            # TODO:スレッド内のユーザーの返信に、スレッドの外で反応すると会話の流れがわかりにくいため
            if 'thread_ts' in message.body:
                message.send(f'{mnsmsg} {homeru_message}', thread_ts=message.body['thread_ts'])

            else:
                message.send(f'{mnsmsg} {homeru_message}')
