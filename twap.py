# src/advanced/twap.py
import time
from typing import List, Dict, Any

try:
    from ..bot_core import BasicBot
except Exception:
    from ..bot_core import BasicBot  # if running from src/

def simple_twap(bot: BasicBot, symbol: str, side: str, total_quantity: float, slices: int = 5, interval_seconds: int = 60) -> List[Dict[str, Any]]:
    if slices < 1:
        raise ValueError("slices must be >= 1")
    side = side.upper()
    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    per_slice = float(total_quantity) / slices
    results = []
    for i in range(slices):
        res = bot.place_market_order(symbol, side, per_slice)
        results.append(res)
        if i < slices - 1:
            time.sleep(interval_seconds)
    return results

if __name__ == "__main__":
    # quick manual test
    import getpass
    api_key = input("API Key: ").strip()
    api_secret = getpass.getpass("API Secret: ").strip()
    bot = BasicBot(api_key, api_secret)
    symbol = input("Symbol: ").strip()
    side = input("Side (BUY/SELL): ").strip()
    total = float(input("Total quantity: ").strip())
    slices = int(input("Slices (default 5): ").strip() or 5)
    interval = int(input("Interval seconds (default 60): ").strip() or 60)
    print(simple_twap(bot, symbol, side, total, slices, interval))

