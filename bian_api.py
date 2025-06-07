import requests
import time
import hmac
import hashlib
import urllib.parse
import logging
import json
from typing import List, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_signature(query_string: str, body: str = "", api_secret: str = "") -> str:
    """
    生成 HMAC-SHA256 签名，符合 Binance 要求（query string 在前，request body 在后）。

    Args:
        query_string (str): 查询参数字符串（已编码）
        body (str): 请求体字符串（已编码），默认为空
        api_secret (str): API 私钥

    Returns:
        str: HMAC-SHA256 签名
    """
    signature_input = query_string + body
    logger.debug(f"签名输入: {signature_input}")

    return hmac.new(
        api_secret.encode('utf-8'),
        signature_input.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def get_symbol_info(symbol: str) -> Dict[str, Any]:
    """
    查询交易对的精度和规则。

    Args:
        symbol (str): 交易对，例如 "BTCUSDT"

    Returns:
        dict: 包含 quantityPrecision、minQty、stepSize 等信息，若失败返回空字典
    """
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        for s in data.get('symbols', []):
            if s['symbol'] == symbol:
                for f in s.get('filters', []):
                    if f['filterType'] == 'LOT_SIZE':
                        return {
                            'quantityPrecision': s['quantityPrecision'],
                            'minQty': float(f['minQty']),
                            'stepSize': float(f['stepSize'])
                        }
        logger.error(f"未找到交易对 {symbol} 的信息")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"查询交易对信息失败: {e}")
        return {}


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

    params = {
        'timestamp': timestamp,
        'recvWindow': 5000
    }
    if symbol:
        params['symbol'] = symbol

    query_string = urllib.parse.urlencode(params, safe='')
    params['signature'] = generate_signature(query_string, "", api_secret)

    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(response.json())
        response.raise_for_status()
        orders = response.json()

        logger.info(f"成功获取未平仓订单，数量: {len(orders)}")
        return orders[:10]
    except requests.exceptions.RequestException as e:
        logger.error(f"查询未平仓订单失败: {e}")
        if response.text:
            logger.error(f"响应内容: {response.text}")
        return []


def place_buy_order(
        api_key: str,
        api_secret: str,
        symbol: str,
        quantity: float,
        position_side: str = "LONG",
        order_type: str = "MARKET",
        price: float = None
) -> Dict[str, Any]:
    """
    下 U 本位合约买入订单（可指定做多或平空）。

    Args:
        api_key (str): Binance API 密钥
        api_secret (str): Binance API 私钥
        symbol (str): 交易对，例如 "BTCUSDT"
        quantity (float): 下单数量
        position_side (str): 仓位方向，"LONG"（做多）或 "SHORT"（平空），默认 "LONG"
        order_type (str): 订单类型，默认 "MARKET"，可选 "LIMIT"
        price (float, optional): 限价单价格，仅限价单需要

    Returns:
        dict: 订单响应数据，若失败返回空字典
    """
    if position_side not in ["LONG", "SHORT"]:
        logger.error("position_side 必须为 LONG 或 SHORT")
        return {}

    # 获取交易对精度规则
    symbol_info = get_symbol_info(symbol)
    if not symbol_info:
        return {}

    # 调整 quantity 精度
    precision = symbol_info['quantityPrecision']
    min_qty = symbol_info['minQty']
    step_size = symbol_info['stepSize']

    # 格式化 quantity
    quantity = round(quantity, precision)
    if quantity < min_qty:
        logger.error(f"数量 {quantity} 小于最小交易量 {min_qty}")
        return {}
    if step_size > 0 and (quantity - min_qty) % step_size != 0:
        logger.error(f"数量 {quantity} 不符合步进大小 {step_size}")
        return {}

    url = "https://fapi.binance.com/fapi/v1/order"
    timestamp = int(time.time() * 1000)

    params = {
        'symbol': symbol,
        'side': 'BUY',
        'positionSide': position_side,
        'type': order_type,
        'quantity': f"{quantity:.{precision}f}",
        'timestamp': timestamp,
        'recvWindow': 5000
    }
    if order_type == "LIMIT":
        if price is None:
            logger.error("限价单需要提供 price 参数")
            return {}
        params['price'] = f"{price:.2f}"
        params['timeInForce'] = 'GTC'

    query_string = urllib.parse.urlencode(params, safe='')
    params['signature'] = generate_signature(query_string, "", api_secret)

    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        order = response.json()

        logger.info(f"成功下买入订单（{position_side}）：{order.get('orderId')}")
        return order
    except requests.exceptions.RequestException as e:
        logger.error(f"下买入订单失败: {e}")
        if response.text:
            logger.error(f"响应内容: {response.text}")
        return {}


