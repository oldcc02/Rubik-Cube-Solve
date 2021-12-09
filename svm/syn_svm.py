# -*- coding: utf-8 -*-
# File: my_test.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/9 11:22
import asyncio
import time

import cv2
import joblib
import numpy as np
from sklearn import svm

# from profiler import aio_profiler

import os

# red green yellow white orange blur
color_class = ['R', 'G', 'Y', 'W', 'O', 'B']
# 允许的图片格式后缀
img_type = ['.jpg', '.png', '.jpeg']


async def load_img(file_root_path: str) -> tuple:
    """
    加载所有图片，并返回所有图片数据的一维向量数组，和标注数组
    :param file_root_path: 图片根路径
    :return: res_mat, res_label
    """
    data_mat = []
    data_label = []
    if not os.path.exists(file_root_path):
        await init_dir()
        return data_mat, data_label
    for c in color_class:
        color_dir_path = os.path.join(file_root_path, c)
        # 获取一个文件下的文件列表
        color_img_list = await get_file_list(color_dir_path)
        if color_img_list:
            mat, label = await convert_img(color_img_list, c)
            data_mat.append(mat)
            data_label.append(label)
    res_mat = np.concatenate(data_mat, axis=0)
    res_label = np.concatenate(data_label, axis=0)

    return res_mat, res_label


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
        # 图片向量
        img_arr = cv2.imread(item)
        # 图片向量调整为25*25
        img_arr = cv2.resize(img_arr, (25, 25), interpolation=cv2.INTER_CUBIC)
        # 归一化处理
        img_normal = (img_arr - np.min(img_arr)) / (np.max(img_arr) - np.min(img_arr))
        # 转为一维向量 1 * 1875
        img_arr2 = img_normal.reshape((1, -1))
        mat[i, :] = img_arr2
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
    clf = svm.SVC(C=1.0, kernel='rbf')
    mat, label = await load_img(img_root_path)
    # todo 切分训练数据集和测试数据集 7:3
    # ...
    # 开始训练模型
    rf = clf.fit(mat, label)
    # 存储训练好的模型
    joblib.dump(rf, os.path.join(img_root_path, 'svm.model'))
    img_path = r"D:\pythonproject\rubik_solve\imgs\W"

    # def img2vector(img):
    #     img = cv2.resize(img, (25, 25), interpolation=cv2.INTER_CUBIC)
    #     img_arr = np.array(img)
    #     img_normlization = img_arr / 255
    #     img_arr2 = np.reshape(img_normlization, (1, -1))
    #     return img_arr2
    #
    # for file in os.listdir(img_path):
    #     filepath = os.path.join(img_path, file)
    #     img = cv2.imread(filepath)
    #
    #     img2arr = img2vector(img)
    #     preResult = clf.predict(img2arr)
    #
    #     print(preResult)


if __name__ == '__main__':
    st = time.perf_counter()
    path = r"../imgs"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_svm(path))
    et = time.perf_counter()
    print("Training spent {:.4f}s.".format((et - st)))
