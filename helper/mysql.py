# coding=utf-8
import pymysql


def get_v2_connect():
    '''获取Mysql数据库游标
    '''
    db = pymysql.connect(host="220.167.101.61", port=33060, user="root",
                         passwd="icb@pwd159+-*/", db="icbv2db", charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()
    return cursor


def get_v3_connect(db_name):
    '''获取Mysql数据库游标
    '''
    # db_name = 'db_v3_%s' % db_name
    # db = pymysql.connect(host="121.43.162.235", port=33060, user="root",
    #                      passwd="Icb@pwd159+-*/", db=db_name, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    db_name = 'db_%s_v3' % db_name
    db = pymysql.connect(host="192.168.0.250", port=3306, user="root",
                         passwd="icb@888", db=db_name, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()
    return cursor