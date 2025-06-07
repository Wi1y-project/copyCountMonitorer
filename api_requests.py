import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import requests
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "if-none-match": "9cc6b21673fcc1e9267d7a344fa8b96dc4f9283a192fe0b23a2f142eb9e49974",
        "priority": "u=0, i",
        "referer": "https://www.binance.com/zh-CN/copy-trading",
        "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

headers2 = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    # "bnc-uuid": "200d472d-d640-4326-b68e-d427c395758b",
    "clienttype": "web",
    "content-type": "application/json",
    # "csrftoken": "d41d8cd98f00b204e9800998ecf8427e",
    # "device-info": "eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjkwMCwxNDQwIiwiYXZhaWxhYmxlX3NjcmVlbl9yZXNvbHV0aW9uIjoiOTAwLDE0NDAiLCJzeXN0ZW1fdmVyc2lvbiI6Ik1hYyBPUyAxMC4xNS43IiwiYnJhbmRfbW9kZWwiOiJ1bmtub3duIiwic3lzdGVtX2xhbmciOiJ6aC1DTiIsInRpbWV6b25lIjoiR01UKzA4OjAwIiwidGltZXpvbmVPZmZzZXQiOi00ODAsInVzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoTWFjaW50b3NoOyBJbnRlbCBNYWMgT1MgWCAxMF8xNV83KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTM2LjAuMC4wIFNhZmFyaS81MzcuMzYiLCJsaXN0X3BsdWdpbiI6IlBERiBWaWV3ZXIsQ2hyb21lIFBERiBWaWV3ZXIsQ2hyb21pdW0gUERGIFZpZXdlcixNaWNyb3NvZnQgRWRnZSBQREYgVmlld2VyLFdlYktpdCBidWlsdC1pbiBQREYiLCJjYW52YXNfY29kZSI6IjdhYjQ1ZmUxIiwid2ViZ2xfdmVuZG9yIjoiR29vZ2xlIEluYy4gKEFwcGxlKSIsIndlYmdsX3JlbmRlcmVyIjoiQU5HTEUgKEFwcGxlLCBBTkdMRSBNZXRhbCBSZW5kZXJlcjogQXBwbGUgTTEsIFVuc3BlY2lmaWVkIFZlcnNpb24pIiwiYXVkaW8iOiIxMjQuMDQzNDgxNTU4NzY1MDUiLCJwbGF0Zm9ybSI6Ik1hY0ludGVsIiwid2ViX3RpbWV6b25lIjoiQXNpYS9TaGFuZ2hhaSIsImRldmljZV9uYW1lIjoiQ2hyb21lIFYxMzYuMC4wLjAgKE1hYyBPUykiLCJmaW5nZXJwcmludCI6IjdlNDk4ZmI2NjA1NGZkOTE3NzJjODQ5NmE5OTQ0ZDQ1IiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiLCJ9",
    # "fvideo-id": "33c9eddb81baa889acbdf9f74c8c682d319f3092",
    "lang": "zh-CN",
    "origin": "https://www.binance.com",
    "priority": "u=1, i",
    "referer": "https://www.binance.com/zh-CN/copy-trading/lead-details/4466349480575764737",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "x-passthrough-token;": "",
    # "x-trace-id": "5cbe468a-0bd4-4739-92ec-a746ca8a55ea",
    # "x-ui-request-trace": "5cbe468a-0bd4-4739-92ec-a746ca8a55ea"
}

# Define cookies
cookies = {
    "aws-waf-token": "88cd7a6d-caf5-4727-b942-34eea22a4303:AQoApZg2+k0PAAAA:SSX3E64h4qNLF5xL7VcIPSo8xpPTUQzLXHOTHhpm79xHAXBJ1CqMSIspKlWz5N37ouwCDL1oaTjCFTiBUKz9eBxU1XsYEv1bEC1wqk4rv2dwiGSsDc+xin/XeJjGXcDAjPkqjA1KCdhrasL95+n2QOWg9A0DskGTOY8jHWj2PgPZ5fYi30isvM5NdvTVj70Izvw="
}


