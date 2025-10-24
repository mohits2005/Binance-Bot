# runner.py (place at project root)
import os, sys
PROJECT_ROOT = os.path.dirname(__file__)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import argparse
import json
import getpass

from src.bot_core import BasicBot
from src.market_orders import place_market
from src.limit_orders import place_limit
from src.advanced.twap import simple_twap
from src.advanced.oco import place_oco
...


def pretty(obj):
    print(json.dumps(obj, indent=2))

def main():
    p = argparse.ArgumentParser(description="Runner for simplified Binance bot (testnet)")
    p.add_argument("--api-key", required=False, help="Binance Testnet API key")
    p.add_argument("--api-secret", required=False, help="Binance Testnet API secret")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("market")
    m.add_argument("--symbol", required=True)
    m.add_argument("--side", required=True, choices=["BUY","SELL"])
    m.add_argument("--qty", required=True, type=float)

    l = sub.add_parser("limit")
    l.add_argument("--symbol", required=True)
    l.add_argument("--side", required=True, choices=["BUY","SELL"])
    l.add_argument("--qty", required=True, type=float)
    l.add_argument("--price", required=True, type=float)

    t = sub.add_parser("twap")
    t.add_argument("--symbol", required=True)
    t.add_argument("--side", required=True, choices=["BUY","SELL"])
    t.add_argument("--total_qty", required=True, type=float)
    t.add_argument("--slices", type=int, default=5)
    t.add_argument("--interval", type=int, default=60)

    o = sub.add_parser("oco")
    o.add_argument("--symbol", required=True)
    o.add_argument("--side", required=True, choices=["BUY","SELL"])
    o.add_argument("--qty", required=True, type=float)
    o.add_argument("--tp", required=True, type=float)
    o.add_argument("--sl", required=True, type=float)

    args = p.parse_args()

    api_key = args.api_key or input("API Key: ").strip()
    api_secret = args.api_secret or getpass.getpass("API Secret: ").strip()

    bot = BasicBot(api_key, api_secret)

    if args.cmd == "market":
        print("Placing MARKET order...")
        res = place_market(bot, args.symbol, args.side, args.qty)
        pretty(res)
    elif args.cmd == "limit":
        print("Placing LIMIT order...")
        res = place_limit(bot, args.symbol, args.side, args.qty, args.price)
        pretty(res)
    elif args.cmd == "twap":
        print("Starting TWAP...")
        res = simple_twap(bot, args.symbol, args.side, args.total_qty, slices=args.slices, interval_seconds=args.interval)
        pretty({"slices_executed": len(res), "last": res[-1] if res else None})
    elif args.cmd == "oco":
        print("Starting OCO...")
        res = place_oco(bot, args.symbol, args.side, args.qty, tp_price=args.tp, sl_price=args.sl)
        pretty(res)

if __name__ == "__main__":
    main()
