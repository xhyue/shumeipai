from predict import get_result as gs
from kears_vgg import get_result as gp
import numpy as np
import datetime
import cv2
import time
import os
import json
import pymysql
from DBUtils.PooledDB import PooledDB
import serial


class DriveIn(object):
    def __init__(self):
        self.__folder_path = 'images'
        self.__camera = self.camera()


    def radar(self):
        while True:
            ser = serial.Serial('/dev/ttyUSB0', 115200)
            data = ser.read(9)
            data_h = data.hex()
            s = str(data_h[6]) + str(data_h[7]) + str(data_h[4]) + str(data_h[5])
            distance = int(s, 16)
            if distance >=3 and distance <= 5:
                break
        return True


    def camera(self):
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()
            # cv2.imshow('frame', frame)
            radar = self.radar()
            if radar:
            # k = cv2.waitKey(1) & 0xFF
            # if k == ord('s'):   # 触发条件
                in_time_str = time.strftime('%Y%m%d%H%M%S', time.localtime())
                car_type = gp(frame)
                car_sign_list = gs(frame)
                car_sign = "".join(car_sign_list)
                if car_type == "未找到匹配车型" or car_type == "小型车":
                    car_type_code = 0
                elif car_type == '中型车':
                    car_type_code = 1
                elif car_type == '大型车':
                    car_type_code = 2
                if car_sign_list == []:
                    code = 1001
                    data = ""
                    msg = "未识别到车辆，请手动录入"
                    continue
                folder_path = self.__folder_path
                is_Exists = os.path.exists(folder_path)
                try:
                    if not is_Exists:
                        os.mkdir(folder_path)
                except Exception as e:
                    raise e
                frame_name = 'in' + in_time_str + '.jpg'
                try:
                    cv2.imwrite(os.path.join(folder_path, frame_name), frame)
                except Exception as e:
                    raise e
                for dir_path, dir_names, file_names in os.walk(folder_path):
                    for file_name in file_names:
                        if file_name == frame_name:
                            file_path = dir_path + '/' + file_name
                in_time = datetime.datetime.strptime(in_time_str, "%Y%m%d%H%M%S")
                self.insert_carinfo(car_type_code, car_sign, file_path, in_time)

    def insert_carinfo(self, car_type_code, car_sign, file_path, in_time):
        db = connect_mysql()
        cursor = db.cursor()
        try:
            sql = "insert into temporary_record(car_type, number_plate, plate_picture, entry_time) values (%d, '%s', '%s', '%s')" % (car_type_code, car_sign, file_path, in_time)
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            db.close()


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
    sql = """create table if not exists temporary_record(
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


if __name__ == '__main__':
    # create_temporary_record()
    DriveIn()
