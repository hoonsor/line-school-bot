"""
學校行政資料模組
包含行事曆、請假、公文等資料管理
使用 SQLite 儲存實際資料
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), 'school.db')


def init_db():
    """初始化資料庫"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_date TEXT NOT NULL,
            event_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_number TEXT NOT NULL,
            title TEXT NOT NULL,
            doc_type TEXT,
            arrival_date TEXT NOT NULL,
            deadline TEXT,
            status TEXT DEFAULT 'unread',
            content TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def get_calendar_events(limit: int = 10, event_type: str = None) -> List[Dict]:
    """取得近期行事曆"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    if event_type:
        cursor.execute(
            '''SELECT * FROM calendar_events 
               WHERE event_date >= ? AND event_type = ?
               ORDER BY event_date ASC LIMIT ?''',
            (today, event_type, limit)
        )
    else:
        cursor.execute(
            '''SELECT * FROM calendar_events 
               WHERE event_date >= ? 
               ORDER BY event_date ASC LIMIT ?''',
            (today, limit)
        )
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_leave_balance(user_id: str = 'default_user') -> str:
    return (
        "🏖️ 您的請假餘額：\n"
        "・特休假：14 天（已用 3 天）\n"
        "・病假：30 天（已用 1 天）\n"
        "・事假：14 天（已用 2 天）\n\n"
        "📝 如要申請請假，請回覆「請假」填寫申請表。"
    )


def format_leave_request_form():
    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [{"type": "text", "text": "📝 請假申請表", "weight": "bold", "size": "lg", "color": "#FFFFFF"}],
            "backgroundColor": "#007BFF"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "請選擇請假類型：", "weight": "bold", "margin": "md"},
                {
                    "type": "box", "layout": "horizontal", "margin": "md", "contents": [
                        {"type": "button", "style": "primary", "action": {"type": "postback", "label": "特休假", "data": "leave_type=special"}},
                        {"type": "button", "style": "secondary", "action": {"type": "postback", "label": "病假", "data": "leave_type=sick"}},
                        {"type": "button", "style": "secondary", "action": {"type": "postback", "label": "事假", "data": "leave_type=personal"}}
                    ]
                },
                {"type": "text", "text": "請假流程說明：\n1. 填寫起始與結束日期\n2. 填寫請假原因\n3. 提交後等待主管核可", "margin": "md", "wrap": True}
            ]
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{"type": "button", "action": {"type": "uri", "label": "📋 查看完整假單", "uri": "https://example.com/leave"}}]
        }
    }


def get_documents(limit: int = 10, status: str = None) -> List[Dict]:
    """取得公文列表"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status:
        cursor.execute('SELECT * FROM documents WHERE status = ? ORDER BY arrival_date DESC LIMIT ?', (status, limit))
    else:
        cursor.execute('SELECT * FROM documents ORDER BY arrival_date DESC LIMIT ?', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def format_document_flex(docs: List[Dict]) -> Dict:
    contents = []
    for doc in docs:
        status_emoji = "✅" if doc.get('status') == 'read' else "📌"
        deadline = doc.get('deadline', '無期限')
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{status_emoji} {doc.get('doc_number', 'N/A')}", "weight": "bold", "size": "sm", "color": "#666666"},
                    {"type": "text", "text": doc.get('title', '無標題'), "weight": "bold", "size": "md", "wrap": True, "margin": "sm"},
                    {"type": "text", "text": f"類型：{doc.get('doc_type', '一般')}", "size": "sm", "color": "#888888", "margin": "sm"},
                    {"type": "text", "text": f"到達：{doc.get('arrival_date', 'N/A')}", "size": "sm", "color": "#888888"},
                    {"type": "text", "text": f"期限：{deadline}", "size": "sm", "color": "#FF6600" if deadline != '無期限' else "#888888"}
                ]
            }
        }
        contents.append(bubble)
    
    return {
        "type": "carousel",
        "contents": contents if contents else [{"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "📭 目前沒有公文"}]}}]
    }


def format_calendar_flex(events: List[Dict]) -> Dict:
    contents = []
    for event in events:
        emoji = {'holiday': '🎉', 'meeting': '📌', 'exam': '📝', 'activity': '🎪', 'general': '📅'}.get(event.get('event_type', 'general'), '📅')
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{emoji} {event.get('title', '無標題')}", "weight": "bold", "size": "md", "wrap": True},
                    {"type": "text", "text": f"📆 日期：{event.get('event_date', 'N/A')}", "size": "sm", "color": "#666666", "margin": "sm"},
                    {"type": "text", "text": f"📝 {event.get('description', '無說明')}", "size": "sm", "color": "#888888", "wrap": True}
                ]
            }
        }
        contents.append(bubble)
    
    return {
        "type": "carousel",
        "contents": contents if contents else [{"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "📅 目前沒有即將到來的活動"}]}}]
    }


def get_welcome_message() -> str:
    return (
        "👋 您好！歡迎使用【學校行政LINE Bot】！\n\n"
        "📅 【行事曆】- 查詢學校近期活動\n"
        "🏖️ 【請假】- 教師請假申請\n"
        "📄 【公文】- 公文查詢與追蹤\n\n"
        "請輸入指令或點擊功能按鈕操作。"
    )


def seed_sample_data():
    """初始化範例資料"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM calendar_events')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    today = datetime.now()
    events = [
        ('校慶運動會', (today + timedelta(days=5)).strftime('%Y-%m-%d'), '年度校慶活動，歡迎參加', 'activity'),
        ('教務會議', (today + timedelta(days=7)).strftime('%Y-%m-%d'), '學期檢討與改進事項', 'meeting'),
        ('期末考試週', (today + timedelta(days=14)).strftime('%Y-%m-%d'), '為期一週的期末考試', 'exam'),
        ('春節連假', (today + timedelta(days=21)).strftime('%Y-%m-%d'), '春節假期', 'holiday'),
    ]
    for title, date, desc, etype in events:
        cursor.execute('INSERT INTO calendar_events (title, event_date, description, event_type) VALUES (?, ?, ?, ?)', (title, date, desc, etype))
    
    docs = [
        ('教育111001', '111學年度第2學期行事曆', '行政', today.strftime('%Y-%m-%d'), (today + timedelta(days=14)).strftime('%Y-%m-%d')),
        ('人資111002', '教師考核辦法修正草案', '人事', (today - timedelta(days=2)).strftime('%Y-%m-%d'), None),
        ('教務111003', '期中考試實施細則', '教務', (today - timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=7)).strftime('%Y-%m-%d')),
    ]
    for doc_num, title, dtype, arrival, deadline in docs:
        cursor.execute('INSERT INTO documents (doc_number, title, doc_type, arrival_date, deadline) VALUES (?, ?, ?, ?, ?)', (doc_num, title, dtype, arrival, deadline))
    
    conn.commit()
    conn.close()
    print("✅ 範例資料已初始化")


init_db()
seed_sample_data()