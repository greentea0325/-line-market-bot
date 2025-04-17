
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import market_indicator_fetcher

app = Flask(__name__)

# ⚠️ 請自行填入你的 Channel Access Token 與 Secret
line_bot_api = LineBotApi("YOUR_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler("YOUR_CHANNEL_SECRET")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.lower()

    if any(keyword in text for keyword in ["市場", "today", "大盤", "指數"]):
        sp500, nasdaq, vix, dxy, tnx = market_indicator_fetcher.fetch_market_indicators_v22()
        market_info = (
            "📊 今日市場概況：\n"
            f"{sp500}\n{nasdaq}\n{vix}\n{dxy}\n{tnx}"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=market_info))
    else:
        reply = "請輸入「市場」、「大盤」或「today」來查詢今日市場概況 📊"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run()
