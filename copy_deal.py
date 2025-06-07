import hashlib
import time

import pymongo
from api_requests import get_deal
connect = pymongo.MongoClient(
            'mongodb://root:Love3597320@127.0.0.1:27017/?authSource=admin',
            maxPoolSize=50,  # 设置连接池大小
            waitQueueTimeoutMS=1000  # 设置等待队列的超时时间
        )


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

        while True:

            data = get_deal(self.search_id)
            if not data:
                print("获取带单人数据失败 No data found, retrying...")
                time.sleep(5)
                continue

            for each_data in data:

                md5_str = self.md5_encrypt(str(each_data))
                if self.db.find_one({'_id': md5_str}):
                    print(f"Data already exists: {md5_str}")
                    continue

                each_data['_id'] = md5_str
                self.db.insert_one(each_data)

            time.sleep(30)


if __name__ == "__main__":
    copy_deal = CopyDeal()
    copy_deal.get_data_insert()
