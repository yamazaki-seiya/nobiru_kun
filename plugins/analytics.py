import datetime
import os
import re
from datetime import timedelta

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def main():
    """実行日から過去7日間の投稿を取得し最もリアクションの多かった投稿を表彰する"""
    oldest_day = datetime.datetime.now() - timedelta(days=7)
    slack_token = os.environ.get('SLACK_TOKEN')
    channel_id = os.environ['CHANNEL_ID']
    client = WebClient(token=slack_token)
    conversation_history = []

    try:
        # コードの実行日から7日前までの投稿を取得, リアクションの総数を集計する
        result = client.conversations_history(
            channel=channel_id, oldest=oldest_day.timestamp(), limit=100000
        )

        conversation_history = result['messages']
        print(f'{len(conversation_history)} messages found')

        conversation_history = [
            {'ts': d['ts'], 'text': d['text'], 'reactions': d['reactions'], 'user': d['user']}
            for d in conversation_history
            if 'reactions' in d.keys()
        ]

        for d in conversation_history:
            cnt = 0
            for s in d['reactions']:
                cnt += s['count']
            d['reactions'] = cnt

        # リアクションの総数が最も多かった投稿を取得
        max_reaction_cnt = max([d.get('reactions') for d in conversation_history])
        best_comments_lst = [d for d in conversation_history if d['reactions'] == max_reaction_cnt]

        # リアクションの総数が最も多かった投稿を表彰するポストを投稿
        chat = None
        for cnt, best_comment in enumerate(best_comments_lst):
            print(cnt, best_comment)
            chat = client.chat_getPermalink(
                token=slack_token,
                channel=channel_id,
                message_ts=best_comment['ts'],  # type: ignore
            )

            m = re.compile(r'<@.*>')
            text_list = re.split(r'[\xa0| |,|;]', best_comment['text'])  # type: ignore

            homember_list = [
                m.match(name).group() for name in text_list if m.match(name) is not None
            ]

            if cnt == 0:
                client.chat_postMessage(
                    channel=channel_id,
                    text='先週もようがんばったな:kissing_cat:ノビルくんの弟からウィークリーレポートのお知らせやで～\n'
                    + '先週みんなが送ってくれた「褒め言葉」の中で、一番多くのスタンプを集めたウィークリーベスト褒めエピソードはこれや！:cv2_res_pect:\n',
                )

            client.chat_postMessage(
                channel=channel_id,
                text=f'最もリアクションの多かった褒めをした人：<@{best_comment["user"]}>\n'
                + f'最も褒められたメンバー：{", ".join(homember_list)}\n'
                + f'{chat["permalink"]}\n',
            )

            client.chat_postMessage(channel=channel_id, text=f'{chat["permalink"]}\n')

        client.chat_postMessage(channel=channel_id, text='今週もぎょうさん褒めに褒めまくって、伸ばし合っていこか！')

    except SlackApiError as e:
        print('Error creating conversation: {}'.format(e))


if __name__ == '__main__':
    main()
