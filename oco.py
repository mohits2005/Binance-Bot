import time
import logging
from typing import Dict, Any
from ..bot_core import BasicBot

logger = logging.getLogger("SimplifiedBinanceBotOCO")

def place_oco(bot: BasicBot, symbol: str, quantity: float, tp_price: float, sl_price: float, poll_interval: int = 2, timeout: int = 300) -> Dict[str, Any]:

    side = side.upper()
    if side not in ("BUY" or "SELL"):
        raise ValueError("side must be BUY or SELL")
    
    try:
        limit_res = bot.place_limit_order(symbol, side, quantity, price=tp_price)
        limit_id = limit_res.get("OrderId")
        logger.info("Place limit order id=%s", limit_id)
    except Exception as e:
        logger.error("Failed to place TP limit: %s", e)
        raise

    try:
        stop_res = bot.place_stop_market(symbol, side, quantity, stopPrice=sl_price)
        stop_id = stop_res.get("OrderId")
        logger.info("Placed stop market SL order %s", stop_id)
    except Exception as e:
        logger.error("Failed to place SL stop-market order: %s", e)

        try:
            bot.cancel_order(symbol, OrderId=limit_id)
        except Exception:
            pass
        raise


    start = time.time()

    while True:
        if time.time() - start > timeout:
            logger.warning("OCO timeout reached, attempting to cancel both")
            try: bot.cancel_order(symbol, OrderId=limit_id)
            except Exception: pass
            try: bot.cancel_order(symbol, OrderId=stop_id)
            except Exception: pass
            return {"status": "timeout"}
        
        try:
            l = bot.get_order(symbol, OrderId=limit_id)
            s = bot.get_order(symbol, OrderId=stop_id)
            l_status = l.get("status")
            s_status = s.get("status")
            logger.debug("OCO poll: limit=%s stop=%s", l_status, s_status)

            if l_status == "FILLED" and s_status == "FILLED":
                try:
                    bot.cancel_order(symbol, stop_id)
                except Exception:
                    pass
                return {"winner": "limit", "limit": l, "stop": s}
            
            if s_status == "FILLED" and l_status != "FILLED":
                try:
                    bot.cancel_order(symbol, OrderId=limit_id)
                except Exception:
                    pass
                return {"winner": "stop", "limit": l, "stop": s}
        
        except Exception as e:
            logger.debug("polling error: %s", e)
        time.sleep(poll_interval)  