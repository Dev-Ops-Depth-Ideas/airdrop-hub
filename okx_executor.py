import os
import hmac
import base64
import time
import json
import requests
from datetime import datetime, timezone

class OKXExecutionEngine:
    def __init__(self, api_key=None, secret_key=None, passphrase=None, is_demo=True):
        self.api_key = api_key or os.getenv("OKX_API_KEY", "")
        self.secret_key = secret_key or os.getenv("OKX_SECRET_KEY", "")
        self.passphrase = passphrase or os.getenv("OKX_PASSPHRASE", "")
        self.base_url = "https://www.okx.com"
        self.is_demo = is_demo

    def _get_headers(self, method, request_path, body=""):
        timestamp = datetime.now(timezone.utc).isoformat("T", "milliseconds").replace("+00:00", "Z")
        message = timestamp + method.upper() + request_path + (body if body else "")
        mac = hmac.new(self.secret_key.encode("utf-8"), message.encode("utf-8"), digestmod="sha256")
        signature = base64.b64encode(mac.digest()).decode("utf-8")
        
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
        if self.is_demo:
            headers["x-simulated-trading"] = "1"
        return headers

    def calculate_position_size(self, equity, risk_pct, entry_price, stop_loss_price):
        """Υπολογισμός Contracts βάσει max % risk απώλειας κεφαλαίου"""
        risk_capital = equity * (risk_pct / 100.0)
        price_diff = abs(entry_price - stop_loss_price)
        if price_diff <= 0:
            return 0.0
        btc_size = risk_capital / price_diff
        # OKX BTC-USDT-SWAP: 1 contract = 0.01 BTC
        contracts = round(btc_size / 0.01)
        return max(1, contracts)

    def execute_signal(self, inst_id="BTC-USDT-SWAP", side="buy", leverage=5, contracts=1, tp_price=None, sl_price=None):
        """Εκτέλεση Market Order με συνδεδεμένο TP/SL"""
        path = "/api/v5/trade/order"
        pos_side = "long" if side.lower() == "buy" else "short"
        
        payload = {
            "instId": inst_id,
            "tdMode": "cross",
            "side": side.lower(),
            "posSide": pos_side,
            "ordType": "market",
            "sz": str(contracts)
        }

        # Attached Take-Profit / Stop-Loss bracket
        if tp_price or sl_price:
            payload["attachAlgoOrds"] = []
            if tp_price:
                payload["attachAlgoOrds"].append({
                    "attachAlgoClOrdId": f"tp_{int(time.time())}",
                    "tpTriggerPx": str(tp_price),
                    "tpOrdPx": "-1"
                })
            if sl_price:
                payload["attachAlgoOrds"].append({
                    "attachAlgoClOrdId": f"sl_{int(time.time())}",
                    "slTriggerPx": str(sl_price),
                    "slOrdPx": "-1"
                })

        body = json.dumps(payload)
        headers = self._get_headers("POST", path, body)
        
        try:
            r = requests.post(self.base_url + path, data=body, headers=headers, timeout=10)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    engine = OKXExecutionEngine()
    print("OKX Execution Engine Initialized (Demo mode active)")
