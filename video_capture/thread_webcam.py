# -*- coding: utf-8 -*-
# File: thread_webcam.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/10 15:58
import numpy as np
import cv2
import threading
from copy import deepcopy

thread_lock = threading.Lock()
thread_exit = False


class CameraThread(threading.Thread):
    def __init__(self, camera_id, img_height, img_width):
        super(CameraThread, self).__init__()
        self.camera_id = camera_id
        self.img_height = img_height
        self.img_width = img_width
        self.frame = np.zeros((img_height, img_width, 3), dtype=np.uint8)
        # self.frame = None

    def get_frame(self):
        return deepcopy(self.frame)

    def run(self):
        global thread_exit
        cap = cv2.VideoCapture(self.camera_id)
        while not thread_exit:
            ret, frame = cap.read()
            if ret:
                # 分辨率已经设置为680*640
                # frame = cv2.resize(frame, (self.img_width, self.img_height))
                thread_lock.acquire()
                self.frame = frame
                thread_lock.release()
            else:
                thread_exit = True
        cap.release()


def main():
    global thread_exit
    # camera_id = "rtsp://admin:admin@192.168.101.4:8554/live"
    camera_id = 0
    img_height = 480
    img_width = 640
    thread = CameraThread(camera_id, img_height, img_width)
    thread.start()

    while not thread_exit:
        thread_lock.acquire()

        frame = thread.get_frame()

        thread_lock.release()

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            thread_exit = True

    thread.join()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
