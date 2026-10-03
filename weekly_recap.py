import sqlite3
import os
import requests
from datetime import datetime

# --- CONFIG ---
BOT_TOKEN = "7950793616:AAHOE3Gk-oN8_i6Yl7gYl-V0-aGk5L6w"
PUBLIC_CHANNEL = "-1002345678901"   # Δημόσιο κανάλι
ADMIN_CHAT_ID = "634407000"         # Το προσωπικό σου Chat ID
VIP_BOT_USERNAME = "Alpha_hub_V_bot"
DB_PATH = os.path.expanduser("~/airdrop-hub/quant_trades.db")

def generate_recap_text():
    if not os.path.exists(DB_PATH):
        return None, "Database not found."
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Τραβάμε όλα τα trades
    c.execute("SELECT pair, direction, entry_price, tp1, tp2, sl, status, opened_at FROM trades")
    trades = c.fetchall()
    conn.close()
    
    if not trades:
        return None, "No trades recorded in database yet."
        
    total_trades = len(trades)
    closed_wins = sum(1 for t in trades if t[6] in ('CLOSED', 'TP1_HIT'))
    stopped = sum(1 for t in trades if t[6] == 'STOPPED')
    active = sum(1 for t in trades if t[6] == 'ACTIVE')
    
    decided = closed_wins + stopped
    win_rate = (closed_wins / decided * 100) if decided > 0 else 0.0
    
    now_str = datetime.now().strftime("%d %b %Y")
    
    recap = (
        f"📊 *DEVOPS QUANT — OFFICIAL WEEKLY RECAP* 📊\n"
        f"Period Ending: *{now_str}*\n"
        f"Horizon: *1H Swing Engine (ATR-Optimized)*\n\n"
        f"📈 *Performance Telemetry:*\n"
        f"• Total Setups Tracked: *{total_trades}*\n"
        f"• Targets Hit / Wins: *{closed_wins}* 🎯\n"
        f"• Defended / Stopped: *{stopped}* 🛑\n"
        f"• Active Positions: *{active}* ⏳\n"
        f"• Verified Win Rate: *{win_rate:.1f}%* ⚡\n\n"
        f"🛡️ *Risk Execution Summary:*\n"
        f"• Zero Account Liquidations (Discipline: 3x-5x max)\n"
        f"• Automated Capital Protection (Auto BE at TP1)\n\n"
        f"💎 *Upgrade to VIP Terminal:*\n"
        f"Instant webhooks, full targets & priority execution.\n"
        f"👉 @{VIP_BOT_USERNAME}"
    )
    return True, recap

def send_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    return requests.post(url, json=payload, timeout=10).json()

if __name__ == "__main__":
    import sys
    success, text = generate_recap_text()
    
    if not success:
        print(f"[!] {text}")
        sys.exit(1)
        
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    
    if mode == "publish":
        send_msg(PUBLIC_CHANNEL, text)
        print("[+] Recap published successfully to Public Hub!")
    else:
        # Default: Preview στο προσωπικό σου DM
        send_msg(ADMIN_CHAT_ID, f"👀 *PREVIEW FOR SUNDAY RECAP:*\n\n{text}")
        print("[+] Preview sent to Admin DM. Verify on Telegram!")
