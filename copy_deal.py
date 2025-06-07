import hashlib
import json
import time
import logging
import pymongo
import requests

from api_requests import get_deal
connect = pymongo.MongoClient(
            'mongodb://root:Love3597320@127.0.0.1:27017/?authSource=admin',
            maxPoolSize=50,  # 设置连接池大小
            waitQueueTimeoutMS=1000  # 设置等待队列的超时时间
        )


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

class CopyDeal:
    def __init__(self):
        self.db = connect['sz_project']['copy_deal_data']
        self.search_id = '4466349480575764737'

    @staticmethod
    def md5_encrypt(text: str) -> str:
        encoded_text = text.encode('utf-8')

        # 创建 MD5 哈希对象并计算哈希值
        md5_hash = hashlib.md5(encoded_text)

        # 返回十六进制哈希值
        return md5_hash.hexdigest()

    def get_data_insert(self):

        retry_count = 0
        while True:

            data = get_deal(self.search_id)
            if not data:
                print("获取带单人数据失败 No data found, retrying...")
                retry_count += 1

                if retry_count >= 5:
                    dd_sender("获取带单人数据失败，连续5次未获取到数据，请检查网络或API状态。")
                    logging.error("获取带单人数据失败，连续5次未获取到数据，请检查网络或API状态。")
                    break

                time.sleep(5)
                continue

            for each_data in data:

                md5_str = self.md5_encrypt(str(each_data))
                if self.db.find_one({'_id': md5_str}):
                    # print(f"Data already exists: {md5_str}")
                    continue

                each_data['_id'] = md5_str
                self.db.insert_one(each_data)

                dd_data = {
                    '交易对': each_data.get('symbol', 'N/A'),
                    '交易方向': each_data.get('side', 'N/A'),
                    '成交价格': each_data.get('avgPrice', 'N/A'),
                    '成交数量': each_data.get('executedQty', 'N/A'),
                }

                dd_sender(f"{dd_data}")
            time.sleep(30)


if __name__ == "__main__":
    copy_deal = CopyDeal()
    copy_deal.get_data_insert()
