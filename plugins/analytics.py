import datetime
import os
import sys
import time
from datetime import timedelta

import pandas as pd
import requests
import slack_sdk
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import client


def main():
    load_dotenv()
    # print(os.environ)
    # print(os.environ.get('SLACK_TOKEN'))
    d = datetime.date.today() - timedelta(days=7)
    print(d)
    client = WebClient(token=os.environ.get('SLACK_TOKEN'))

    # Store conversation history
    conversation_history = []
    # ID of the channel you want to send the message to
    # channel_id = os.environ.get('CHANNEL_ID')
    channel_id = os.environ.get('CHANNEL_ID')

    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id, oldest=d)

        conversation_history = result["messages"]

        # Print results
        print("{} messages found in {}".format(len(conversation_history), id))

        conversation_history = [
            {'ts': i['ts'], 'text': i['text'], 'reactions': i['reactions']}
            for i in conversation_history
            if 'reactions' in i.keys()
        ]
        for i in conversation_history:
            cnt = 0
            for s in i['reactions']:
                cnt += s['count']
            i['reactions'] = cnt

        return pd.DataFrame(conversation_history)

    except SlackApiError as e:
        print("Error creating conversation: {}".format(e))


if __name__ == '__main__':
    conversation_history = main()
    print(pd.to_datetime(conversation_history['ts'], unit='s'))

    df_best_comments = conversation_history[
        conversation_history.reactions == conversation_history.reactions.max()
    ]
    # print(best_comments)

    best_comments = ''
    for _, i in df_best_comments.iterrows():
        client = WebClient(token=os.environ.get('SLACK_TOKEN'))
        # print(i)
        chat = client.chat_getPermalink(
            token=os.environ.get('SLACK_TOKEN'),
            channel=os.environ.get('CHANNEL_ID'),
            message_ts=i['ts'],
        )
        best_comments = '今週のベスト褒めエピソードはこれや:rose:' + chat['permalink']
        # response = client.chat_postMessage(channel=chat['channel'], text=best_comments)

    print(best_comments)

    # print(chat)
