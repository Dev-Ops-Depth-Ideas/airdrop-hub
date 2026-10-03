import asyncio
import logging
from aiohttp import ClientSession, ClientTimeout

BOT_TOKEN = "8661204678:AAGTE-dxuPbx3RWC_d2XKFqipJlCVCvzBVA"
CHAT_ID = "7176159687"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def send_signal(
    session: ClientSession,
    pair: str,
    action: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    indicator_note: str = "Quant Momentum Breakout"
) -> bool:
    emoji_action = "🟢 LONG / BUY" if action.upper() == "BUY" else "🔴 SHORT / SELL"
    
    text = (
        f"⚡ <b>QUANT APEX SIGNAL</b> ⚡\n\n"
        f"📊 <b>Asset:</b> #{pair}\n"
        f"🎯 <b>Action:</b> {emoji_action}\n"
        f"💵 <b>Entry:</b> ${entry_price:,.4f}\n"
        f"🛑 <b>Stop Loss:</b> ${stop_loss:,.4f}\n"
        f"💰 <b>Take Profit:</b> ${take_profit:,.4f}\n\n"
        f"📈 <b>Strategy:</b> <i>{indicator_note}</i>\n"
        f"🤖 <b>Bot:</b> <code>@Quant_Apex_Signal_Bot</code>"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        async with session.post(url, json=payload, timeout=ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                logging.info(f"Signal sent successfully for {pair}")
                return True
            else:
                err_text = await resp.text()
                logging.error(f"Failed to send ({resp.status}): {err_text}")
                return False
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return False

async def main():
    print("Testing connection with Telegram...")
    async with ClientSession() as session:
        success = await send_signal(
            session=session,
            pair="BTCUSDT",
            action="BUY",
            entry_price=64500.00,
            stop_loss=63800.00,
            take_profit=66200.00,
            indicator_note="RSI Rebound + Volume Spike"
        )
        if success:
            print("To minima stalthike epitixos sto Telegram sou!")
        else:
            print("Apotyxia apostolis. Elegkse an exeis patisei START sto bot.")

if __name__ == "__main__":
    asyncio.run(main())
