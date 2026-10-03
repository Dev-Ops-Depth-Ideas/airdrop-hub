import os
import json
import asyncio
import aiohttp
import feedparser
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUB_BOT_TOKEN = os.getenv("HUB_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@AlphaHunterHub")
CACHE_FILE = "posted_airdrops.json"

# Πηγές Feed (Cryptorank, Web3 Alpha, Testnet guides)
RSS_FEEDS = [
    "https://cryptorank.io/news/feed",
    "https://medium.com/feed/tag/airdrop",
    "https://cointelegraph.com/rss/tag/altcoin"
]

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache), f)

async def evaluate_and_format_with_gemini(title: str, summary: str, link: str):
    """
    Το Gemini λειτουργεί ταυτόχρονα ως Scam Filter, Evaluator και Copywriter.
    Αν το περιεχόμενο δεν είναι ουσιαστικό airdrop/testnet alpha, επιστρέφει REJECT.
    """
    prompt = f"""
You are the Lead Web3 & Airdrop Researcher for Telegram channel '@AlphaHunterHub'.

Analyze this news/feed item:
Title: {title}
Summary: {summary}
Link: {link}

TASK:
1. Determine if this is an actual legit Airdrop, Testnet, Retroactive campaign, or high-potential ecosystem alpha.
2. If it is generic news, price prediction, memecoin pump, or irrelevant spam, reply STRICTLY with the single word: REJECT
3. If it is a VALID opportunity, format it into an elite Telegram post:
   - Header with emojis (e.g. 🪂 NEW AIRDROP / TESTNET ALPHA)
   - Quick Stats: Cost (Free/Testnet/Gas), Time, Potential (Tier 1/Tier 2)
   - 1-2 sentences project summary + why it matters
   - Step-by-Step Action Guide (3-4 concise actionable bullets)
   - Official Link: {link}
   - Footer: #Alpha #Airdrop #Testnet #Web3
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                if resp.status != 200:
                    print(f"⚠️ Gemini API Error ({resp.status})")
                    return None
                data = await resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text.startswith("REJECT") or text == "REJECT":
                    return None
                return text
    except Exception as e:
        print(f"❌ Error communicating with Gemini: {e}")
        return None

async def broadcast_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{HUB_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                res = await resp.json()
                return res.get("ok", False)
    except Exception as e:
        print(f"❌ Telegram send error: {e}")
        return False

async def scan_cycle():
    cache = load_cache()
    print("🔍 Έναρξη σκαναρίσματος πηγών για νέα Alpha...")

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:  # Έλεγχος των 5 πιο πρόσφατων ανά πηγή
                entry_id = entry.get("link", entry.get("title", ""))
                if not entry_id or entry_id in cache:
                    continue

                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                link = entry.get("link", "")

                print(f"⚡ Εντοπίστηκε υποψήφιο θέμα: {title[:50]}...")
                formatted_post = await evaluate_and_format_with_gemini(title, summary, link)

                if formatted_post:
                    print("🎯 Εγκρίθηκε ως Legit Alpha από το Gemini! Αποστολή...")
                    success = await broadcast_to_telegram(formatted_post)
                    if success:
                        print("✅ Δημοσιεύτηκε στο @AlphaHunterHub!")
                        cache.add(entry_id)
                        save_cache(cache)
                        # Μικρό delay ανάμεσα στα posts
                        await asyncio.sleep(5)
                else:
                    print("⏭️ Απορρίφθηκε (χαμηλής ποιότητας ή άσχετο).")
                    cache.add(entry_id)
                    save_cache(cache)

        except Exception as e:
            print(f"⚠️ Σφάλμα κατά την ανάγνωση του feed {feed_url}: {e}")

async def main():
    print("🚀 Alpha Hunter Bot Daemon ξεκίνησε!")
    while True:
        await scan_cycle()
        print("💤 Αναμονή 60 λεπτών μέχρι τον επόμενο έλεγχο...")
        await asyncio.sleep(3600)  # Έλεγχος κάθε 1 ώρα

if __name__ == "__main__":
    asyncio.run(main())
