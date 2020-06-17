# coding=utf-8
# 安装单
from helper.mysql import get_v3_connect

def query_device(page=1, size=20):
    with get_v3_connect('shield') as cursor:
        sql = 'SELECT `id`,`device_info` FROM `t_install` WHERE `device_info` IS NOT NULL AND `device_info`<>'''
        cursor.execute(sql)
        results = cursor.fetchall()