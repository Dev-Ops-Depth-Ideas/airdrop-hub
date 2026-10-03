import os
import sys
import time
import requests
import sqlite3
from datetime import datetime

# --- CONFIGURATION ---
BOT_TOKEN = "7950793616:AAHOE3Gk-oN8_i6Yl7gYl-V0-aGk5L6w"  # To bot token sou
CHANNEL_ID = "-1002345678901"  # To Channel ID tou Alpha Hunter Hub
VIP_BOT_USERNAME = "Alpha_hub_V_bot"

PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
TIMEFRAME = "1h"
CHECK_INTERVAL_SEC = 180  # Check kathe 3 lepta gia candles

DB_PATH = os.path.expanduser("~/airdrop-hub/quant_trades.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
        pair TEXT PRIMARY KEY,
        direction TEXT,
        entry_price REAL,
        tp1 REAL,
        tp2 REAL,
        sl REAL,
        status TEXT,
        opened_at TEXT,
        last_signal_time REAL
    )''')
    conn.commit()
    conn.close()

def get_klines(symbol, interval="1h", limit=50):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        r = requests.get(url, timeout=10)
        data = r.json()
        closes = [float(k[4]) for k in data]
        highs = [float(k[2]) for k in data]
        lows = [float(k[3]) for k in data]
        return closes, highs, lows
    except Exception as e:
        print(f"Error fetching klines for {symbol}: {e}")
        return [], [], []

def compute_atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return 0.0
    tr_list = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        tr_list.append(tr)
    return sum(tr_list[-period:]) / period

def send_telegram(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram send error: {e}")

def check_and_generate_signals():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for pair in PAIRS:
        closes, highs, lows = get_klines(pair, interval=TIMEFRAME)
        if not closes or len(closes) < 30:
            continue
            
        current_price = closes[-1]
        atr = compute_atr(highs, lows, closes)
        if atr == 0:
            continue
            
        clean_sym = pair.replace("USDT", "")
        c.execute("SELECT direction, entry_price, tp1, tp2, sl, status, last_signal_time FROM trades WHERE pair = ?", (pair,))
        row = c.fetchone()
        
        now_ts = time.time()
        
        # An yparxei idi active setup, elegxoume ta targets
        if row and row[5] == "ACTIVE":
            direction, entry, tp1, tp2, sl, status, last_sig = row
            
            if direction == "LONG":
                if current_price >= tp2:
                    send_telegram(f"🎯 *TARGET 2 HIT — FULL EXIT* 🎯\n\n#{clean_sym} hit *${tp2:,.2f}*! (+{((tp2-entry)/entry)*100:.2f}% clean move)\nSetup closed successfully.")
                    c.execute("UPDATE trades SET status = 'CLOSED' WHERE pair = ?", (pair,))
                elif current_price >= tp1:
                    # Move to Break Even
                    new_sl = entry
                    send_telegram(f"🎯 *TARGET 1 REACHED* 🎯\n\n#{clean_sym} hit *${tp1:,.2f}*!\n🛡️ *Stop Loss moved to BREAK-EVEN* (${new_sl:,.2f}). Risk-free ride to TP2.")
                    c.execute("UPDATE trades SET tp1 = 99999999, sl = ? WHERE pair = ?", (new_sl, pair))
                elif current_price <= sl:
                    send_telegram(f"🛑 *STOP LOSS HIT*\n\n#{clean_sym} closed at *${sl:,.2f}*. Capital protected.")
                    c.execute("UPDATE trades SET status = 'STOPPED' WHERE pair = ?", (pair,))
            
            elif direction == "SHORT":
                if current_price <= tp2:
                    send_telegram(f"🎯 *TARGET 2 HIT — FULL EXIT* 🎯\n\n#{clean_sym} hit *${tp2:,.2f}*! (+{((entry-tp2)/entry)*100:.2f}% clean move)\nSetup closed successfully.")
                    c.execute("UPDATE trades SET status = 'CLOSED' WHERE pair = ?", (pair,))
                elif current_price <= tp1:
                    new_sl = entry
                    send_telegram(f"🎯 *TARGET 1 REACHED* 🎯\n\n#{clean_sym} hit *${tp1:,.2f}*!\n🛡️ *Stop Loss moved to BREAK-EVEN* (${new_sl:,.2f}). Risk-free ride to TP2.")
                    c.execute("UPDATE trades SET tp1 = -1, sl = ? WHERE pair = ?", (new_sl, pair))
                elif current_price >= sl:
                    send_telegram(f"🛑 *STOP LOSS HIT*\n\n#{clean_sym} closed at *${sl:,.2f}*. Capital protected.")
                    c.execute("UPDATE trades SET status = 'STOPPED' WHERE pair = ?", (pair,))
                    
            conn.commit()
            continue

        # Cooldown elegxos: 4 wres (14400 sec) anamesa sta signals
        if row and (now_ts - row[6]) < 14400:
            continue

        # Dynamic EMA Trends
        ema20 = sum(closes[-20:]) / 20
        ema50 = sum(closes[-50:]) / 50
        
        direction = None
        if current_price > ema20 > ema50:
            direction = "LONG"
        elif current_price < ema20 < ema50:
            direction = "SHORT"
            
        if not direction:
            continue

        # Dynamic ATR Targets
        if direction == "LONG":
            sl = current_price - (1.5 * atr)
            tp1 = current_price + (2.0 * atr)
            tp2 = current_price + (3.8 * atr)
            safe_liq = current_price * 0.75  # 25% safety distance
            sugg_lev = "3x - 5x"
            dir_emoji = "🟢 LONG"
        else:
            sl = current_price + (1.5 * atr)
            tp1 = current_price - (2.0 * atr)
            tp2 = current_price - (3.8 * atr)
            safe_liq = current_price * 1.25
            sugg_lev = "3x - 5x"
            dir_emoji = "🔴 SHORT"

        sl_pct = abs(current_price - sl) / current_price * 100
        tp1_pct = abs(tp1 - current_price) / current_price * 100
        tp2_pct = abs(tp2 - current_price) / current_price * 100

        msg = (
            f"⚡ *QUANT APEX SWING SETUP* ⚡\n"
            f"Asset: *#{clean_sym}/USDT* (1H Horizon)\n"
            f"Direction: *{dir_emoji}*\n\n"
            f"💵 *Entry Zone:* `${current_price:,.2f}`\n"
            f"🛡️ *Stop Loss:* `${sl:,.2f}` (-{sl_pct:.2f}% | Dynamic ATR)\n"
            f"🎯 *Target 1:* `${tp1:,.2f}` (+{tp1_pct:.2f}% ➔ Auto BE)\n"
            f"🚀 *Target 2:* `${tp2:,.2f}` (+{tp2_pct:.2f}% Extended)\n\n"
            f"📊 *Risk Parameters:*\n"
            f"• Max Suggested Lev: *{sugg_lev}*\n"
            f"• Safe Liq Buffer: *${safe_liq:,.2f}* (>25% room)\n"
            f"• ATR Volatility: `${atr:,.2f}`"
        )

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": f"📈 {clean_sym} Chart", "url": f"https://www.tradingview.com/chart/?symbol=BINANCE:{pair}"},
                    {"text": "👑 VIP Checkout & Plans", "url": f"https://t.me/{VIP_BOT_USERNAME}?start=vip"}
                ]
            ]
        }

        send_telegram(msg, reply_markup)
        
        c.execute("""
            INSERT OR REPLACE INTO trades (pair, direction, entry_price, tp1, tp2, sl, status, opened_at, last_signal_time)
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
        """, (pair, direction, current_price, tp1, tp2, sl, datetime.now().isoformat(), now_ts))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    while True:
        try:
            check_and_generate_signals()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(CHECK_INTERVAL_SEC)
