import sqlite3
from datetime import datetime
from fastapi import FastAPI
import subprocess
import re
import threading
import time
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()


templates = Jinja2Templates(directory="templates")

@app.get("/graph", response_class=HTMLResponse)
def show_graph(request: Request):
    return templates.TemplateResponse("graph.html", {"request": request})


# データベース初期化
def init_db():
    conn = sqlite3.connect("ping_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ping_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT,
            average_rtt INTEGER,
            packet_loss INTEGER,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


#ルート確認用
@app.get("/")
def read_root():
    return {"message": "Network Monitor Running"}
    



#ping実行

@app.get("/ping")
def ping_test(host: str):
    result = subprocess.run(
        ["ping", host, "-n", "4"],
        capture_output=True,
        text=True
    )
    output = result.stdout

    # 平均RTT抽出（日本語Windows対応）
    avg_match = re.search(r"平均 = (\d+)ms", output)
    if avg_match:
        avg_rtt = int(avg_match.group(1))
    else:
        avg_rtt = None

    # ロス率抽出（日本語Windows対応）
    loss_match = re.search(r"\((\d+)% の損失\)", output)
    if loss_match:
        packet_loss = int(loss_match.group(1))
    else:
        packet_loss = None

    # データベースに保存
    conn = sqlite3.connect("ping_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ping_results (host, average_rtt, packet_loss, timestamp)
        VALUES (?, ?, ?, ?)
    """, (host, avg_rtt, packet_loss, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return {
        "host": host,
        "average_rtt_ms": avg_rtt,
        "packet_loss_percent": packet_loss
    }

#履歴取得
@app.get("/history")
def get_history(host: str):
    conn = sqlite3.connect("ping_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT average_rtt, packet_loss, timestamp
        FROM ping_results
        WHERE host = ?
        AND date(timestamp) = date('now','localtime')
        ORDER BY timestamp
    """, (host,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "average_rtt": row[0],
            "packet_loss": row[1],
            "timestamp": row[2]
        }
        for row in rows
    ]

def monitor_host(host):
    while True:
        try:
            result = subprocess.run(
                ["ping", host, "-n", "4"],
                capture_output=True,
                text=True
            )

            output = result.stdout

            # 平均RTT
            avg_match = re.search(r"平均 = (\d+)ms", output)
            avg_rtt = int(avg_match.group(1)) if avg_match else None

            # パケットロス
            loss_match = re.search(r"\((\d+)% の損失\)", output)
            packet_loss = int(loss_match.group(1)) if loss_match else None

            # DB保存
            conn = sqlite3.connect("ping_history.db", check_same_thread=False)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO ping_results (host, average_rtt, packet_loss, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                host,
                avg_rtt,
                packet_loss,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(e)

        time.sleep(1)

@app.on_event("startup")
def start_monitor():
    hosts = ["google.com", "yahoo.co.jp"]

    for host in hosts:
        thread = threading.Thread(target=monitor_host, args=(host,))
        thread.daemon = True
        thread.start()

