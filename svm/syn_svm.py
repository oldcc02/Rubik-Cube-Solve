# -*- coding: utf-8 -*-
# File: my_test.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/9 11:22
import os
import cv2
import time
import joblib
import asyncio
import logging
import numpy as np

from sklearn import svm
from collections import Counter, defaultdict
from profiler import aio_profiler

# 日志器
logger = logging.getLogger()

# red green yellow white orange blur
color_class = ['R', 'G', 'Y', 'W', 'O', 'B']

# 允许的图片格式后缀
img_type = ['.jpg', '.png', '.jpeg']

# 测试数据集比例划分
proportion = 1 / 3


async def load_img(file_root_path: str) -> tuple:
    """
    加载所有图片，并返回所有图片数据的一维向量数组，和标注数组
    :param file_root_path: 图片根路径
    :return: res_mat, res_label
    """
    train_data_mat = []
    train_data_label = []
    test_data_mat = defaultdict(list)
    if not os.path.exists(file_root_path):
        await init_dir()
        return train_data_mat, train_data_label
    for c in color_class:
        color_dir_path = os.path.join(file_root_path, c)
        # 获取一个文件下的文件列表
        color_img_list = await get_file_list(color_dir_path)
        length = int(len(color_img_list) * proportion)
        if color_img_list:
            train_img_list = color_img_list[:-length]
            test_img_list = color_img_list[-length:]
            mat, label = await convert_img(train_img_list, c)
            t_mat, _ = await convert_img(test_img_list, c)
            train_data_mat.append(mat)
            train_data_label.append(label)
            test_data_mat[c].append(t_mat)
    res_mat = np.concatenate(train_data_mat, axis=0)
    res_label = np.concatenate(train_data_label, axis=0)

    return res_mat, res_label, test_data_mat


async def get_file_list(file_dir_path: str) -> list:
    """
    获取一个文件下的文件列表,并返回包含文件绝对路径的列表
    :param file_dir_path: 文件夹路径
    :return: ["file_absolute_path",...]
    """
    res = []
    for img_name in os.listdir(file_dir_path):
        sub = os.path.splitext(img_name)
        if sub[-1] in img_type:
            res.append(os.path.join(file_dir_path, img_name))

    return res


async def convert_img(color_img: list, c: str) -> tuple:
    """
    读取单个颜色文件夹下的所有图片并转换图片为一维向量
    :param color_img: 单个颜色文件夹路径
    :param c: 图片所属颜色分类
    :return: mat（单个文件夹下所有图片的数据），label（图片的标注）
    """

    img_num = len(color_img)
    # 1875 = 25*25*3
    mat = np.zeros((img_num, 1875))
    label = [c] * img_num

    for i, item in enumerate(color_img):
        try:
            # 图片向量
            img_arr = cv2.imread(item)
            # 图片向量调整为25*25
            img_arr = cv2.resize(img_arr, (25, 25), interpolation=cv2.INTER_CUBIC)
            # 归一化处理
            img_normal = (img_arr - np.min(img_arr)) / (np.max(img_arr) - np.min(img_arr))
            # 转为一维向量 1 * 1875
            img_arr2 = img_normal.reshape((1, -1))
            mat[i, :] = img_arr2
        except Exception as e:
            logger.error(f"{item} 图片读取失败！ \n line:{e.__traceback__.tb_lineno} \n error: {e}")
            label.pop()
            continue
    return mat, label


async def init_dir(dir_name: str = "imgs"):
    """
    在该py文件的上级目录初始化创建图片保存路径
    :param dir_name: 初始化文件夹名称
    |-- dir_name
        |- B
        |- G
        |- O
        |- R
        |- W
        |- Y
    """

    pre_path = os.path.dirname(os.getcwd())
    img_root_path = os.path.join(pre_path, dir_name)
    for c in color_class:
        color_class_dir = os.path.join(img_root_path, c)
        if os.path.exists(color_class_dir):
            continue
        os.makedirs(color_class_dir)


# @aio_profiler
async def create_svm(img_root_path):
    """
    构建svm模型,并保存模型到图片根路径
    :param img_root_path: 图片根目录路径
    """
    try:
        st = time.perf_counter()
        clf = svm.SVC(C=1.0, kernel='rbf')
        # 加载训练集、标签以及测试数据集
        mat, label, t_mat = await load_img(img_root_path)
        # 开始训练模型
        rf = clf.fit(mat, label)
        # 存储训练好的模型
        joblib.dump(rf, os.path.join(img_root_path, 'svm.model'))
        et = time.perf_counter()

        # 训练结果输出
        res = await predict_t_mat(clf, t_mat)
        t_num = sum([len(x[0]) for x in t_mat.values()])
        res['本次训练总结:\n'] = f"训练集数据为 {len(mat)} 张 " \
                           f"测试数据集为 {t_num} 张 " \
                           f"花费 {round((et - st), 4)}s"
        for k, v in res.items():
            print(k, v)
    except Exception as e:
        logger.info(e)


async def predict_t_mat(clf: svm.SVC, t_mat: defaultdict):
    """
    训练结果测试，可在后续调用中输出测试结果
    :param clf:完成训练的模型
    :param t_mat:测试数据集
    :return:predict_res
    """
    predict_res = defaultdict(str)
    for color, color_mat in t_mat.items():
        pass_ = 0
        for mat in color_mat:
            res = clf.predict(mat)
            res = Counter(res)
            pass_ = res[color]
        check = len(color_mat[0])
        predict_res[color] = f"共计测试 {check} 张，识别率为{round(pass_ / check, 2) * 100}%"

    return predict_res


if __name__ == '__main__':
    path = r"../imgs"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_svm(path))
