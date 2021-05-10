import csv
import math
import random
import re

from slackbot.bot import listen_to

# 複数のユーザーIDが1つの文字列に含まれる場合に、1ユーザーIDずつ分けて抽出するため
_EXTRACT_USER_PATTERN = re.compile(r'<@[a-zA-Z_0-9]{1,}>')

# メンションされたユーザーを抽出するための正規表現パターン
# メンションユーザーの区切り文字としては現状以下のパターンが大多数を占めるが他の文字も考慮した
#   - 半角スペース、'\xa0'（ノーブレークスペース）
#
# 投稿メッセージ例: @user1 @user2,@user3;@user4 messages
_MENTION_SPLIT_PATTERN = re.compile(r'[\xa0| |,|;]')


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
    return ('subtype' in message.body) and (message.body['subtype'] == 'bot_message')


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
    random.shuffle(text_list)
    return text_list[:user_num]


def _extract_users(message):
    """メッセージからメンションするためのユーザーのリストを抽出する"""
    splitted_message = re.split(_MENTION_SPLIT_PATTERN, message)
    print(f'splitted_message:{splitted_message}')

    # TODO:メンションされたユーザーが重複する場合に返答は1回にするかを検討する
    user_list = []
    for words in splitted_message:
        print('words:', words)
        # メンションユーザーの文字列にマッチする文字列を全て取得するため
        menttioned_user_list = _EXTRACT_USER_PATTERN.findall(words)
        print('menttioned_user_list:', menttioned_user_list)
        for menttioned_user in menttioned_user_list:
            user_list.append(menttioned_user)
    print('user_list:', user_list)
    return user_list


def _get_post_message(user_list):
    """ユーザーをほめるメッセージを生成する"""

    text_list = _create_random_element_list('resources/responce_messages.csv', len(user_list))
    stamp_list = _create_random_element_list('resources/responce_stamps.csv', len(user_list))
    post_messages = [f'{u} {t}{s}' for u, t, s in zip(user_list, text_list, stamp_list)]

    return '\n'.join(post_messages)
