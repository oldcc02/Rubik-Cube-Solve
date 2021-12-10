# -*- coding: utf-8 -*-
# File: collection_cam.py
# @Author: 陈志洋
# @Email:  chenzhiyang@sinontt.com
# @Time: 2021/12/10 15:58
import os
import cv2

from datetime import datetime

from webcam_base import CameraThread, thread_lock


class CameraThreadCollection(CameraThread):
    def __init__(self, *args, **kwargs):
        super(CameraThreadCollection, self).__init__(*args, **kwargs)

    def collection_frame(self, img):
        contours = self.find_counters(img)
        img = img.copy()
        for cnt in contours:
            try:
                x, y, w, h = cv2.boundingRect(cnt)
                rect_area = w * h
                mid_x = int(x + w / 2)
                mid_y = int(y + h / 2)
                if 6000 > rect_area > 3000:
                    # 圈出颜色块
                    solve_img = img[mid_y - 12:mid_y + 13, mid_x - 12:mid_x + 13]
                    cv2.imwrite(f"../imgs/Y/Y_{len(os.listdir('../imgs/Y'))}.png", solve_img)
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    continue
            except Exception as e:
                print(e)
                continue
        return img


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
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
