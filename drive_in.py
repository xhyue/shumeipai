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


class DriveIn(object):
    def __init__(self):
        self.__folder_path = 'images'
        self.__identification = self.identification()

    def get_picture(self):
        folder_path = self.__folder_path
        capture = cv2.VideoCapture(0)
        while (capture.isOpened()):
            ret, frame = capture.read()
            cv2.imshow('frame', frame)
            k = cv2.waitKey(1) & 0xFF
            if k == ord('s'):
                timestr = time.strftime('%Y%m%d%H%M%S', time.localtime())
                capture.release()
                cv2.destroyAllWindows()
                isExists = os.path.exists(folder_path)
                if not isExists:
                    os.mkdir(folder_path)
                cv2.imwrite(os.path.join(folder_path, 'in'+timestr+'.jpg'), frame)
                return {"frame":frame, 'time':timestr}
            elif k == ord('q'):
                break

    def identification(self):
        data = self.get_picture()
        frame = data['frame']
        in_time = data['time']
        car_type = gp(frame)
        car_sign = '冀G88888'
        # car_sign = gs(frame)
        # if car_sign == []:
        #     code = 1001
        #     data = ""
        #     msg = "未识别到车辆，请手动录入"
        #     return json.dumps({"code":code, "data":data, "msg":msg})
        # else:
        #     car_sign = '冀G88888'
        if car_type == "未找到匹配车型" or car_type == "小型车":
            car_type = 0
        elif car_type == '中型车':
            car_type = 1
        elif car_type == '大型车':
            car_type = 2
        for root, dirs, files in os.walk('images'):
            for file in files:
                if os.path.splitext(file)[0][2:] == in_time:
                    in_picture = file
        dataset_dir = "images/"
        image_filename = dataset_dir + in_picture
        # in_time = datetime.datetime.strptime(in_time, "%Y%m%d%H%M%S")
        self.create_db(car_type, car_sign, image_filename, in_time)
        return True

    def create_db(self, car_type, car_sign, image_filename, in_time):
        pool = PooledDB(pymysql, 5, host='localhost', user='root', passwd='123456', db='uftc_front_db', port=3306, setsession=[
            'SET AUTOCOMMIT = 1'])  # 5为连接池里的最少连接数，setsession=['SET AUTOCOMMIT = 1']是用来设置线程池是否打开自动更新的配置，0为False，1为True
        db = pool.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
        cursor = db.cursor()
        try:
            sql = "insert into temporaryrecord(car_type, number_plate, plate_picture, entry_time) values (%d, '%s', '%s', '%s')" % (car_type, car_sign, image_filename, in_time)
            cursor.execute(sql)
            db.commit()
        except:
            code = 1002
            data = ""
            msg = "数据有误，车辆驶入失败!"
            return json.dumps({"code":code, "data":data, "msg":msg})
        finally:
            cursor.close()
            db.close()


if __name__ == '__main__':
    DriveIn()
