from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions

def getVehicle_type(key):
    # 构建车辆类型
    dict = {'n02701002': '中型车',
            'n02814533': '中型车',
            'n02930766': '小型车',
            'n03100240': '小型车',
            'n03384352': '小型车',
            'n03393912': '大型车',
            'n03417042': '大型车',
            'n03594945': '小型车',
            'n03670208': '小型车',
            'n03770679': '中型车',
            'n03796401': '大型车',
            'n038958662': '大型车',
            'n03930630': '小型车',
            'n03977966': '小型车',
            'n04037443': '小型车',
            'n04065272': '中型车',
            'n04146614': '中型车',
            'n04285008': '小型车',
            'n04461696': '中型车',
            'n04467665': '大型车'}
    vehicle_type = dict.get(key, "未找到匹配车型")
    return vehicle_type

import numpy as np
import cv2


def get_result(path):
    # 导入模型
    model = VGG16()
    # print(model.summary())

    # 导入预测图片
    # load an image from file
    # imageas = np.asarray(bytearray(path), dtype="uint8")
    # query = cv2.imdecode(imageas, cv2.IMREAD_COLOR)

    from PIL import Image
    # img = Image.fromarray(path)
    image = cv2.resize(path,(224,224))
    # image = load_img(img, target_size=(224, 224))
    # image = path
    # convert the image pixels to a numpy array
    image = img_to_array(image)

    # reshape data for the model
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))

    # 对图片进行预测
    # prepare the image for the VGG model
    image = preprocess_input(image)
    # print(image)

    # predict the probability across all output classes
    yhat = model.predict(image)

    # convert the probabilities to class labels
    label = decode_predictions(yhat)
    # retrieve the most likely result, e.g. highest probability
    label = label[0][0]
    # print(label)
    # print the classification
    # print('%s (%.2f%%)' % (label[1], label[2] * 100))
    # print(label[0])

    return (getVehicle_type(label[0]))

# path = '03.jpg'
# result = get_result(path)
# print(result)




