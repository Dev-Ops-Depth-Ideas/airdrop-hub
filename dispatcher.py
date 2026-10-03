import asyncio
import html
import logging
from typing import Optional
import aiohttp

logger = logging.getLogger("TelegramDispatcher")

class TelegramDispatcher:
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self.queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        self._session = aiohttp.ClientSession()
        self._worker_task = asyncio.create_task(self._process_queue())
        logger.info("Telegram Dispatcher active.")

    async def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
        if self._session:
            await self._session.close()

    async def send_signal(
        self,
        strategy: str,
        pair: str,
        action: str,
        entry: float,
        sl: float,
        tp1: float,
        tp2: float,
        timeframe: str = "15m",
        notes: str = ""
    ):
        strategy_safe = html.escape(strategy.upper())
        pair_safe = html.escape(pair.upper())
        action_safe = html.escape(action.upper())
        notes_safe = html.escape(notes) if notes else ""
        icon = "🟢" if action_safe == "LONG" else "🔴"

        text = (
            f"⚡ <b>[{strategy_safe}]</b>\n"
            f"{icon} <b>#{pair_safe}</b> | {timeframe}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Action:</b> <code>{action_safe}</code>\n"
            f"<b>Entry:</b> <code>{entry:.4f}</code>\n"
            f"<b>SL:</b> <code>{sl:.4f}</code>\n"
            f"<b>TP 1:</b> <code>{tp1:.4f}</code>\n"
            f"<b>TP 2:</b> <code>{tp2:.4f}</code>\n"
        )
        if notes_safe:
            text += f"\n💡 <i>Notes:</i> {notes_safe}\n"
        text += f"━━━━━━━━━━━━━━━━━━\n⚠️ <i>Risk: 1-2% max</i>"

        await self.queue.put({"text": text, "silent": False})

    async def send_update(self, strategy: str, pair: str, status: str, pnl_pct: float):
        strategy_safe = html.escape(strategy.upper())
        pair_safe = html.escape(pair.upper())
        icon = "🎯" if pnl_pct > 0 else "🛑"
        sign = "+" if pnl_pct >= 0 else ""

        text = (
            f"⚡ <b>[{strategy_safe}] UPDATE</b>\n"
            f"{icon} <b>#{pair_safe}</b>: {html.escape(status)}\n"
            f"PnL: <b>{sign}{pnl_pct:.2f}%</b>"
        )
        await self.queue.put({"text": text, "silent": True})

    async def _process_queue(self):
        while True:
            item = await self.queue.get()
            payload = {
                "chat_id": self.channel_id,
                "text": item["text"],
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
                "disable_notification": item["silent"]
            }
            
            for attempt in range(1, 4):
                try:
                    async with self._session.post(self.api_url, json=payload, timeout=10) as resp:
                        res = await resp.json()
                        if resp.status == 200 and res.get("ok"):
                            break
                        if resp.status == 429:
                            wait_s = res.get("parameters", {}).get("retry_after", 3)
                            await asyncio.sleep(wait_s)
                            continue
                        logger.error(f"API Error {resp.status}: {res.get('description')}")
                        break
                except Exception as e:
                    logger.error(f"Network error (attempt {attempt}): {e}")
                    await asyncio.sleep(2 * attempt)

            self.queue.task_done()
            await asyncio.sleep(1.0)
