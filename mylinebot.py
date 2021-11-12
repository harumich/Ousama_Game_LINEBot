import os
import boto3
import decimal
import json
import gamelist

from pprint import pprint

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import LineBotApiError

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerMessage
)


handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))

dynamodb = boto3.resource('dynamodb')



def lambda_handler(event, context):
    headers = event["headers"]
    body = event["body"]

    # get X-Line-Signature header value
    signature = headers['x-line-signature']

    # handle webhook body
    handler.handle(body, signature)

    return {"statusCode": 200, "body": "OK"}


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    texts = event.message.text
    
    #userIdを検索→①該当なしなら表示名とgruopIdとUserIdをDynamoに登録②該当ありならメッセージ表記して終了
    if texts == '参加':
       profile = line_bot_api.get_profile(event.source.user_id)
       summary = line_bot_api.get_group_summary(event.source.group_id)
       line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=profile.display_name + 'さん、参戦!'+summary.group_id))

       def put_userinfo(user_id, display_name, group_id, dynamodb=None):
          if not dynamodb:
              dynamodb = boto3.resource('dynamodb', endpoint_url="https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/${ServerlessRestApi.Stage}/api_endpoint")

          table = dynamodb.Table('user_info_kinggame')
          response = table.put_item(
             Item={
                  'user_id': user_id,
                  'display_name': display_name,
                  'group_id': group_id
             }
          )
          return response


       if __name__ == '__main__':
            userinfo_resp = put_userinfo(profile.user_id, profile.display_name,
                           summary.group_id)
            print("Put UserId succeeded:")
            pprint(userinfo_resp, sort_dicts=False)
    
    #userIdを検索→①該当なしならメッセージ表記して終了②該当ありなら表示名とgruopIdとUserIdをDynamoから削除
    elif texts == '退出':
        profile = line_bot_api.get_profile(event.source.user_id)
        summary = line_bot_api.get_group_summary(event.source.group_id)
        line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text=profile.display_name + 'さんがゲーム終了しました'))
    
    #groupIdを検索→①該当者がいればリストを表示②該当がいなければメッセ―ジを表示
    elif texts == 'メンバー' :
        summary = line_bot_api.get_group_summary(event.source.group_id)
        line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text='はるみち\n碓井綾音'))
    
    else:
        line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text='特定の文字を送ってくれ！\n・「参加」でゲーム参加\n・「退出」でゲーム退出\n・「メンバー」で参加者確認\n・スタンプでゲーム実行\nできるんだ。\nさぁ、始めようぞ！'))

    # なんでランダムしないんだ
    
    
def operation_put(partitionKey, sortKey):
    putResponse = table.put_item(	
        Item={	
            'user_id': partitionKey,
            'display_name': sortKey
        }
    )

@handler.add(MessageEvent, message=StickerMessage)
def handle_Sticker_message(event):
    # メッセージを決める
    message = gamelist.game
    # 返答を送信する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message))

