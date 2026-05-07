# LINE Bot 學校行政通知系統

LINE Messaging API 整合的學校行政通知機器人。

## 功能
- 📅 行事曆查詢
- 🏖️ 請假申請
- 📄 公文管理
- 🔔 主動推播

## 設定
1. 建立 LINE Bot（LINE Developers Console）
2. 取得 Channel Secret 與 Access Token
3. 設定環境變數：
   ```env
   LINE_CHANNEL_SECRET=your_secret
   LINE_ACCESS_TOKEN=your_token
   PORT=5000
   ```
4. 啟動 ngrok：`ngrok http 5000`
5. 在 LINE Console 設定 Webhook URL

## 指令
| 指令 | 功能 |
|------|------|
| 行事曆 | 查看近期活動 |
| 請假 | 請假申請 |
| 公文 | 公文列表 |
| help | 說明 |

## 啟動
```bash
pip install -r requirements.txt
python app.py
```