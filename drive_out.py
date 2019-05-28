from predict import get_result as gs
from kears_vgg import get_result as gp
from paytime import ShareToPay
import numpy as np
import datetime
import cv2
import time
import os
import json
import pymysql
from DBUtils.PooledDB import PooledDB
import urllib.request
import urllib.parse
import pickle
import requests
from PIL import Image
import numpy as np


class DriveOut(object):
    def __init__(self):
        self.__folder_path = 'images'
        self.__identification = self.identification()
    
    def get_picture(self):
        folder_path = self.__folder_path
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()
            cv2.imshow('frame', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('s'):
                timestr = time.strftime('%Y%m%d%H%M%S', time.localtime())
                isExists = os.path.exists(folder_path)
                if not isExists:
                    os.mkdir(folder_path)
                cv2.imwrite(os.path.join(folder_path, 'out'+timestr+'.jpg'), frame)
                break
            elif k == ord('q'):
                break
        capture.release()
        cv2.destroyAllWindows()
        data = {}
        data['frame'] = frame
        data['time'] = timestr
        return data

    def identification(self):
        data = self.get_picture()
        frame = data['frame']
        out_time = data['time']
        out_dt = datetime.datetime.strptime(out_time, "%Y%m%d%H%M%S")
        # car_sign = gs(frame)
        car_sign = "冀G88888"
        for root, dirs, files in os.walk('images'):
            for file in files:
                if os.path.splitext(file)[0][3:] == out_time:
                    out_picture = file
        result = self.query_db(car_sign)
        if result is None:
            code = 1003
            data = ""
            msg = "未检测到该车辆"
            return json.dumps({"code":code, "data":data, "msg":msg})
        number_plate = result[0]
        plate_picture = result[1]
        entry_time = result[2]
        entry_time_str = entry_time.strftime('%Y%m%d%H%M%S')
        
        car_type = result[3]
        pid = 1
        sendurl = 'http://0.0.0.0:8001/api/parkbackend/chargestandard'

        params = 'pid=%s&car_type=%s' % (pid, car_type)

        wp = urllib.request.urlopen(sendurl + "?" + params)
        content = wp.read()
        str1 = str(content, encoding="utf-8")
        data = eval(str1)
        if data['code'] != 1000:
            return False
        result_data = data['data']
        f_time = result_data[0]['start_time']
        f_time = f_time[0:2] + f_time[3:5] + f_time[6:]
        s_time = result_data[0]['end_time']
        s_time = s_time[0:2] + s_time[3:5] + s_time[6:]
        early_money = float(result_data[0]['night_money'])
        day_money = float(result_data[0]['day_money'])
        night_money = float(result_data[0]['night_money'])
        all_day_money = float(result_data[0]['all_day_money'])
        per_se_money = result_data[0]['time_unit']
        result = ShareToPay(entry_time_str, out_time, f_time, s_time, early_money, day_money, night_money,
                             all_day_money, per_se_money)
        total_money = result.get_money()["total_money"]
        print(total_money)

        uid = 1
        pid = 1
        number_plate = car_sign
        entry_time = entry_time
        exit_time = out_time
        # folder_path = self.__folder_path
        # entry_file = open(folder_path+'/' + 'in' + entry_time_str + '.jpg', 'rb')
        # entry_content = pickle.dumps(entry_file.read())
        # exit_file = open(folder_path+'/' + 'out' + str(exit_time) + '.jpg', 'rb')
        # exit_content = pickle.dumps(exit_file.read())
        # entry_picture = entry_file
        # exit_picture = exit_file
        total_time = out_dt - entry_time
        total_time = round(total_time.seconds/60)
        total_money = total_money
        payment_mode_id = 1
        # self.save_record(uid, pid, number_plate, entry_time, exit_time, entry_picture, exit_picture, total_time, total_money, payment_mode_id)
        self.save_record(uid, pid, number_plate, entry_time, exit_time, total_time, total_money, payment_mode_id)

        self.delete_tem_db(car_sign, entry_time)
        return True


    def query_db(self, car_sign):
        pool = PooledDB(pymysql, 5, host='localhost', user='root', passwd='123456', db='uftc_front_db', port=3306, setsession=[
            'SET AUTOCOMMIT = 1'])  # 5为连接池里的最少连接数，setsession=['SET AUTOCOMMIT = 1']是用来设置线程池是否打开自动更新的配置，0为False，1为True
        db = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
        cursor = db.cursor()
        sql = "select * from temporaryrecord where number_plate='%s'" % (car_sign)
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
        except:
            print("error")
        cursor.close()
        db.close()
        return result

    def save_record(self, uid, pid, number_plate, entry_time, exit_time, total_time, total_money, payment_mode_id):
        data_dict = {"uid":uid, "pid":pid, "number_plate":number_plate, "entry_time":entry_time, "exit_time":exit_time, "total_time":total_time, "total_money":total_money, "payment_mode_id":payment_mode_id}
        entry_time_str = entry_time.strftime('%Y%m%d%H%M%S')
        folder_path = self.__folder_path
        heads = {'content-type':'application/json;charset=UTF-8'}
        # data_string = urllib.parse.urlencode(data_dict)
        # last_data = bytes(data_string, encoding='utf-8')
        files = {'file1': ('in' + entry_time_str + '.jpg', open(folder_path+'/'+ 'in' + entry_time_str + '.jpg', 'rb'), 'jpg'),
                 'file2': ('out' + exit_time + '.jpg', open(folder_path + '/' + 'out' + exit_time + '.jpg', 'rb'), 'jpg')}
        sendurl = 'http://0.0.0.0:8001/api/backend/parkingrecord'
        # urllib.request.urlopen(sendurl, data=last_data)
        # requests.post(sendurl, data=data_dict, files=files, headers=heads)
        requests.post(sendurl, data=data_dict, files=files)
        return True

    def delete_tem_db(self, car_sign, entry_time):
        pool = PooledDB(pymysql, 5, host='localhost', user='root', passwd='123456', db='uftc_front_db', port=3306, setsession=['SET AUTOCOMMIT = 1'])
        db = pool.connection()
        cursor = db.cursor()
        sql = "delete from temporaryrecord where number_plate='%s' and entry_time='%s'" % (car_sign, entry_time)
        print("###", sql)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        cursor.close()
        db.close()
        return True


def connect_mysql():
    pool = PooledDB(pymysql, 5, host='localhost', user='root', passwd='123456', db='uftc_front_db', port=3306,
                    setsession=['SET AUTOCOMMIT = 1'])
    try:
        db = pool.connection()
    except Exception as err:
        raise err
    return db


def create_temporary_record():
    db = connect_mysql()
    cursor = db.cursor()
    sql = """create table if not exists temporaryrecord(
        number_plate VARCHAR(20) NOT NULL,
        plate_picture VARCHAR(100) NOT NULL,
        entry_time DATETIME(6) NOT NULL,
        car_type INT(11) NOT NULL)"""
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()
    db.close()
    return True


def create_parking_record():
    db = connect_mysql()
    cursor = db.cursor()
    sql = """create table if not exists parking_record(
        number_plate VARCHAR(20) NOT NULL,
        entry_time DATETIME(6) NOT NULL,
        exit_time DATETIME(6) NOT NULL,
        entry_picture VARCHAR(100) NOT NULL,
        exit_picture VARCHAR(100) NOT NULL,
        total_time INT(11) NOT NULL,
        total_money DECIMAL(8, 2) NOT NULL,
        car_type INT(11) NOT NULL)"""
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    cursor.close()
    db.close()
    return True


if __name__ == '__main__':
    create_temporary_record()
    create_parking_record()
    DriveOut()