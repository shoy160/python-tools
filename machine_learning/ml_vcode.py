
import os
import time
import glob
import cv2
import pickle
import numpy as np
import imutils
import onnxmltools
from imutils import paths
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from keras.models import Sequential
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.core import Flatten, Dense
from keras.models import load_model

# pip install -r requirements.txt -i https://pypi.douban.com/simple


def resize_to_fit(image, width, height):
    """
    A helper function to resize an image to fit within a given size
    :param image: image to resize
    :param width: desired width in pixels
    :param height: desired height in pixels
    :return: the resized image
    """

    # grab the dimensions of the image, then initialize
    # the padding values
    (h, w) = image.shape[:2]

    # if the width is greater than the height then resize along
    # the width
    if w > h:
        image = imutils.resize(image, width=width)

    # otherwise, the height is greater than the width so resize
    # along the height
    else:
        image = imutils.resize(image, height=height)

    # determine the padding values for the width and height to
    # obtain the target dimensions
    padW = int((width - image.shape[1]) / 2.0)
    padH = int((height - image.shape[0]) / 2.0)

    # pad the image then apply one more resizing to handle any
    # rounding issues
    image = cv2.copyMakeBorder(image, padH, padH, padW, padW,
                               cv2.BORDER_REPLICATE)
    image = cv2.resize(image, (width, height))

    # return the pre-processed image
    return image


class ML_VCode:
    def __init__(self, name='vcode', dir='source', size=4):
        super().__init__()
        self.__source_dir = os.path.join(dir)
        self.__extract_dir = os.path.join(name, 'source')
        self.__model_file = os.path.join(name, '%s.hdf5' % name)
        self.__model_labels_file = os.path.join(name, '%s.dat' % name)
        self.__size = size

    def __log(self, msg, level='INFO'):
        print('[%s] %s: %s' % (str(level).upper(),
                               time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), msg))

    def __extract_image(self, gray):
        '''分离图片'''
        thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        contours, _ = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        letter_image_regions = []
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if w / h > 1.25:
                half_width = int(w / 2)
                letter_image_regions.append((x, y, half_width, h))
                letter_image_regions.append((x + half_width, y, half_width, h))
            else:
                letter_image_regions.append((x, y, w, h))

        if len(letter_image_regions) != self.__size:
            return None

        return sorted(letter_image_regions, key=lambda x: x[0])

    def __extract_files(self):
        ''' 分离模块 '''
        if os.path.exists(self.__extract_dir):
            return
        # 图片
        image_files = glob.glob(os.path.join(self.__source_dir, "*"))
        counts = {}
        for (i, image_file) in enumerate(image_files):
            self.__log("processing image {}/{}".format(i + 1, len(image_files)))
            filename = os.path.basename(image_file)
            correct_text = os.path.splitext(filename)[0]

            image = cv2.imread(image_file)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            gray = cv2.copyMakeBorder(gray, 8, 8, 8, 8, cv2.BORDER_REPLICATE)

            image_regions = self.__extract_image(gray)
            if image_regions is None:
                continue

            for letter_bounding_box, letter_text in zip(image_regions, correct_text):

                x, y, w, h = letter_bounding_box

                letter_image = gray[y - 2:y + h + 2, x - 2:x + w + 2]

                save_path = os.path.join(self.__extract_dir, letter_text)

                if not os.path.exists(save_path):
                    os.makedirs(save_path)

                count = counts.get(letter_text, 1)
                p = os.path.join(
                    save_path, "{}.png".format(str(count).zfill(6)))
                cv2.imwrite(p, letter_image)
                counts[letter_text] = count + 1

    def __get_date_label(self):
        ''' 获取数据集 '''
        self.__log('收集数据...')
        data = []
        labels = []
        for image_file in paths.list_images(self.__extract_dir):

            image = cv2.imread(image_file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            image = resize_to_fit(image, 20, 20)

            image = np.expand_dims(image, axis=2)

            label = image_file.split(os.path.sep)[-2]

            data.append(image)
            labels.append(label)
        return (data, labels)

    def train_model(self):
        ''' 训练模型    
        '''
        self.__extract_files()
        (data, labels) = self.__get_date_label()

        data = np.array(data, dtype="float") / 255.0
        labels = np.array(labels)

        (X_train, X_test, Y_train, Y_test) = train_test_split(
            data, labels, test_size=0.25, random_state=0)

        lb = LabelBinarizer().fit(Y_train)
        Y_train = lb.transform(Y_train)
        Y_test = lb.transform(Y_test)

        with open(self.__model_labels_file, "wb") as f:
            pickle.dump(lb, f)

        # 顺序模型
        model = Sequential()

        model.add(Conv2D(20, (5, 5), padding="same",
                         input_shape=(20, 20, 1), activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

        model.add(Conv2D(50, (5, 5), padding="same", activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

        model.add(Flatten())
        model.add(Dense(500, activation="relu"))

        model.add(Dense(32, activation="softmax"))

        model.compile(loss="categorical_crossentropy",
                      optimizer="adam", metrics=["accuracy"])

        model.fit(X_train, Y_train, validation_data=(
            X_test, Y_test), batch_size=32, epochs=10, verbose=1)
        self.__log('保存模型.')
        model.save(self.__model_file)

    def recog_image(self, path):
        ''' 识别 '''
        image = cv2.imread(path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.copyMakeBorder(gray, 20, 20, 20, 20, cv2.BORDER_REPLICATE)
        regions = self.__extract_image(gray)
        if regions is None:
            return ''
        with open(self.__model_labels_file, "rb") as f:
            labels = pickle.load(f)
        model = load_model(self.__model_file)

        predictions = []
        for (x, y, w, h) in regions:

            letter_image = gray[y - 2:y + h + 2, x - 2:x + w + 2]
            letter_image = resize_to_fit(letter_image, 20, 20)
            letter_image = np.expand_dims(letter_image, axis=2)
            letter_image = np.expand_dims(letter_image, axis=0)
            prediction = model.predict(letter_image)
            # print(prediction)
            transforms = labels.inverse_transform(prediction)
            # print(transforms)
            letter = transforms[0]
            predictions.append(letter)
            # cv2.rectangle(output, (x - 2, y - 2),
            #               (x + w + 4, y + h + 4), (0, 255, 0), 1)
            # cv2.putText(output, letter, (x - 5, y - 5),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
        return "".join(predictions)

    def convert_to_onnx(self):
        model = load_model(self.__model_file)
        onnx_model = onnxmltools.convert_keras(model, target_opset=7)
        onnxmltools.utils.save_model(
            onnx_model, self.__model_file.replace('.hdf5', '.onnx'))
