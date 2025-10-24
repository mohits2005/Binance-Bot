from typing import Dict, Any
from .bot_core import BasicBot

def place_limit(bot: BasicBot, symbol: str, side: str, quantity: float, price: float, timeInForce: str = "GTC") -> Dict[str, Any]:

    return bot.place_limit_order(symbol, side, quantity, price, timeInForce)
