# coding=utf-8
from ml_vcode import ML_VCode

if __name__ == "__main__":
    ml = ML_VCode('wordpress', 'sources\\wordpress_codes')
    # ml.train_model()
    # codes = ml.recog_image('sources\\wordpress_codes\\2D25.png')
    ml.convert_to_onnx()
    # print(codes)
