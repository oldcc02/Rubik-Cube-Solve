# -*- coding: utf-8 -*-
# File: predict_cam.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/10 15:58
import joblib
import numpy as np
import cv2
from webcam_base import CameraThread, thread_lock


class CameraThreadPredict(CameraThread):
    def __init__(self, *args, **kwargs):
        super(CameraThreadPredict, self).__init__(*args, **kwargs)
        self.clf = joblib.load("../imgs/svm.model")

    def pretreatment_frame(self, img):
        contours = self.find_counters(img)
        img = img.copy()
        for cnt in contours:
            try:
                x, y, w, h = cv2.boundingRect(cnt)
                rect_area = w * h
                mid_x = int(x + w / 2)
                mid_y = int(y + h / 2)
                # img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                print(rect_area)
                if 6000 > rect_area > 3000:
                    res = self.predict_color(mid_x, mid_y, img)
                    # 圈出颜色块
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    # 在色块上打上识别结果
                    img = cv2.putText(img, res, (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 5,
                                      cv2.LINE_AA, False)
                else:
                    continue
            except Exception:
                continue
        return img

    def predict_color(self, mid_x, mid_y, img):
        # 基于中点要检测的位置
        check_img = img[mid_y - 12:mid_y + 13, mid_x - 12:mid_x + 13]
        img_normalization = check_img / 255
        img_arr2 = np.reshape(img_normalization, (1, -1))
        res = self.clf.predict(img_arr2)
        print(res)
        return res[0]


def main():
    camera_id = "rtsp://admin:admin@192.168.101.6:8554/live"
    # camera_id = 0

    thread = CameraThreadPredict(camera_id)
    thread.start()

    while True:
        thread_lock.acquire()
        frame = thread.get_frame()
        thread_lock.release()

        frame = thread.pretreatment_frame(frame)
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            thread_lock.acquire()
            thread.set_thread_exit(True)
            thread_lock.release()
            break

    thread.join()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
