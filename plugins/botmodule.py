import csv
import math
import os
import random
import re

from slackbot.bot import listen_to

GCP_TOKEN = os.getenv('GCP_TOKEN')
OWM_TOKEN = os.getenv('OWM_TOKEN')

_EXTRACT_USER_PATTERN = re.compile(r'<@.*>')
_MESSAGE_SPLIT_PATTERN = re.compile(r'[\xa0| |,|;]')


@listen_to(r'.*@.*')
def homeru_post(message):
    """
    メンション付きの投稿がされた場合に、メッセージ内のメンションされた人をほめる機能
    """

    _validation_bot_subtype(message)

    # このボットの投稿に反応しないようにする
    _add_bot_message_subtype(message)

    text = message.body['text']
    print(f'ポストされたメッセージ: {text}')
    user_list = _extract_users(text)
    print(f'user_num: {len(user_list)}')

    post_message = _get_post_message(user_list)

    # スレッド内のユーザーの返信に、スレッドの外で反応すると会話の流れがわかりにくいため
    message.send(
        post_message, thread_ts=message.body['thread_ts'] if 'thread_ts' in message.body else None
    )


def _validation_bot_subtype(message):
    """ボットのメッセージか判定する"""
    if 'subtype' in message.body and message.body['subtype'] == 'bot_message':
        return True
    return False


def _add_bot_message_subtype(message):
    """ボットのメッセージだとわかるように判別をつける"""
    message.body['subtype'] = 'bot_message'
    return message


def _create_random_element_list(path, user_num):
    """メッセージの元ファイルを読み出して、ユーザー数分のテキストリストをランダムに生成する"""
    # TODO:コメント生成時に毎回csvファイルを読み込んでいるので、bot.py読み出し時に読みだすようにする。
    with open(path, newline='') as csvfile:
        text_list = [s[0] for s in csv.reader(csvfile)]

    random.shuffle(text_list)

    # メンションされたユーザー数 ＞ テキスト数の場合、
    # テキストが足りなくなるため倍数分だけ要素を増やす
    scale_num = user_num / len(text_list)
    text_list = text_list if scale_num <= 1 else text_list * math.ceil(scale_num)
    return random.shuffle(text_list)[:user_num]


def _extract_users(message):
    """メッセージからメンションするためのユーザーのリストを抽出する"""
    # コメント内のメンションのsplit_stringとして現状以下のパターンが大多数を占める
    #   - ' '（半角スペース）, '\xa0'（ノーブレークスペース）
    splitted_message = re.split(_MESSAGE_SPLIT_PATTERN, message)
    print(f'splitted_message:{splitted_message}')

    # TODO:メンションされたユーザーが重複する場合に返答は1回にするかを検討する
    user_list = []
    for words in splitted_message:
        menttioned_user = _EXTRACT_USER_PATTERN.match(words)
        if menttioned_user is not None:
            user_list.append(menttioned_user.group())

    return user_list


def _get_post_message(user_list):
    """ユーザーをほめるメッセージを生成する"""

    text_list = _create_random_element_list('resources/homeru_message_text.csv', len(user_list))
    stamp_list = _create_random_element_list('resources/homeru_message_stamp.csv', len(user_list))
    post_messages = [f'{u} {t}{s}' for u, t, s in zip(user_list, text_list, stamp_list)]

    return '\n\n'.join(post_messages)
