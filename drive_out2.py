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
        self.__camera = self.camera()


    def camera(self):
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()
            cv2.imshow('frame', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('s'):
                out_time_str = time.strftime('%Y%m%d%H%M%S', time.localtime())
                car_sign_list = gs(frame)
                car_sign = "".join(car_sign_list)
                print(car_sign)
                if car_sign_list == []:
                    code = 1002
                    data = ""
                    msg = "未识别到车辆，请手动录入"
                    continue
                result = self.query_carinfo(car_sign)
                if result is None:
                    code = 1003
                    data = ""
                    msg = "未检测到该车辆驶入信息"
                    continue
                number_plate = result[0]
                entry_picture = result[1]
                entry_time = result[2]
                car_type = result[3]
                entry_time_str = entry_time.strftime('%Y%m%d%H%M%S')
                folder_path = self.__folder_path
                is_Exists = os.path.exists(folder_path)
                try:
                    if not is_Exists:
                        os.mkdir(folder_path)
                except Exception as e:
                    raise e
                frame_name = 'out' + out_time_str + '.jpg'
                try:
                    cv2.imwrite(os.path.join(folder_path, frame_name), frame)
                except Exception as e:
                    raise e
                for dir_path, dir_names, file_names in os.walk(folder_path):
                    for file_name in file_names:
                        if file_name == frame_name:
                            out_file_path = dir_path + '/' + file_name
                pid = 1
                charge_standard = self.get_charge_standard(pid, car_type)
                if not charge_standard:
                    code = 1004
                    data = ""
                    msg = "停车场未建立收费标准"
                    continue
                charge_standard = json.loads(charge_standard)
                f_time = charge_standard['f_time']
                s_time = charge_standard['s_time']
                early_money = charge_standard['early_money']
                day_money = charge_standard['day_money']
                night_money = charge_standard['night_money']
                all_day_money = charge_standard['night_money']
                per_se_money = charge_standard['per_se_money']
                result = ShareToPay(entry_time_str, out_time_str, f_time, s_time, early_money, day_money, night_money,
                                    all_day_money, per_se_money)
                total_money = result.get_money()["total_money"]
                print(total_money)
                uid = 1
                entry_time = entry_time
                exit_time = datetime.datetime.strptime(out_time_str, "%Y%m%d%H%M%S")
                total_time = exit_time - entry_time
                total_time = round(total_time.seconds / 60)
                total_money = total_money
                payment_mode_id = 1
                try:
                    self.save_record(uid, pid, number_plate, entry_time, exit_time, total_time, total_money, payment_mode_id)
                except Exception as e:
                    raise e
                try:
                    self.save_record_local(number_plate, entry_time, exit_time, entry_picture, out_file_path, total_time, total_money, car_type)
                except Exception as e:
                    raise e
                try:
                    self.delete_tem_db(car_sign, entry_time)
                except Exception as e:
                    raise e


    def get_charge_standard(self, pid, car_type):
        params = 'pid=%s&car_type=%s' % (pid, car_type)
        sendurl = 'http://0.0.0.0:8001/api/parkbackend/chargestandard'
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
        data = {}
        data["f_time"] = f_time
        data["s_time"] = s_time
        data["early_money"] = early_money
        data["day_money"] = day_money
        data["night_money"] = night_money
        data["all_day_money"] = all_day_money
        data["per_se_money"] = per_se_money
        return json.dumps(data)


    def query_carinfo(self, car_sign):
        db = connect_mysql()
        cursor = db.cursor()
        sql = "select * from temporary_record where number_plate='%s'" % (car_sign)
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
        except Exception as e:
            raise e
        cursor.close()
        db.close()
        return result

    def save_record(self, uid, pid, number_plate, entry_time, exit_time, total_time, total_money, payment_mode_id):
        data_dict = {"uid":uid, "pid":pid, "number_plate":number_plate, "entry_time":entry_time, "exit_time":exit_time, "total_time":total_time, "total_money":total_money, "payment_mode_id":payment_mode_id}
        entry_time_str = entry_time.strftime('%Y%m%d%H%M%S')
        exit_time_str = exit_time.strftime('%Y%m%d%H%M%S')
        folder_path = self.__folder_path
        heads = {'content-type':'application/json;charset=UTF-8'}
        files = {'file1': ('in' + entry_time_str + '.jpg', open(folder_path+'/'+ 'in' + entry_time_str + '.jpg', 'rb'), 'jpg'),
                 'file2': ('out' + exit_time_str + '.jpg', open(folder_path + '/' + 'out' + exit_time_str + '.jpg', 'rb'), 'jpg')}
        sendurl = 'http://0.0.0.0:8001/api/backend/parkingrecord'
        # requests.post(sendurl, data=data_dict, files=files, headers=heads)
        requests.post(sendurl, data=data_dict, files=files)
        return True

    def save_record_local(self, number_plate, entry_time, exit_time, entry_picture, exit_picture, total_time, total_money, car_type):
        db = connect_mysql()
        cursor = db.cursor()
        try:
            sql = "insert into parking_record(number_plate, entry_time, exit_time, entry_picture, exit_picture, total_time, total_money, car_type) values ('%s', '%s', '%s', '%s', '%s', %d, %f, %d)" % (number_plate, entry_time, exit_time, entry_picture, exit_picture, total_time, total_money, car_type)
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            db.close()


    def delete_tem_db(self, car_sign, entry_time):
        db = connect_mysql()
        cursor = db.cursor()
        sql = "delete from temporary_record where number_plate='%s' and entry_time='%s'" % (car_sign, entry_time)
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
    create_parking_record()
    DriveOut()