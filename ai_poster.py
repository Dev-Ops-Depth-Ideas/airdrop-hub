import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TG_BOT_TOKEN = os.getenv("HUB_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@AlphaHunterHub")

PROMPT_TEMPLATE = """
You are the lead Web3 Alpha Researcher for the Telegram channel '@AlphaHunterHub'.
Format the provided raw crypto/airdrop info into an attractive, high-engagement Telegram post.

Requirements:
- Catchy Header with emojis (e.g. 🪂 NEW POTENTIAL AIRDROP / TESTNET)
- Meta stats: Cost (Free/Gas/Paid), Time required, Potential Tier (Tier 1/2/3)
- Brief summary (1-2 sentences on what the project is)
- Step-by-step action guide (3-4 crisp bullet points)
- Call-to-Action Link
- Footer with tags: #Alpha #Airdrop #Testnet #Web3

Raw Info:
{raw_data}
"""

async def generate_post(raw_text: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": PROMPT_TEMPLATE.format(raw_data=raw_text)}]
        }]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                print(f"API Error {resp.status}: {await resp.text()}")
                return None
            data = await resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"Parsing error: {e}")
                return None

async def send_to_channel(text: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()

async def main():
    test_data = "Monad testnet ecosystem guide: Claim testnet MON from faucet, complete initial swaps on test DEXs, bridge test assets. High tier potential backed by Paradigm. Link: https://monad.xyz"
    
    print("🧠 Κλήση Gemini API για formatting...")
    post = await generate_post(test_data)
    
    if post:
        print("\n--- Προεπισκόπηση Post ---")
        print(post)
        print("\n🚀 Αποστολή στο Telegram...")
        res = await send_to_channel(post)
        if res.get("ok"):
            print("✅ Δημοσιεύτηκε επιτυχώς στο @AlphaHunterHub!")
        else:
            print(f"❌ Σφάλμα Telegram: {res}")
    else:
        print("❌ Απέτυχε η δημιουργία του post.")

if __name__ == "__main__":
    asyncio.run(main())
