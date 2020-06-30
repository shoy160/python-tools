# coding=utf-8

import requests
import urllib.request
from openpyxl import Workbook, load_workbook
from openxls import read_xlsx
from helper.mysql import get_v2_connect
import time
import traceback

requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
start_index = 664


def sync_maker(install_id):
    url = 'http://open.i-cbao.com//sys/synchro-install'
    token = '0e28c3c68a5c2f4f2f31599579c29e87:584cca8d67207a38ff88fdacb19253bf02d12a278a5a72535e53c3b0acf3b9a30fe977fa44129ff7dbe985c0cc877cb9522dff00107954123fe9d094a6474c5b073d311ed8f7855896bbf6615f949f566b8e678b188aefb1e328b6dd7d6df0ce23e1600dd38cad6cdda15ba9777923d689ad16cc94fbd33ab4fb9cf2169c6f43ef040e31864f81da05e646f85095ef95d94fa4970bd3dc79'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }
    payload = {
        'list[]': install_id,
        'token': token
    }

    s = requests.session()
    s.keep_alive = False
    response = s.request('POST', url, data=payload, headers=headers)
    if response.status_code != 200:
        print(response.status_code)
        return False
    json = response.json()
    if json['status'] == False:
        print(json)
    return json['status']


def get_policy_list():
    lines = read_xlsx('D:\work\other\需处理明细.xlsx')
    sql = 'SELECT d.Id,d.Process,d.ProcessStatus FROM to_order as o left join to_dispatch as d on o.Id=d.orderid WHERE o.PolicyNumber="%s" LIMIT 1'
    index = start_index
    for row in lines[index:]:
        policy = row[1]
        print(policy)
        try:
            with get_v2_connect() as cursor:
                cursor.execute(sql, [policy])
                install = cursor.fetchone()
                print(install)
                install_id = install['Id']
                result = sync_maker(install_id)
                if result == False:
                    print('\033[31m同步失败：%s -> %s,%s\033[0m' %
                          (index, policy, install_id))
                else:
                    print('\033[32m同步成功：%s -> %s,%s\033[0m' %
                          (index, policy, install_id))            
        except:
            traceback.print_exc()
            print('\033[31m同步失败：%s -> %s\033[0m' % (index, policy))
            # break
        finally:
            index += 1
        break
        # time.sleep(0.5)


if __name__ == "__main__":
    get_policy_list()
