from typing import Dict, Any
from .bot_core import BasicBot

def place_market(bot: BasicBot, symbol: str, side: str, quantity: float) -> Dict[str, Any]:

    return bot.place_market_order(symbol, side,quantity)

