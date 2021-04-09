import datetime
import os
import sys
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def hoge():
    load_dotenv()
    print(os.environ)
    print(os.environ.get('SLACK_TOKEN'))
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
        result = client.conversations_history(channel=channel_id)

        conversation_history = result["messages"]

        # Print results
        print("{} messages found in {}".format(len(conversation_history), id))
        print(conversation_history)

    except SlackApiError as e:
        print("Error creating conversation: {}".format(e))


# token = os.environ.get('SLACK_TOKEN')
# headers = {"Content-type": "application/json", "Authorization": f"Bearer {token}"}


#  def fetch_messages_by_channel(channel_id):
#     oldest_ts = None
#     one_year_ago = pd.to_datetime('2021-04-04')
#     endpoint = 'https://slack.com/api/channels.history'

#     ls_messages = []
#     while True:
#         payload = {'channel': channel_id, 'latest': oldest_ts, 'count': 1000}

#         data = requests.get(endpoint, headers=headers, params=payload).json()
#         print(data)
#         messages = data['messages']
#         ls_messages.extend(messages)

#         if data['has_more']:
#             time.sleep(1)
#             oldest_ts = messages[-1]['ts']
#             oldest_datetime = pd.to_datetime(oldest_ts, unit='s')
#             sys.stdout.write(f"\r{oldest_datetime}")
#             sys.stdout.flush()
#             if oldest_datetime < one_year_ago:
#                 sys.stdout.write(f"\rfinish!" + ' ' * 50)
#                 break
#         else:
#             break
#     df = pd.DataFrame(ls_messages)
#     df['channel_id'] = channel_id
#     return df


# def main():
#     print(fetch_messages_by_channel('C01SGT4J2AC'))


if __name__ == '__main__':
    print(os.environ)
    # hoge()
