import sys
import time
import requests

TOKEN = '8992708431:AAFyr0BgA4zimCEijFIAuHgr6hbbLnYacw0'
VIP_CHANNEL = '-1004437107994'

def create_one_time_link():
    url = f"https://api.telegram.org/bot{TOKEN}/createChatInviteLink"
    payload = {
        "chat_id": VIP_CHANNEL,
        "name": f"VIP-Auto-{int(time.time())}",
        "member_limit": 1,
        "expire_date": int(time.time()) + 86400
    }
    res = requests.post(url, json=payload, timeout=10).json()
    if res.get("ok"):
        return res["result"]["invite_link"]
    return None

def send_vip_access(target_chat_id):
    link = create_one_time_link()
    if not link:
        print("[-] Failed to create invite link.")
        return

    msg = (
        "👑 *WELCOME TO DEVOPS ARCHITECT VIP TERMINAL*\n\n"
        "Your payment has been verified successfully.\n\n"
        f"🔗 *Exclusive 1-Time Invite Link:*\n{link}\n\n"
        "⚠️ *Security Notice:* This link is valid for *1 use only* and expires in 24 hours. "
        "Do not forward or share it."
    )
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    }
    r = requests.post(url, json=payload, timeout=10).json()
    if r.get("ok"):
        print(f"[+] VIP link delivered successfully to {target_chat_id}!")
    else:
        print(f"[-] Delivery failed: {r}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Χωρίς παράμετρο chat_id, απλώς τυπώνει ένα νέο link
        link = create_one_time_link()
        print(f"[+] Generated Link: {link}")
    else:
        target = sys.argv[1]
        send_vip_access(target)
