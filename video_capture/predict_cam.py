# -*- coding: utf-8 -*-
# File: predict_cam.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/10 15:58
import joblib
import numpy as np
import cv2
from numpy import ndarray

from webcam_base import CameraThread, thread_lock


class CameraThreadPredict(CameraThread):
    """
    实时颜色识别类，继承CameraThread父类
    """

    def __init__(self, *args, **kwargs):
        super(CameraThreadPredict, self).__init__(*args, **kwargs)
        # 预加载模型
        self.clf = joblib.load("../imgs/svm.model")

    def pretreatment_frame(self, img: ndarray) -> ndarray:
        """
        对视频帧预处理
        :param img:视频帧
        :return 绘制完轮廓矩形框后的视频帧
        """
        contours = self.find_counters(img)
        img = img.copy()
        for cnt in contours:
            try:
                l_corner, r_corner, mid, rect_area = self._find_img_mid_point(cnt)
                # img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                print(rect_area)
                if 6000 > rect_area > 3000:
                    res = self.predict_color(mid['x'], mid['y'], img)
                    # 圈出颜色块
                    img = cv2.rectangle(img, l_corner, r_corner, (0, 255, 0), 2)
                    # 在色块上打上识别结果
                    img = cv2.putText(img, res, (mid['x'], mid['y']), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 5,
                                      cv2.LINE_AA, False)
                else:
                    continue
            except Exception as e:
                print(e)
                continue
        return img

    def predict_color(self, mid_x: int, mid_y: int, img: ndarray) -> str:
        """
        截取基于中点的 25*25*3的截图与模型匹配获取识别结果并在原图绘制轮廓矩形框以及识别结果
        :param mid_x:轮廓中点x轴坐标
        :param mid_y:轮廓中点y轴坐标
        :param img:视频帧
        :return 识别结果
        """
        # 基于中点要检测的位置
        check_img = img[mid_y - 12:mid_y + 13, mid_x - 12:mid_x + 13]
        # 图片归一化处理
        img_normalization = (check_img - np.min(check_img)) / (np.max(check_img) - np.min(check_img))
        # 二维向量转为一维向量
        one_vector = np.reshape(img_normalization, (1, -1))
        # 模型匹配结果
        res = self.clf.predict(one_vector)
        print(res)
        return res[0]


def main():
    camera_id = "rtsp://admin:admin@192.168.101.6:8554/live"

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
