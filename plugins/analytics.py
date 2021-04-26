import datetime
import os
import re
from datetime import timedelta

import pandas as pd
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

'''
TODO
1. 投稿を取得し、最もリアクションの多い投稿を再投稿する機能を実装する。(analytics.py)
    1.投稿を取得する機能をつくる
    2.投稿を集計する機能をつくる
    3.リアクションが最も多い投稿を取得する
    4.リアクションが最も多い投稿を投稿する
2. 1週間に一度analytics.pyを実行する。
'''


def main():
    load_dotenv()
    d = datetime.datetime.now() - timedelta(days=7)
    client = WebClient(token=os.environ.get('SLACK_TOKEN'))
    conversation_history = []
    channel_id = os.environ['CHANNEL_ID']

    try:
        result = client.conversations_history(
            channel=channel_id, oldest=d.timestamp(), limit=100000
        )

        conversation_history = result['messages']

        print('{} messages found in {}'.format(len(conversation_history), id))

        conversation_history = [
            {'ts': i['ts'], 'text': i['text'], 'reactions': i['reactions'], 'user': i['user']}
            for i in conversation_history
            if 'reactions' in i.keys()
        ]

        for i in conversation_history:
            cnt = 0
            for s in i['reactions']:
                cnt += s['count']
            i['reactions'] = cnt

        conversation_history = pd.DataFrame(conversation_history)

        df_best_comments = conversation_history[
            conversation_history.reactions == conversation_history.reactions.max()
        ].reset_index()

        chat = None

        for idx, row in df_best_comments.iterrows():
            client = WebClient(token=os.environ.get('SLACK_TOKEN'))

            chat = client.chat_getPermalink(
                token=os.environ.get('SLACK_TOKEN'),
                channel=channel_id,
                message_ts=row['ts'],  # type: ignore
            )

            m = re.compile(r'<@.*>')
            text_list = re.split(r'[\xa0| |,|;]', row['text'])  # type: ignore
            homember_list = [m.match(name).group() for name in text_list]  # if m.match(name) !=

            if idx == 0:
                client.chat_postMessage(
                    channel=channel_id,
                    text='先週もようがんばったな:kissing_cat:ノビルくんの弟からウィークリーレポートのお知らせやで～\n'
                    + '先週みんなが送ってくれた「褒め言葉」の中で、一番多くのスタンプを集めたウィークリーベスト褒めエピソードはこれや！:cv2_res_pect:\n',
                )

            client.chat_postMessage(
                channel=channel_id,
                text=f'最もリアクションの多かった褒めをした人：<@{row["user"]}>\n'
                + f'最も褒められたメンバー：{", ".join(homember_list)}\n'
                + f'{chat["permalink"]}\n',
            )

            client.chat_postMessage(channel=channel_id, text=f'{chat["permalink"]}\n')

        client.chat_postMessage(channel=channel_id, text='今週もぎょうさん褒めに褒めまくって、伸ばし合っていこか！')

    except SlackApiError as e:
        print('Error creating conversation: {}'.format(e))


if __name__ == '__main__':
    main()
