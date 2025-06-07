import json

from binance.cm_futures import CMFutures
import requests
import time
import hmac
import hashlib
import urllib.parse
import logging
from typing import List, Dict, Any


# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_signature(query_string: str, api_secret: str) -> str:
    """
    生成 HMAC-SHA256 签名。

    Args:
        query_string (str): 查询参数字符串
        api_secret (str): API 私钥

    Returns:
        str: HMAC-SHA256 签名
    """
    return hmac.new(
        api_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def get_open_orders(api_key: str, api_secret: str, symbol: str = None) -> List[Dict[str, Any]]:
    """
    查询 U 本位合约账户的当前未平仓订单。

    Args:
        api_key (str): Binance API 密钥
        api_secret (str): Binance API 私钥
        symbol (str, optional): 交易对，例如 "BTCUSDT"。若不提供，查询所有交易对

    Returns:
        list: 未平仓订单列表，若失败返回空列表
    """
    url = "https://fapi.binance.com/fapi/v1/openOrders"
    timestamp = int(time.time() * 1000)

    # 构造查询参数
    params = {
        'timestamp': timestamp,
        'recvWindow': 5000
    }
    if symbol:
        params['symbol'] = symbol

    # 生成签名
    query_string = urllib.parse.urlencode(params)
    params['signature'] = generate_signature(query_string, api_secret)

    # 设置请求头
    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        orders = response.json()

        logger.info(f"成功获取未平仓订单，数量: {len(orders)}")
        return orders[:10]  # 限制返回最多 10 条
    except requests.exceptions.RequestException as e:
        logger.error(f"查询未平仓订单失败: {e}")
        return []


def place_buy_order(
        api_key: str,
        api_secret: str,
        symbol: str,
        quantity: float,
        position_side: str,
        order_type: str = "MARKET",
        price: float = None
) -> Dict[str, Any]:
    """
    下 U 本位合约买入订单。

    Args:
        api_key (str): Binance API 密钥
        api_secret (str): Binance API 私钥
        symbol (str): 交易对，例如 "BTCUSDT"
        quantity (float): 下单数量
        order_type (str): 订单类型，默认 "MARKET"，可选 "LIMIT"
        price (float, optional): 限价单价格，仅限价单需要

    Returns:
        dict: 订单响应数据，若失败返回空字典
    """
    url = "https://fapi.binance.com/fapi/v1/order"
    timestamp = int(time.time() * 1000)

    # 构造请求参数
    params = {
        'symbol': symbol,
        'side': 'BUY',
        'positionSide': position_side,  # 持仓方向
        'type': order_type,
        'quantity': quantity,
        'timestamp': timestamp,
        'recvWindow': 5000
    }
    if order_type == "LIMIT":
        if price is None:
            logger.error("限价单需要提供 price 参数")
            return {}
        params['price'] = price
        params['timeInForce'] = 'GTC'  # 有效至取消

    # 生成签名
    query_string = urllib.parse.urlencode(params)
    params['signature'] = generate_signature(query_string, api_secret)

    # 设置请求头
    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        order = response.json()

        logger.info(f"成功下买入订单: {order.get('orderId')}")
        return order
    except requests.exceptions.RequestException as e:
        logger.error(f"下买入订单失败: {e}")
        return {}


def place_sell_order(
        api_key: str,
        api_secret: str,
        symbol: str,
        quantity: float,
        order_type: str = "MARKET",
        price: float = None
) -> Dict[str, Any]:
    """
    下 U 本位合约卖出订单。

    Args:
        api_key (str): Binance API 密钥
        api_secret (str): Binance API 私钥
        symbol (str): 交易对，例如 "BTCUSDT"
        quantity (float): 下单数量
        order_type (str): 订单类型，默认 "MARKET"，可选 "LIMIT"
        price (float, optional): 限价单价格，仅限价单需要

    Returns:
        dict: 订单响应数据，若失败返回空字典
    """
    url = "https://fapi.binance.com/fapi/v1/order"
    timestamp = int(time.time() * 1000)

    # 构造请求参数
    params = {
        'symbol': symbol,
        'side': 'SELL',
        'type': order_type,
        'quantity': quantity,
        'timestamp': timestamp,
        'recvWindow': 5000
    }
    if order_type == "LIMIT":
        if price is None:
            logger.error("限价单需要提供 price 参数")
            return {}
        params['price'] = price
        params['timeInForce'] = 'GTC'  # 有效至取消

    # 生成签名
    query_string = urllib.parse.urlencode(params)
    params['signature'] = generate_signature(query_string, api_secret)

    # 设置请求头
    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        order = response.json()

        logger.info(f"成功下卖出订单: {order.get('orderId')}")
        return order
    except requests.exceptions.RequestException as e:
        logger.error(f"下卖出订单失败: {e}")
        return {}


def main():
    # 替换为你的 API 密钥和私钥
    key = 'cbZ1BYC8pvpFTlBFu6sXEadeTPzdEw3u7SgqC7RxCcFyJWx57m09mFqxhlS0cSSj',
    secret = 'w2le7dkibjAQ4i1RgKUOqk0lAIDALzGoayU827yLJE150iliAsnC5CMpQHUdDAG3'

    symbol = "NEIROUSDT"  # 示例交易对

    # 示例：下市价买入订单
    buy_order = place_buy_order(
        api_key=key[0],
        api_secret=secret[0],
        symbol=symbol,
        quantity=0.01,  # 示例数量
        position_side="LONG",  # 持仓方向，LONG 或 SHORT
        # price=0.0004210,  # 市价单不需要价格
        order_type="MARKET"
    )
    print("\n买入订单结果:")
    print(json.dumps(buy_order, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()