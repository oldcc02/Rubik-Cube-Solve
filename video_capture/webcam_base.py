# -*- coding: utf-8 -*-
# File: webcam_base.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/10 15:58


import cv2
import threading
import numpy as np

from copy import deepcopy

thread_lock = threading.Lock()


class CameraThread(threading.Thread):
    def __init__(self, camera_id, img_height=480, img_width=640):
        super(CameraThread, self).__init__()
        self.camera_id = camera_id
        self.img_height = img_height
        self.img_width = img_width
        self.frame = np.zeros((img_height, img_width, 3), dtype=np.uint8)
        self.thread_exit = False

    def get_frame(self):
        return deepcopy(self.frame)

    def get_thread_exit(self):
        return self.thread_exit

    def set_thread_exit(self, flag):
        self.thread_exit = flag

    @staticmethod
    def find_counters(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 高斯模糊
        gs_img = cv2.GaussianBlur(gray, (5, 5), 0)
        # 二值操作，设置40位临界，高于为白色（255），低于为黑色
        _, thresh = cv2.threshold(gs_img, 40, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        while not self.thread_exit and cap.isOpened():
            ret, frame = cap.read()
            frame = cv2.flip(frame, -1)
            if ret:
                frame = cv2.resize(frame, (self.img_width, self.img_height))
                thread_lock.acquire()
                self.frame = frame
                thread_lock.release()
            else:
                self.thread_exit = True
        cap.release()
