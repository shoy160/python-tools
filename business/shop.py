# coding=utf-8
import uuid
from helper.mysql import get_v3_connect


class ShopService():
    def __init__(self, sql_path='doc/update.sql'):
        self.__city_cache = {}
        self.__unit_cache = {}
        self.__sql_path = sql_path

    def __save_sql(self, sql):
        ''' 保存sql
        '''
        with open(self.__sql_path, 'a+', encoding='utf-8') as f:
            f.write('%s;\n' % sql)

    def __save_unknown(self, shop):
        with open('doc/unknown.csv', 'a+', encoding='utf-8') as f:
            line = [str(i) for i in shop]
            f.write('%s\n' % (','.join(line)))

    def __get_city(self, city_name):
        ''' 获取城市编码
        :param  city_name:str   城市名称
        '''
        if len(self.__city_cache) > 0:
            if city_name in self.__city_cache:
                return self.__city_cache[city_name]
            return None
        with get_v3_connect('main') as cursor:
            sql = 'select `code`,`name` from `t_areas` where `depth`=2'
            cursor.execute(sql)
            results = cursor.fetchall()
        for item in results:
            self.__city_cache.setdefault(item['name'], item['code'])
        if city_name in self.__city_cache:
            return self.__city_cache[city_name]
        return None

    def __get_shop(self, shop_name):
        ''' 获取店铺信息
        '''
        with get_v3_connect('user') as cursor:
            sql = 'select `id`,`name`,`alias`,`addr_code`,`unit_id`,`unit_name`,`state` from `t_shop` where `name`=%s'
            cursor.execute(sql, [shop_name])
            return cursor.fetchone()

    def __get_shop_id(self, shop_id):
        ''' 获取店铺信息
        '''
        with get_v3_connect('user') as cursor:
            sql = 'select `id`,`name`,`alias`,`addr_code`,`unit_id`,`unit_name`,`state` from `t_shop` where `id`=%s'
            cursor.execute(sql, [shop_id])
            return cursor.fetchone()

    def __get_unit(self, unit_name):
        ''' 获取 OR 创建机构
        '''
        if unit_name in self.__unit_cache:
            return self.__unit_cache[unit_name]
        with get_v3_connect('user') as cursor:
            sql = 'select `id`,`name` from `t_unit` where `name`=%s'
            cursor.execute(sql, [unit_name])
            unit = cursor.fetchone()
            if unit != None:
                self.__unit_cache.setdefault(unit_name, unit)
                return unit
            # 新建
            id = str(uuid.uuid1()).replace('-', '')
            # todo number,code
            sql = 'insert into `t_unit` (`id`,`type`,`parent_id`,`deep`,`number`,`code`,`name`,`alias`,`state`,`create_time`) values ("%s",4,"",1,"","","%s","%s",0,now())' % (
                id, unit_name, unit_name)
            self.__save_sql(sql)
            unit = {'id': id, 'name': unit_name}
            self.__unit_cache.setdefault(unit_name, unit)
            return unit

    def __check_area(self, shop, city):
        ''' 检测区域信息
        '''
        # city
        if city == None or city == '':
            return None
        city_code = self.__get_city(city)
        if city_code == None:
            print('unknown city:%s' % city)
            return None
        # 更新city
        current_code = shop['addr_code']
        # 不相等 且 不是下级
        if current_code == None or (current_code != city_code and not current_code.startswith(city_code[:4])):
            print('update code %s, %s' % (shop['id'], city_code))
            return city_code
        return None

    def __check_unit(self, shop, unit_name):
        ''' 检测集团信息
        '''
        if unit_name == None or unit_name == '' or unit_name == '单店':
            return None
        unit = self.__get_unit(unit_name)
        if unit == None:
            print('unknown unit:%s' % unit_name)
            return None
        unit_id = unit['id']
        # 更新unit
        if shop['unit_id'] != unit_id:
            print('update unit %s,%s' % (shop['id'], unit_id))
            return unit_id
        return None

    def check_shop(self, line, unknow_fn=lambda x: print(x)):
        ''' 检测4s店铺信息
        '''
        if len(line) < 7:
            print('error line : %s' % (','.join(line)))
            unknow_fn(line)
            return
        province = line[0]
        city = line[1]
        unit = line[2]
        name = line[3]
        alias = line[4]
        time = line[5]
        state = line[6]
        if len(line) > 7:
            id = line[7]
        shop = self.__get_shop(name) if id == None else self.__get_shop_id(id)
        if shop == None:
            print('unknow name %s' % name)
            unknow_fn(line)
            return
        print(shop)
        city_code = self.__check_area(shop, city)
        unit_id = self.__check_unit(shop, unit)
        current_state = shop['state']
        # state change logic
        state_change = False
        if state == -400 and current_state >= 0:
            state_change = True
        if not state_change and city_code == None and unit_id == None and name == shop['name']:
            # 没有修改
            print('no change:%s' % name)
            return
        sql = 'update `t_shop` set '
        if city_code != None:
            sql += '`addr_code`="%s",' % city_code
        if unit_id != None:
            sql += '`unit_id`="%s",`unit_name`="%s",' % (unit_id, unit)
        # todo 状态
        if state_change:
            sql += '`state`=%d,' % state
        if name != shop['name']:
            sql += '`name`="%s",' % name
        # 名字
        sql = sql[:-1] + ' where `id`="%s"' % shop['id']
        self.__save_sql(sql)

# 1.原4s店已删除的，表格不是红色的怎么处理？ -- 以原数据为准
# 2.addr_code存储的节点不确定，有些是市，有些是省，有些是街道 -- 判断是否是下级，是下级也不处理
# 3.unit的number,code怎么生成？
# 4.4s集团单店？ --不要了
# 5.未找到的4s店怎么处理？大约14条
