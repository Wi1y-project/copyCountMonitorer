import json
import requests
import time
import logging
from api_requests import parse_binance_lead_data


def dd_sender(text):
    """
    发送钉钉通知

    Args:
        text (str): 要发送的通知消息内容
    """
    headers = {
        "Content-Type": "application/json"
    }
    url = "https://oapi.dingtalk.com/robot/send"
    params = {
        "access_token": "10eaa0ee407dc6ddb4c87ba0e99ef9943e7cbb53912f6ef4004d1751978266b3"
    }
    data = {
        "msgtype": "text",
        "text": {
            "content": f"通知： 线上Gemini出错:{text}"
        }
    }
    try:
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, params=params, data=data)
        response.raise_for_status()
        logging.info("钉钉通知发送成功")
    except requests.exceptions.RequestException as e:
        logging.error(f"钉钉通知发送失败: {e}")


def main():
    """
    每分钟检查Binance领单者跟单人数，若少于1000人或连续错误超过5次则发送钉钉通知
    """
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 领单者ID
    lead_id = "4466349480575764737"
    # 跟单人数阈值
    threshold = 1000
    # 每分钟检查一次（60秒）
    check_interval = 60
    # 错误计数器
    error_count = 0
    # 最大错误次数
    max_error_count = 5

    logger.info("开始监控数据")

    while True:
        try:
            # 调用parse_binance_lead_data获取数据
            result = parse_binance_lead_data(lead_id)

            if result and 'current_copy_count' in result:
                current_copy_count = result['current_copy_count']
                logger.info(f"领单者 {lead_id} 当前跟单人数: {current_copy_count}")

                # 重置错误计数器
                error_count = 0

                # 检查跟单人数是否低于阈值
                if current_copy_count < threshold:
                    message = f"领单者 {lead_id} 跟单人数低于{threshold}，当前为 {current_copy_count}"
                    logger.warning(message)
                    dd_sender(message)
                else:
                    logger.info(f"跟单人数 {current_copy_count} 正常，超过阈值 {threshold}")

            else:
                error_count += 1
                error_message = f"无法获取领单者 {lead_id} 的数据 (错误次数: {error_count})"
                logger.error(error_message)
                dd_sender(error_message)

                # 检查是否连续错误超过最大次数
                if error_count >= max_error_count:
                    critical_message = f"监控程序连续错误 {error_count} 次，领单者 {lead_id} 数据获取失败"
                    logger.error(critical_message)
                    dd_sender(critical_message)

        except Exception as e:
            error_count += 1
            error_message = f"程序运行出错: {str(e)} (错误次数: {error_count})"
            logger.error(error_message)
            dd_sender(error_message)

            # 检查是否连续错误超过最大次数
            if error_count >= max_error_count:
                critical_message = f"监控程序连续错误 {error_count} 次，异常: {str(e)}"
                logger.error(critical_message)
                dd_sender(critical_message)

        # 等待指定间隔时间
        time.sleep(check_interval)


if __name__ == "__main__":
    main()