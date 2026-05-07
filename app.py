"""
LINE Bot 學校行政通知系統 - Flask 後端
功能：行事曆查詢、請假申請、公文提醒
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, FlexMessage,
    FlexBubble, FlexBox, FlexText, FlexButton,
    URIAction, MessageAction
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent,
    FollowEvent, PostbackEvent
)

from school_data import (
    get_calendar_events,
    get_leave_balance,
    format_leave_request_form,
    get_documents,
    get_welcome_message,
    format_calendar_flex,
    format_document_flex
)

app = Flask(__name__)

# LINE Bot 設定
channel_secret = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/")
def index():
    return "LINE Bot 學校行政系統運行中！"


@app.route("/callback", methods=['POST'])
def callback():
    """LINE Webhook 回调端点"""
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
    """處理文字訊息"""
    if isinstance(event.message, TextMessageContent):
        text = event.message.text.strip()
        
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            
            # 關鍵字路由
            if text in ['行事曆', '校曆', '行事曆查詢']:
                events = get_calendar_events(limit=5)
                flex = format_calendar_flex(events)
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[FlexMessage(alt_text='近期活動', content=flex)]
                    )
                )
            
            elif text in ['請假', '请假', '請假申請']:
                leave_info = get_leave_balance()
                form = format_leave_request_form()
                messages = [
                    TextMessage(text=leave_info),
                    FlexMessage(alt_text='請假申請表', content=form)
                ]
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=messages
                    )
                )
            
            elif text in ['公文', '公文查詢', '收文']:
                docs = get_documents(limit=5)
                flex = format_document_flex(docs)
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[FlexMessage(alt_text='公文列表', content=flex)]
                    )
                )
            
            elif text in ['help', '幫助', '功能', '使用說明']:
                welcome = get_welcome_message()
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=welcome)]
                    )
                )
            
            else:
                # 預設回應
                help_text = (
                    "📋 我是學校行政機器人！\n\n"
                    "請輸入以下指令：\n"
                    "📅 「行事曆」- 查看近期活動\n"
                    "🏖️ 「請假」- 請假申請\n"
                    "📄 「公文」- 公文查詢\n"
                    "❓ 「help」- 顯示說明"
                )
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=help_text)]
                    )
                )


@handler.add(FollowEvent)
def on_follow(event):
    """新朋友加入"""
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        welcome = get_welcome_message()
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=welcome)]
            )
        )


@handler.add(PostbackEvent)
def handle_postback(event):
    """處理按鈕回調"""
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        
        postback_data = event.postback.data
        
        if postback_data == 'leave_form':
            form = format_leave_request_form()
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text='請假申請表', content=form)]
                )
            )
        elif postback_data == 'view_calendar':
            events = get_calendar_events(limit=10)
            flex = format_calendar_flex(events)
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text='完整行事曆', content=flex)]
                )
            )
        elif postback_data == 'view_documents':
            docs = get_documents(limit=10)
            flex = format_document_flex(docs)
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text='公文列表', content=flex)]
                )
            )


@app.route("/push", methods=['POST'])
def push_notification():
    """
    主動推播通知（範例）
    可由 Cron Job 或外部系統觸發
    """
    notification_type = request.json.get('type', 'reminder')
    
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        
        if notification_type == 'leave_reminder':
            message = TextMessage(text="📌 提醒：您有待核假的請假單，請記得處理！")
        elif notification_type == 'doc_arrival':
            message = TextMessage(text="📬 新公文到達，請及時處理！")
        else:
            message = TextMessage(text="📢 學校通知：請留意相關公告。")
        
        # 這裡需要指定 User ID，實際使用时从数据库获取
        # messaging_api.push_message(push_request={
        #     'to': 'USER_ID',
        #     'messages': [message]
        # })
        
    return {'status': 'ok'}


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)