def fetch_binance_lead_details(lead_id, time_range="30D", max_retries=3, backoff_factor=0.3, timeout=10):
    """
    Fetch lead details from Binance copy trading API with retry mechanism.

    Args:
        lead_id (str): The lead ID for the copy trading details
        time_range (str): Time range parameter (default: "30D")
        max_retries (int): Maximum number of retry attempts (default: 3)
        backoff_factor (float): Backoff factor for retry delays (default: 0.3)
        timeout (int): Request timeout in seconds (default: 10)

    Returns:
        dict: Response data if successful, None if failed
    """

    # Define headers

    # Define URL and parameters
    url = f"https://www.binance.com/zh-CN/copy-trading/lead-details/{lead_id}"
    params = {"timeRange": time_range}

    # Retry loop
    for attempt in range(max_retries + 1):
        try:
            # Make the request
            response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=timeout)

            # Check if response is successful
            response.raise_for_status()

            logger.info(f"Successfully fetched data for lead_id: {lead_id}")
            return {
                "status_code": response.status_code,
                "text": response.text,
            }

        except requests.exceptions.HTTPError as http_err:
            if response.status_code in [429, 500, 502, 503, 504] and attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.warning(f"HTTP error {response.status_code}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                continue
            logger.error(f"HTTP error occurred: {http_err}")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.warning(f"Connection error. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                continue
            logger.error(f"Connection error occurred: {conn_err}")
            return None
        except requests.exceptions.Timeout as timeout_err:
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.warning(f"Timeout error. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                continue
            logger.error(f"Timeout error occurred: {timeout_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred: {req_err}")
            return None

    logger.error(f"Failed to fetch data after {max_retries} attempts")
    return None


def parse_binance_lead_data(lead_id, time_range="30D", max_retries=3, backoff_factor=0.3, timeout=10):
    """
    从Binance复制交易API的响应中解析领单者数据。

    Args:
        lead_id (str): 领单者ID
        time_range (str): 时间范围参数 (默认: "30D")
        max_retries (int): 最大重试次数 (默认: 3)
        backoff_factor (float): 重试延迟的退避因子 (默认: 0.3)
        timeout (int): 请求超时时间（秒） (默认: 10)

    Returns:
        dict: 包含解析数据的字典，包含当前跟单人数等信息；如果失败返回None
    """
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # 调用fetch_binance_lead_details函数获取数据
        result = fetch_binance_lead_details(
            lead_id=lead_id,
            time_range=time_range,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            timeout=timeout
        )

        # 检查是否成功获取数据
        if not result or 'text' not in result:
            logger.error(f"无法获取领单者 {lead_id} 的数据")
            return None

        # 解析HTML响应
        soup = BeautifulSoup(result['text'], 'html.parser')

        # 查找__APP_DATA脚本标签
        script_tag = soup.find(attrs={'id': '__APP_DATA'})
        if not script_tag:
            logger.error("未找到__APP_DATA脚本标签")
            return None

        # 解析JSON数据
        try:
            app_data = json.loads(script_tag.text)
            user_dict = \
            app_data['appState']['loader']['dataByRouteId']['d6a9']['dehydratedState']['queries'][1]['state']['data'][
                'data']
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"JSON解析错误或数据结构不正确: {e}")
            return None

        # 提取当前跟单人数
        current_copy_count = user_dict.get('currentCopyCount')
        if current_copy_count is None:
            logger.error("无法获取当前跟单人数")
            return None

        # 构造返回结果
        result_data = {
            'lead_id': lead_id,
            'current_copy_count': current_copy_count,
            'user_data': user_dict
        }

        logger.info(f"成功解析领单者 {lead_id} 的数据，当前跟单人数: {current_copy_count}")
        return result_data

    except Exception as e:
        logger.error(f"解析领单者 {lead_id} 数据时发生未知错误: {e}")
        return None


def get_deal(
    portfolio_id: str,
    max_retries: int = 3,
    backoff_factor: float = 0.3,
    timeout: int = 10
) -> Optional[Dict[str, Any]]:
    """
    从 Binance 复制交易接口获取领单者的最新订单历史。

    Args:
        portfolio_id (str): 领单者 portfolio ID
        max_retries (int): 最大重试次数，默认 3
        backoff_factor (float): 重试延迟的退避因子，默认 0.3
        timeout (int): 请求超时时间（秒），默认 10

    Returns:
        dict: 包含订单历史的字典，如果失败返回 None
    """
    # 固定时间范围：end_time 为当前时间，start_time 为 7 天前
    end_time = int(time.time() * 1000)
    start_time = end_time - 7 * 24 * 3600 * 1000  # 7 天前
    page_size = 10

    # 定义请求 URL
    url = "https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/order-history"

    # 构造请求数据
    data = {
        "portfolioId": portfolio_id,
        "startTime": start_time,
        "endTime": end_time,
        "pageSize": page_size
    }
    data_str = json.dumps(data, separators=(',', ':'))

    # 重试循环
    for attempt in range(max_retries + 1):
        try:
            # 发送 POST 请求
            response = requests.post(
                url,
                headers=headers2,
                cookies=cookies,
                data=data_str,
                timeout=timeout
            )

            # 检查响应状态
            response.raise_for_status()

            # 解析 JSON 响应
            result = response.json()

            # 检查响应代码
            if result.get("code") != "000000":
                logger.error(f"API 返回错误: {result.get('message')} - {result.get('messageDetail')}")
                return None

            logger.info(f"成功获取 portfolioId {portfolio_id} 的订单历史")
            return result.get("data", {})['list']

        except requests.exceptions.HTTPError as http_err:
            if response.status_code in [429, 500, 502, 503, 504] and attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.warning(f"HTTP 错误 {response.status_code}，将在 {sleep_time:.2f} 秒后重试...")
                time.sleep(sleep_time)
                continue
            logger.error(f"HTTP 错误: {http_err}")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.warning(f"连接错误，将在 {sleep_time:.2f} 秒后重试...")
                time.sleep(sleep_time)
                continue
            logger.error(f"连接错误: {conn_err}")
            return None
        except requests.exceptions.Timeout as timeout_err:
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.warning(f"超时错误，将在 {sleep_time:.2f} 秒后重试...")
                time.sleep(sleep_time)
                continue
            logger.error(f"超时错误: {timeout_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            logger.error(f"请求错误: {req_err}")
            return None
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON 解析错误: {json_err}")
            return None

    logger.error(f"在 {max_retries} 次尝试后仍无法获取订单历史")
    return None


if __name__ == "__main__":
    print(get_deal('4466349480575764737'))
