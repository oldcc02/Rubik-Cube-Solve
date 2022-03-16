# -*- coding: utf-8 -*-
# File: collection_cam.py
# @Author: 陈志洋
# @Email:  1209685646@qq.com
# @Time: 2021/12/10 15:58
import os
import cv2

from datetime import datetime

from webcam_base import CameraThread, thread_lock


class CameraThreadCollection(CameraThread):
    """
    颜色数据采集类，继承于CameraThread父类
    """

    def __init__(self, color='', file_root_path="../imgs/", img_save_type="png", *args, **kwargs):
        """
        :param color:正在提取的颜色
        :param file_root_path:数据存储的根目录
        :param img_save_type:图片存储的格式
        """
        super(CameraThreadCollection, self).__init__(*args, **kwargs)
        self.color = color
        self.color_dir_path = os.path.join(file_root_path, color)
        self.img_save_type = img_save_type

    def collection_frame(self, img):
        """
        :param img:视频帧
        :return 处理后的视频帧
        """
        contours = self.find_counters(img)
        img = img.copy()
        for cnt in contours:
            try:
                l_corner, r_corner, mid, rect_area = self._find_img_mid_point(cnt)
                img = cv2.rectangle(img, l_corner, r_corner, (0, 255, 0), 2)
                if 6000 > rect_area > 3000:
                    # 提取颜色块
                    solve_img = img[mid['y'] - 12:mid['y'] + 13, mid['x'] - 12:mid['x'] + 13]
                    save_path = self._img_save_path_setting()
                    cv2.imwrite(save_path, solve_img)
                else:
                    continue
            except Exception as e:
                print(e)
                continue
        return img

    def _img_save_path_setting(self):
        """
        图片保存路径设置
        :return 图片保存路径
        """
        file_num = len(os.listdir(self.color_dir_path))
        img_name = "{}_{}.{}".format(self.color, file_num, self.img_save_type)
        return os.path.join(self.color_dir_path, img_name)


def main():
    camera_id = "rtsp://admin:admin@192.168.101.6:8554/live"

    thread = CameraThreadCollection(camera_id)
    thread.start()
    st = datetime.now()
    while True:
        thread_lock.acquire()
        frame = thread.get_frame()
        thread_lock.release()
        et = datetime.now()
        dur = (et - st).seconds
        if dur == 10:
            print(f'开始第收集')
            st = et
            frame = thread.collection_frame(frame)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            thread_lock.acquire()
            thread.set_thread_exit(True)
            thread_lock.release()
            break

    thread.join()


if __name__ == "__main__":
    main()
