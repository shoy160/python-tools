# coding=utf-8
import pymysql

def get_connect():
    '''获取Mysql数据库游标
    '''
    db = pymysql.connect(host="175.153.165.102", port=23306, user="root",
                         passwd="byDmp3l6fO8MQGrz", db="db_mall", charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()
    return cursor

def transfer(url):
    ''' 转存图片
    '''
    
    
