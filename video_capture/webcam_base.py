# -*- coding: utf-8 -*-
# File: webcam_base.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2021/12/10 15:58


import cv2
import threading
import numpy as np

from copy import deepcopy

from numpy import ndarray

thread_lock = threading.Lock()


class CameraThread(threading.Thread):
    """
    视频线程的基类，包含视频帧拷贝，线程状态设置等函数，开箱即用
    在使用其内置方法 get_frame() set_thread_exit()需要对线程加锁，并在使用结束后释放锁
    """

    def __init__(self, camera_id, img_height=480, img_width=640):
        super(CameraThread, self).__init__()
        # 摄像头id
        self.camera_id = camera_id
        # 窗口高度
        self.img_height = img_height
        # 窗口宽度
        self.img_width = img_width

        # 视频帧
        self.frame = np.zeros((img_height, img_width, 3), dtype=np.uint8)
        # 线程退出标识符
        self.thread_exit = False

    def get_frame(self):
        """
        深拷贝视频帧
        """
        return deepcopy(self.frame)

    def set_thread_exit(self, flag: bool):
        """
        设置线程的退出状态
        """
        self.thread_exit = flag

    @staticmethod
    def _find_img_mid_point(cnt: ndarray) -> tuple:
        """
        获取轮廓左上角坐标,右下角坐标，中点坐标，以及轮廓面积
        :param cnt: 轮廓
        :return (x, y), (x + w, y + h), {x: mid_x, y: mid_y}, rect_area
        """
        x, y, w, h = cv2.boundingRect(cnt)
        rect_area = w * h
        mid_x = int(x + w / 2)
        mid_y = int(y + h / 2)
        return (x, y), (x + w, y + h), {'x': mid_x, 'y': mid_y}, rect_area

    @staticmethod
    def find_counters(img: ndarray) -> list:
        """
        查找视频帧的所有轮廓信息，并返回
        :param img:视频帧
        :return 包含所有轮廓的列表
        """
        # 获取灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 高斯模糊
        gs_img = cv2.GaussianBlur(gray, (5, 5), 0)
        # 二值操作，设置40位临界，高于为白色（255），低于为黑色
        _, thresh = cv2.threshold(gs_img, 40, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours

    def run(self):
        """
        重写Thread类run方法，调用摄像头循环获取视频帧
        """
        # 获取摄像头对象
        cap = cv2.VideoCapture(self.camera_id)
        while not self.thread_exit and cap.isOpened():
            # cap.read获取一个视频帧
            ret, frame = cap.read()
            if ret:
                # 翻转帧
                frame = cv2.flip(frame, -1)
                frame = cv2.resize(frame, (self.img_width, self.img_height))
                thread_lock.acquire()
                self.frame = frame
                thread_lock.release()
            else:
                self.thread_exit = True
        # 释放摄像头占用资源
        cap.release()

    def __del__(self):
        """
        在类被回收时前，关闭所有cv2产生的窗口
        """
        cv2.destroyAllWindows()


if __name__ == '__main__':
    web_thread = CameraThread(camera_id=1)