def place_sell_order(
        api_key: str,
        api_secret: str,
        symbol: str,
        quantity: float,
        position_side: str = "SHORT",
        order_type: str = "MARKET",
        price: float = None
) -> Dict[str, Any]:
    """
    下 U 本位合约卖出订单（可指定做空或平多）。

    Args:
        api_key (str): Binance API 密钥
        api_secret (str): Binance API 私钥
        symbol (str): 交易对，例如 "BTCUSDT"
        quantity (float): 下单数量
        position_side (str): 仓位方向，"SHORT"（做空）或 "LONG"（平多），默认 "SHORT"
        order_type (str): 订单类型，默认 "MARKET"，可选 "LIMIT"
        price (float, optional): 限价单价格，仅限价单需要

    Returns:
        dict: 订单响应数据，若失败返回空字典
    """
    if position_side not in ["LONG", "SHORT"]:
        logger.error("position_side 必须为 LONG 或 SHORT")
        return {}

    # 获取交易对精度规则
    symbol_info = get_symbol_info(symbol)
    if not symbol_info:
        return {}

    # 调整 quantity 精度
    precision = symbol_info['quantityPrecision']
    min_qty = symbol_info['minQty']
    step_size = symbol_info['stepSize']

    # 格式化 quantity
    quantity = round(quantity, precision)
    if quantity < min_qty:
        logger.error(f"数量 {quantity} 小于最小交易量 {min_qty}")
        return {}
    if step_size > 0 and (quantity - min_qty) % step_size != 0:
        logger.error(f"数量 {quantity} 不符合步进大小 {step_size}")
        return {}

    url = "https://fapi.binance.com/fapi/v1/order"
    timestamp = int(time.time() * 1000)

    params = {
        'symbol': symbol,
        'side': 'SELL',
        'positionSide': position_side,
        'type': order_type,
        'quantity': f"{quantity:.{precision}f}",
        'timestamp': timestamp,
        'recvWindow': 5000
    }
    if order_type == "LIMIT":
        if price is None:
            logger.error("限价单需要提供 price 参数")
            return {}
        params['price'] = f"{price:.2f}"
        params['timeInForce'] = 'GTC'

    query_string = urllib.parse.urlencode(params, safe='')
    params['signature'] = generate_signature(query_string, "", api_secret)

    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        order = response.json()

        logger.info(f"成功下卖出订单（{position_side}）：{order.get('orderId')}")
        return order
    except requests.exceptions.RequestException as e:
        logger.error(f"下卖出订单失败: {e}")
        if response.text:
            logger.error(f"响应内容: {response.text}")
        return {}


def main():
    # 替换为你的 API 密钥和私钥
    api_key = "cbZ1BYC8pvpFTlBFu6sXEadeTPzdEw3u7SgqC7RxCcFyJWx57m09mFqxhlS0cSSj"
    api_secret = "你的API私钥"  # 替换为实际私钥
    key = 'cbZ1BYC8pvpFTlBFu6sXEadeTPzdEw3u7SgqC7RxCcFyJWx57m09mFqxhlS0cSSj',
    secret = 'w2le7dkibjAQ4i1RgKUOqk0lAIDALzGoayU827yLJE150iliAsnC5CMpQHUdDAG3'
    symbol = "NEIROUSDT"  # 示例交易对

    # 查询未平仓订单
    open_orders = get_open_orders(api_key, secret)
    print("未平仓订单:")
    print(json.dumps(open_orders, indent=2, ensure_ascii=False))

    # 示例：下市价买入订单（做多）
    buy_long_order = place_buy_order(
        api_key=api_key,
        api_secret=secret,
        symbol=symbol,
        quantity=5,
        position_side="LONG",
        order_type="MARKET"
    )
    print("\n买入订单（做多）结果:")
    print(json.dumps(buy_long_order, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()