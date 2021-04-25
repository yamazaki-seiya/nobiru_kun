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
    # print(os.environ)
    # print(os.environ.get('SLACK_TOKEN'))
    d = datetime.datetime.now() - timedelta(days=7)
    print(d)
    client = WebClient(token=os.environ.get('SLACK_TOKEN'))

    # Store conversation history
    conversation_history = []
    # ID of the channel you want to send the message to
    # channel_id = os.environ.get('CHANNEL_ID')
    channel_id = os.environ['CHANNEL_ID']

    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination # noqa: E501

        result = client.conversations_history(
            channel=channel_id, oldest=d.timestamp(), limit=100000
        )

        conversation_history = result['messages']

        # Print results
        print('{} messages found in {}'.format(len(conversation_history), id))

        conversation_history = [
            {'ts': i['ts'], 'text': i['text'], 'reactions': i['reactions'], 'user': i['user']}
            for i in conversation_history
            if 'reactions' in i.keys()
        ]

        # print(conversation_history)

        for i in conversation_history:
            cnt = 0
            for s in i['reactions']:
                cnt += s['count']
            i['reactions'] = cnt

        conversation_history = pd.DataFrame(conversation_history)

        df_best_comments = conversation_history[
            conversation_history.reactions == conversation_history.reactions.max()
        ].reset_index()
        # print(df_best_comments)

        for idx, r in df_best_comments.iterrows():
            client = WebClient(token=os.environ.get('SLACK_TOKEN'))

            chat = client.chat_getPermalink(
                token=os.environ.get('SLACK_TOKEN'),
                channel=channel_id,
                message_ts=r['ts'],
            )
            # print(idx)
            # print(r['text'])

            m = re.compile(r'<@.*>')
            # コピペした場合は' ',スラックでメンションを連続して入力する場合には'\xa0'が引っかかる
            text_list = re.split('[\xa0| |,|;]', r['text'])
            # print(text_list)

            homember_list = [m.match(name).group() for name in text_list]  # if m.match(name) !=
            # print(homember_list)

            if idx == 0:
                response = client.chat_postMessage(
                    channel=chat['channel'],
                    text='先週もようがんばったな:kissing_cat:ノビルくんの弟からウィークリーレポートのお知らせやで～\n'
                    + '先週みんなが送ってくれた「褒め言葉」の中で、一番多くのスタンプを集めたウィークリーベスト褒めエピソードはこれや！:cv2_res_pect:\n',
                )

            response = client.chat_postMessage(
                channel=chat['channel'],
                text=f'最もリアクションの多かった褒めをした人：<@{r["user"]}>\n'
                + f'最も褒められたメンバー：{", ".join(homember_list)}\n',
            )

            response = client.chat_postMessage(
                channel=chat['channel'], text=f'{chat["permalink"]}\n'
            )

        response = client.chat_postMessage(  # noqa: F841
            channel=chat['channel'], text='今週もぎょうさん褒めに褒めまくって、伸ばし合っていこか！'
        )

    except SlackApiError as e:
        print('Error creating conversation: {}'.format(e))


if __name__ == '__main__':
    main()
    # print(chat)
