import csv
import math
import random
import re

from slackbot.bot import listen_to

# Slackへの投稿コメントからユーザーIDを抽出するための正規表現パターン
_EXTRACT_USER_PATTERN = re.compile(r'<@\w+>')


@listen_to(r'.*@.*')
def homeru_post(message):
    """
    メンション付きの投稿がされた場合に、メッセージ内のメンションされた人をほめる機能
    """
    if _is_bot_message(message):
        # botからのメッセージの場合反応しない
        return
    text = message.body['text']
    print(f'ポストされたメッセージ: {text}')
    user_list = _extract_users(text)
    print(f'user_num: {len(user_list)}')

    post_message = _get_post_message(user_list)

    # スレッド内のユーザーの返信に、スレッドの外で反応すると会話の流れがわかりにくいため
    message.send(
        post_message,
        thread_ts=message.body['thread_ts'] if 'thread_ts' in message.body else None,
    )


def _is_bot_message(message):
    """ボットからのメッセージかを判定する"""
    hubot_flag = ('subtype' in message.body) and (message.body['subtype'] == 'bot_message')
    auto_reply_flag = ('subtype' in message.body) and (message.body['subtype'] == 'channel_join')
    slack_bot_flag = 'bot_id' in message.body

    result = any((hubot_flag, auto_reply_flag, slack_bot_flag))

    print(f'is bot message: {result}')
    return result


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
    random.shuffle(text_list)
    return text_list[:user_num]


def _extract_users(message):
    """メッセージからメンションするためのユーザーのリストを抽出する"""

    # TODO:メンションされたユーザーが重複する場合に返答は1回にするかを検討する
    user_list = _EXTRACT_USER_PATTERN.findall(message)
    print('user_list:', user_list)

    return user_list


def _get_post_message(user_list):
    """ユーザーをほめるメッセージを生成する"""

    text_list = _create_random_element_list('resources/responce_messages.csv', len(user_list))
    stamp_list = _create_random_element_list('resources/responce_stamps.csv', len(user_list))
    post_messages = [f'{u} {t}{s}' for u, t, s in zip(user_list, text_list, stamp_list)]

    return '\n'.join(post_messages)
