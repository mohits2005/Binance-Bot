from typing import Dict, Any, Optional
import time
import hmac
import hashlib
import logging
from urllib.parse import urlencode
import requests
import json


logger = logging.getLogger("SimplifiedBinanceBotCore")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

DEFAULT_BASE_URL = "https://testnet.binancefuture.com"
ORDER_PATH = "/fapi/v1/order"
SERVER_TIME_PATH = "/fapi/v1/time"
EXCHANGE_INFO = "/fapi/v1/exchangeInfo"

class BasicBot:
    def __init__(self, api_key: str, api_secret: str, base_url: str = DEFAULT_BASE_URL, recv_window: int = 5000):

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.recv_window = recv_window
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        logger.info("BasicBot initialized (base_url=%s)", self.base_url)

    def _now_ms(self):
        return int(time.time() * 1000)
        
    def _sign(self, qs: str):
        return hmac.new(self.api_secret.encode("utf-8"), qs.encode("utf-8"), hashlib.sha256).hexdigest()
        
    def _get_server_time_offset(self):

        try:
            url = f"{self.base_url}{SERVER_TIME_PATH}"
            r = self.session.get(url, timeout=5)
            r.raise_for_status()
            server_time = r.json().get("serverTime")
            if server_time is None:
                return 0
            return int(server_time) - self._now_ms()
        except Exception as e:
            logger.debug("Could not fetch server time offset: %s", e)
            return 0
            
    def _signed_request(self, method, path, params: Dict[str, Any]):

        params = dict(params)
        offset = self._get_server_time_offset()
        params["timestamp"] = self._now_ms() + offset
        params["recvWindow"] = self.recv_window

        qs = urlencode(params, doseq=True)
        signatue = self._sign(qs)
        url = f"{self.base_url}{path}?{qs}&signature={signatue}"

        logger.debug("API REQUEST -> %s %s", method.upper(), url)
        if method.upper() == "GET":
            resp = self.session.get(url, timeout=10)
        elif method.upper() == "POST":
            resp = self.session.post(url, timeout=10)
        elif method.upper() == "DELETE":
            resp = self.session.delete(url, timeout=10)
        else:
            raise ValueError("Unsupported HTTP method: " + method)
        
        logger.debug("API Response code=%s body=%s", resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json()
    
    def place_market_order(self, symbol: str, side: str, quantity: float, reduce_only: bool = False) -> Dict[str, Any]:

        side = side.upper()
        if side not in ("BUY" or "SELL"):
            raise ValueError("side must be BUY or SELL")
        params = {
            "symbol": symbol.upper(),
            "side": side,
            "type": "MARKET",
            "quantity": float(quantity),
            "reduceOnly": str(bool(reduce_only)).lower()
        }
        return self._signed_request("POST", ORDER_PATH, params)
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, timeInForce: str = "GTC", reduce_only: bool = False) -> Dict[str, Any]:
        side = side.upper()
        if side not in ("BUY" or "SELL"):
            raise ValueError("side must be BUY or SELL")
        params = {
            "symbol": symbol.upper(),
            "side": side,
            "type": "LIMIT",
            "quantity": float(quantity),
            "price": float(price),
            "timeInForce": timeInForce,
            "reduceOnly": str(bool(reduce_only)).lower()
        }

        return self._signed_request("POST", ORDER_PATH, params)
    
    def place_stop_market(self, symbol: str, side: str, quantity: float, stopPrice: float, reduce_only: bool = False) -> Dict[str, Any]:

        side = side.upper()
        if side not in ("BUY" or "SELL"):
            raise ValueError("side must be BUY or SELL")
        params = {
            "symbol": symbol.upper(),
            "side": side,
            "quantity": float(quantity),
            "stopPrice": float(stopPrice),
            "reduce_only": str(bool(reduce_only)).lower()
        }
        
        return self._signed_request("POST", ORDER_PATH, params)
    
    def get_order(self, symbol: str, OrderId: Optional[int] = None, origClientId: Optional[int] = None):

        params = {"symbol": symbol.upper()}
        if OrderId is not None:
            params["OrderId"] = int(OrderId)
        if origClientId:
            params["origClientId"] = origClientId
        return self._signed_request("GET", ORDER_PATH, params)
    
    def cancel_order(self, symbol: str, OrderId: Optional[int] = None, origClientId: Optional[int] = None):

        params = {"symbol": symbol.upper()}
        if OrderId is not None:
            params["OrderId"] = int(OrderId)
        if origClientId:
            params["origClientId"] = origClientId
        return self._signed_request("DELETE", ORDER_PATH, params)
    

