# import paddle.fluid
# paddle.fluid.install_check.run_check()
import os
import sys
import json
import six
import paddlehub as hub


def cut_pictures():
    ''' 智能抠图 '''
    # hub install deeplabv3p_xception65_humanseg=1.0
    # 1.加载模型
    humanseg = hub.Module(name="deeplabv3p_xception65_humanseg")

    # 2.指定待抠图图片目录
    path = '../doc/pictures/'
    files = []
    dirs = os.listdir(path)
    for diretion in dirs:
        files.append(path + diretion)

    # 3.抠图
    results = humanseg.segmentation(data={"image": files})

    for result in results:
        print(result['origin'])
        print(result['processed'])


def porn_check(*texts):
    ''' 色情检测 '''
    # hub install porn_detection_lstm=1.0
    porn_detection_lstm = hub.Module(name="porn_detection_lstm")

    # test_text = ["黄片下载", "打击黄牛党"]

    input_dict = {"text": texts}

    results = porn_detection_lstm.detection(data=input_dict)

    for index, text in enumerate(texts):
        results[index]["text"] = text
    for index, result in enumerate(results):
        if six.PY2:
            print(
                json.dumps(results[index], encoding="utf8", ensure_ascii=False))
        else:
            print(results[index])


def senta_check(*texts):
    '''情感倾向分析'''
    # hub install senta_lstm
    senta = hub.Module(name="senta_lstm")
    # test_text = ["这家餐厅很好吃", "这部电影真的很差劲"]
    input_dict = {"text": texts}
    results = senta.sentiment_classify(data=input_dict)

    for result in results:
        print(result['text'])
        print(result['sentiment_label'])  # 1.积极，0.消极
        print(result['sentiment_key'])
        print(result['positive_probs'])  # 积极概率
        print(result['negative_probs'])  # 消极概率


if __name__ == "__main__":
    # porn_check("黄片下载", "打击黄牛党")
    senta_check("这家餐厅很好吃", "这部电影真的很差劲")
