import csv
import os
import random
import re

from slackbot.bot import listen_to

GCP_TOKEN = os.getenv('GCP_TOKEN')
OWM_TOKEN = os.getenv('OWM_TOKEN')


def add_bot_message_subtype(message):
    """ ボットのメッセージだとわかるように判別をつける """
    message.body['subtype'] = 'bot_message'
    return mess


def validation_bot_subtype(message):
    """ ボットのメッセージか判定する """
    if 'subtype' in message.body and message.body['subtype'] == 'bot_message':
        return True
    return False


def create_homeru_message(user_num):
    """メッセージリストを読み出して、スタンプと組み合わせて、メッセージを生成する"""
    with open('resources/homeru_message_stamp.csv', newline='') as csvfile_stamp:
        homeru_message_stamp_list = [s for s in csv.reader(csvfile_stamp)]

    with open('resources/homeru_message_text.csv', newline='') as csvfile_text:
        homeru_message_text_list = [t for t in csv.reader(csvfile_text)]

    # 複数ユーザーに同じメッセージを送らない仕様にする
    # ユーザーの数よりメッセージの数が少ない場合にも対応する
    # num = random.choice(0, len(homeru_message_stamp_list) - 1)
    # homeru_message = homeru_message_stamp_list.pop(num)
    # num = random.randint(0, len(homeru_message_stamp_list) - 1)
    # homeru_message = homeru_message_stamp_list.pop(num)
    return ['a'] * user_num


def extract_users(message):
    """メッセージからメンションするためのユーザーのリストを抽出する"""
    m = re.compile(r'<@.*>')
    # コピペした場合は' ',スラックでメンションを連続して入力する場合には'\xa0'が引っかかる
    split_character = '[\xa0| |,|;]'
    splitted_message = re.split(split_character, message)
    print(f'splitted_message:{splitted_message}')
    # TODO:メンションされたユーザーが重複する場合に返答は1回にするかを検討する
    user_list = []
    for words in splitted_message:
        mo = m.match(words)
        if mo is not None:
            user_list.append(mo.group())

    return user_list


@listen_to(r'.*@.*')
def homeru_post(message):
    """
    メンション付きの投稿がされた場合に、メッセージ内のメンションされた人をほめる機能
    """

    # TODO: validationする

    text = message.body['text']
    print(f'ポストされたメッセージ: {text}')
    user_list = extract_users(text)
    homeru_message_list = create_homeru_message(len(user_list))

    for user, homeru_message in zip(user_list, homeru_message_list):
        # スレッド内のユーザーの返信に、スレッドの外で反応すると会話の流れがわかりにくいため
        if 'thread_ts' in message.body:
            message.send(f'{user} {homeru_message}', thread_ts=message.body['thread_ts'])
        else:
            message.send(f'{user} {homeru_message}')
