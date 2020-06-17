# coding=utf-8

# import json
# import requests
# import urllib.request
import time
import aiohttp
import asyncio

# requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
SFZH = 'xxx'
ZKZH = 'xxx'


async def reg(count):
    # s = requests.session()
    # s.keep_alive = False
    # await asyncio.sleep(2)
    url = 'https://zk.sceea.cn/RegExam/switchPage?resourceId=reg'
    payload = {
        'sfzh': SFZH,
        'zkzh': ZKZH,
        'kslb': 1,
        'mainIds': '0112',
        'qxname': '龙泉驿区',
        'xx_bm': '0132',
        'courseJson': [{"zy_bm": "W120102", "kc_bm": "02133"}]
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Cookie': 'JSESSIONID=9C5B7111F5F009BA2489389B9F17F403; UM_distinctid=17217c9e5d597-09ed91218aee6e-4313f6a-1fa400-17217c9e5d698e; SF_cookie_1=41647646; JSESSIONID=1D2E8670DDF9CCF44C9D39767D3FEBA8; allan=M723M7M7P57P56M7M72M72M75M7ZP5M7P5P5P599P552M7P5P55',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    # response = s.request('POST', url, data=payload, headers=headers)
    # data = response.text
    # 秒
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, data=payload) as response:
            data = await response.text()
            print("\033[32m[%s]->%s\033[0m\t%s" % (count, time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime()), data))
            return data


async def loop_reg(interval=2):
    count = 1
    while(True):
        result = await reg(count)
        if '已报考' in result:
            break
        # 秒
        await asyncio.sleep(interval)
        count = count+1


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loop_reg())
