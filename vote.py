import requests
import random
from singer import Singer
import time

url = "https://mp.weixin.qq.com/mp/newappmsgvote"


def random_str(len=12):
    LETTERS = '0123456789ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba'
    return ''.join(random.choice(LETTERS) for x in range(len))


def vote():
    # payload = 'action=vote&__biz=MzU5MTQ4ODczMg%3A%3A&uin=MjY3NTc1MjcyMg%3A%3A&key=f5973dc8ca5ea0d095183eee7714746be340ee76a80f73cef404baf89d376b48f2128968de1a056315a95b58eb01c1cad7f9fade24985d7b327ffdd617d3d4dcef6cfb7d3cc3402ef61b126b51009c62a1de71a9025d1192c63f2d6f947ffc1dbb762c32e653a477289946d3927b44a5573c42e035b97c3fedf9d26ae40954b7&pass_ticket=U%2FJhDBPXLigU63BZEgpFehGudPy8Mew1oZvbaWfUA8qz9b0kb3SYSDN54Ro6nuVu5&appmsg_token=1098_IfgcnUzQYRxVTaJoy7J1dGu_2qmGgZuNXKc22ZMbEoCYNP_gBxrSp-4MhdokebNQMJcSGKBlr3IOtkkP&f=json&json=%7B%22super_vote_item%22%3A%5B%7B%22vote_id%22%3A478232173%2C%22item_idx_list%22%3A%7B%22item_idx%22%3A%5B%224%22%5D%7D%7D%5D%2C%22super_vote_id%22%3A478232170%7D&idx=2&mid=2247489892&wxtoken=777'
    # uin = random.randint(2100000000, 3000000000)
    payload = {
        "action": "vote",
        "__biz": "MzU5MTQ4ODczMg==",
        "uin": "MjE4OTcyOTM5MQ==",
        "key": "edbc4005805c8af77a8f4e084cede5734d9e28c79654e1b614a4b4ef2fc984c311e624d8e86539c20598a0e535037ea0a36e25552d242106c40c19a91dda759e189f7688cb20d2e98cffaf14d9f37bf25b0cf59884711f3eda71e8f5c057a8f3bd61cdcc69419a6a2424446952ac91e8c30d186c26a3bf221db07e7012fc2c4c",
        # "pass_ticket": "1VWEXqoBuJtSjfm3XbiC80oSGoqm0k7Kv922jWoag1vIIsn4hujY4xoSauOQEpRb",
        # "appmsg_token": "1098_VHVFrUsZtuS4TcTU6GujzIAqzwvfDWu7zzUYT92SaSjWkhtGUSJFM1D4RPbkZR1bJKPNpGRj3hsdOB7C",
        "pass_ticket": random_str(64),
        "appmsg_token": str(random.randint(1000, 3000)) + "_" + random_str(80),
        "f": "json",
        "json": "{\"super_vote_item\":[{\"vote_id\":478232173,\"item_idx_list\":{\"item_idx\":[\"4\"]}}],\"super_vote_id\":478232170}",
        # "idx":2,
        "idx": random.randint(1, 100),
        # "mid": 2247489892,
        "mid": random.randint(2200000000, 2500000000),
        # "wxtoken": 777,
        "wxtoken": random.randint(200, 1000)
    }
    # print(payload)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1316.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2875.116 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat',
        'accept-encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def task(index):
    logger = Singer.logger('vote_task')
    logger.info('running vote task %s', index)
    vote()
    time.sleep(0.3)


if __name__ == "__main__":
    # vote()
    # print(random_str(32))
    with Singer.executor() as executor:
        for i in range(10):
            executor.start(task, i)
        executor.wait_complete()
