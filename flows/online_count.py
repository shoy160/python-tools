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


def get_test_conn():
    return get_connection("101.206.8.33", 30285, "test", "Yz@5cSjvWrB", "db_test")


def parse_date(date_str):
    if isinstance(date_str, datetime.datetime):
        return date_str
    return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def get_count(date_str, minutes=5, pre_hours=12):
    date = parse_date(date_str)
    end = date + datetime.timedelta(minutes=minutes)
    online_start = date + datetime.timedelta(hours=-pre_hours)
    # print(date, end)
    db = get_test_conn()
    try:
        sql = "select count(1) as count from online_auth_log_1 where fd_onlineTime >='%s' AND fd_onlineTime<'%s' AND (fd_offlineTime >='%s' OR fd_offlineTime is null)" % (
            online_start, end, date)
        with db.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            count = row['count']
            # print(count)
            return (date, count)
    except TimeoutError as err:
        print("timeout error: {0}".format(err))
    else:
        print("other error")
    finally:
        db.close()


def insert_counts(counts=[]):
    ''' 新增在线数数据
    '''
    db = get_test_conn()
    sql = "insert into online_count (fd_time,fd_count) values (%s,%s)"
    try:
        with db.cursor() as cursor:
            cursor.executemany(sql, counts)
            db.commit()
    except:
        db.rollback()
    finally:
        db.close()


def get_count_between(start_str, end_str, minutes=5):
    start = parse_date(start_str)
    end = parse_date(end_str)
    with ThreadPoolExecutor(max_workers=5) as executor:
        task_list = []
        while True:
            if start >= end:
                break
            task = executor.submit(get_count, start, minutes)
            task_list.append(task)
            start += datetime.timedelta(minutes=minutes)
        counts = []
        for future in as_completed(task_list):
            date, count = future.result()
            print(date, count)
            counts.append((date, count))
        print(len(counts))
        # insert_counts(counts)


if __name__ == "__main__":
    time_start = datetime.datetime.now()
    get_count_between('2020-10-01 00:00:00', '2020-10-02 00:00:00')
    time_end = datetime.datetime.now()
    print('use time', time_end-time_start, 's')
