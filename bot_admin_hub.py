import asyncio
from push_airdrop import push_to_dashboard
from okx_executor import OKXExecutionEngine

okx = OKXExecutionEngine()

def handle_telegram_command(command_text, is_admin=True):
    if not is_admin:
        return "Unauthorized"

    parts = command_text.strip().split()
    cmd = parts[0].lower()

    # Συνταξη: /add_drop Project Type Status Tasks Score EstVal URL
    # Παράδειγμα: /add_drop Movement Testnet Active Faucet/Swap TierS 1200 https://movementlabs.xyz
    if cmd == "/add_drop":
        if len(parts) < 8:
            return "Usage: /add_drop <Project> <Testnet|Mainnet> <Status> <Task> <Score> <EstVal> <URL>"
        
        _, proj, cat, status, task, score, est_val, url = parts[:8]
        res = push_to_dashboard(proj, cat, status, task, score, int(est_val), url)
        if res.get("success"):
            return f"✅ Published to Airdrop Hub Dashboard: {proj} ({cat}) - Score: {score}"
        return f"❌ Failed: {res}"

    # Συνταξη: /signal BTC buy 63000 61800 66000
    if cmd == "/signal":
        if len(parts) < 6:
            return "Usage: /signal <ASSET> <buy|sell> <Entry> <SL> <TP>"
        
        _, asset, side, entry, sl, tp = parts[:6]
        entry, sl, tp = float(entry), float(sl), float(tp)
        
        # Risk Calc (1% risk on $10,000 equity default test)
        sz = okx.calculate_position_size(10000, 1.0, entry, sl)
        exec_res = okx.execute_signal(inst_id=f"{asset}-USDT-SWAP", side=side, contracts=sz, tp_price=tp, sl_price=sl)
        
        return (f"🚨 4H INSTITUTIONAL SIGNAL\n"
                f"Asset: {asset}/USDT\n"
                f"Side: {side.upper()}\n"
                f"Entry: ${entry}\n"
                f"Stop Loss: ${sl}\n"
                f"Take Profit: ${tp}\n"
                f"Calculated Contracts: {sz}\n"
                f"OKX Engine Status: {exec_res.get('msg', 'Executed')}")

    return "Unknown command"

if __name__ == "__main__":
    # Test local commands
    print(handle_telegram_command("/add_drop MovementLabs Testnet Active Swaps/Bridge TierS 1500 https://movementlabs.xyz"))
