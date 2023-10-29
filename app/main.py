import os
import re
import json
import logging
import requests
from pydantic import BaseModel
from typing import Literal
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

# SLACK_BOT_TOKEN=xoxb-529919538064-5922207341377-NO4chFrdjNC32QLBUNQIEaBf
# SLACK_APP_TOKEN=xapp-1-A05SB0TB4ET-5922216609617-902b077bef5421b1587a31bec9f8297d8f408cc33dd4151b68845286b1d6d67d
# SLACK_SIGNING_SECRET=b3774499ab6b13bd7be12d3fb841be69
# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    process_before_response=True,
)

logging.basicConfig(level=logging.DEBUG)

# https://api.slack.com/events/app_mention


class WfParser(BaseModel):
    """messageをparseするクラス
    """
    userName: str = None
    firstName: str = None
    lastName: str = None
    email: str = None
    group: str = Literal["enginner", "sales", "market", "cooporate"]

    # メッセージをパースして、userNameなどに代入する
    def run(self, message):
        message_l = message.splitlines()
        print("メッセージをパースする")

        # slack上で自動的にmaill形式がformatされる
        match = re.search(r'<mailto:(.*?)\|', message_l[3])
        if match:
            self.userName = match.group(1)
        if re.match('([a-z]+)', message_l[5]):
            self.firstName = message_l[5]
        if re.match('([a-z]+)', message_l[7]):
            self.lastName = message_l[5]
        match = re.search(r'<mailto:(.*?)\|', message_l[9])
        if match:
            self.email = match.group(1)
        self.group = message_l[11]

# workflowの設定に従って、okta userを作成する


# class OktaClients(BaseModel):
#     """paramsを受け取って、oktaのAPIをcallするclass
#     """

#     api_endpoint: [str, str] = {
#         "create_user": "http:xxxxx",
#         "delete_user": "http:xxx",
#         "update_user": "http:xxx"
#     }

#     def __init__(self):
#         print("AAA")

#     def _call_okta_workflow(self, api_endpoint: str, params: [str, str]):
#         headers = {'Authorization': 'Bearer {}'.format("okta_access_token")}
#         # boolでokという変数を持って、returnした方がわかりやすいかも
#         try:
#             resp = requests.post(api_endpoint, headers=headers, json=params)
#             print("無事にoktaのworkflowをcallできたであります: %s", resp)
#             return True
#         except Exception as err:
#             print("なんかミスったようであります: %s", err)
#             return False

#     def create_user(self, user_info):
#         # debug
#         # print(user_info.userName)
#         # print(user_info.firstName)

#         params = {
#             "userName": user_info.userName,
#             "firstName": user_info.firstName,
#             "lastName": user_info.lastName,
#             "email": user_info.email,
#             "group": user_info.group
#         }

#         self._call_okta_workflow(self.api_endpoint["create_user"], params)

#     def delete_user(user_info):
#         print(user_info.userName)
#         print(user_info.firstName)

#     def update_user(user_info):
#         print(user_info.userName)
#         print(user_info.firstName)

@app.message("hello")
def message_hello(message, say):
    say(f"Hey there!")


@app.event("message")
def handler_message_events(body, logger):
    logger.info(body)


@app.event("app_mention")
def mention_handler(body, say):
    message = body["event"]["text"]
    channel = body["event"]["channel"]
    thread_ts = body["event"]["ts"]

    say(text=message, thread_ts=thread_ts)
    user_info = WfParser()
    user_info.run(message)

    print(user_info.userName)
    print(user_info.lastName)
    print(user_info.group)

    # oc = OktaClients()

    # if message == "help":
    #     say(f"ヘルプだよ", channel=channel, thread_ts=thread_ts)
    # elif message in "oktaアカウント発行":
    #     oc.create_user(user_info)
    #     say(f"okta アカウントを作成します", channel=channel, thread_ts=thread_ts)

    # else:
    #     say(f"コマンドミスってるっす", channel=channel, thread_ts=thread_ts)


# ロギングを AWS Lambda 向けに初期化します
# see: https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

## test変更変更変更変更変更!!!!!!!!!!

def lambda_handler(event, context):
    slack_handler = SlackRequestHandler(app=app)

    # slackのchallenge認証対応
    if 'challenge' in event:
        return event['challenge']

    return slack_handler.handle(event, context)
