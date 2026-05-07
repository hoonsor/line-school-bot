#!/bin/bash
echo "🚀 啟動 LINE Bot 學校行政系統..."
echo "🔗 啟動 ngrok..."
ngrok http 5000 --log=ngrok.log &
sleep 3
NGROK_URL=$(grep -o 'https://[^ ]*\.ngrok\.io' ngrok.log 2>/dev/null | head -1)
if [ -n "$NGROK_URL" ]; then
    echo "✅ Webhook URL: ${NGROK_URL}/callback"
fi
echo "🖥️ 啟動 Flask..."
python app.py