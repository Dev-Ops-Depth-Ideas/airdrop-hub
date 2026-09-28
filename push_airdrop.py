import requests

def push_to_dashboard(project, category, status, task, score, est_val, url):
    endpoint = "https://airdrop-hub-xi.vercel.app/api/campaigns"
    headers = {
        "Authorization": "Bearer alpha_secret_key_123",
        "Content-Type": "application/json"
    }
    payload = {
        "project": project,
        "type": category,
        "tagClass": "bg-cyan-950 text-cyan-300 border-cyan-800",
        "status": status,
        "statusClass": "text-emerald-400",
        "task": task,
        "score": score,
        "estVal": int(est_val),
        "url": url
    }
    r = requests.post(endpoint, json=payload, headers=headers, timeout=5)
    return r.json()

if __name__ == "__main__":
    res = push_to_dashboard("Sui Network", "Mainnet", "Active Quest", "Swap & Liquidity", "Tier A", 600, "https://sui.io")
    print(res)
