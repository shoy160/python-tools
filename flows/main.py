# coding=utf-8
import pymysql
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_connection(ip, port, user, pwd, db):
    '''获取Mysql数据库游标
    '''
    db = pymysql.connect(host=ip, port=port, user=user,
                         passwd=pwd, db=db, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    return db


def get_zero_data(start_time):
    db = get_connection("", 3306,
                        "user", "", "db_flow")
    sql = "SELECT f.fd_id,f.fd_device_id,d.fd_ip,f.fd_port,f.fd_collection_time FROM sys_flow as f left JOIN sys_device as d on d.fd_id=f.fd_device_id WHERE f.fd_collection_time>=%s AND (f.fd_flow_out=0 OR f.fd_flow_in=0)"
    with db.cursor() as cursor:
        cursor.execute(sql, [start_time])
        return cursor.fetchall()


def update_zero_data(flow_in, flow_out, id):
    db = get_connection("", 3306,
                        "user", "", "db_flow")
    sql = "update sys_flow set fd_flow_in=%s,fd_flow_out=%s where fd_id=%s" % (
        flow_in, flow_out, id)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()


def get_data_future(item, map):
    if item["fd_id"] == 18722999:
        print('start')
    port = item['fd_port']
    time = item['fd_collection_time']
    deviceId = item['fd_ip']
    if deviceId in map:
        deviceId = map[deviceId]
    db = get_connection("192.168.5.237", 3306,
                        "test", "Yz@5cSjvWrB", "db_test")
    print(item['fd_ip'], deviceId, port, time)
    sql = 'SELECT * FROM sys_flow WHERE fd_device_id="%s" AND fd_port=%s AND fd_collection_time=%s LIMIT 1' % (
        deviceId, port, time)
    with db.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchone()
        return data


def update_zero_item(item, device_map):
    data = get_data_future(item, device_map)
    if data is not None:
        print("execute update for ", item['fd_id'])
        id = item['fd_id']
        flowIn = data['fd_flow_in']
        flowOut = data['fd_flow_out']
        update_zero_data(flowIn, flowOut, id)


def update_zero_list(zero_list, threads=5):
    device_map = {
        "192.168.5.81": "172.20.0.2",
        "192.168.5.82": "172.20.113.248",
        "192.168.5.83": "172.20.0.10",
        "192.168.5.84": "172.20.0.22",
        "192.168.5.85": "172.20.0.26",
        "192.168.5.86": "172.28.0.73",
        "192.168.5.87": "172.29.0.94",
        "192.168.5.88": "172.29.132.1",
        "192.168.5.89": "192.168.20.81",
        "192.168.5.90": "192.168.20.120",
        "192.168.5.91": "172.29.0.78",
        "192.168.5.92": "172.20.10.101"
    }
    print("find rows", len(zero_list))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        task_list = []
        for item in zero_list:
            task = executor.submit(update_zero_item, item, device_map)
            task_list.append(task)
        for _ in as_completed(task_list):
            pass


if __name__ == "__main__":
    # 1607875200 2020-12-14
    # 1606752000 2020-12-01
    # 1577808000 2020-01-01
    start = datetime.datetime.now()
    zero_list = get_zero_data(1606752000)
    update_zero_list(zero_list)
    time = datetime.datetime.now()-start
    print("use time", time, 's')
