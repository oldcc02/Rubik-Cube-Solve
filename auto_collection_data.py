import time
from datetime import datetime

import cv2

from serial_core.serial_arduino import SerialArduino
from video_capture.collection_cam import CameraThreadCollection
from video_capture.webcam_base import thread_lock

cube_map = {
    "l": "G",  # 左 绿
    "r": "B",  # 右 蓝

    "f": "R",  # 正 红
    "b": "O",  # 背 橙

    "u": "W",  # 顶 白
    "d": "Y",  # 底 黄
}

pre_faces = ["l"]


def get_face_color():
    global pre_faces
    for face in cube_map:
        if "d" in pre_faces:
            pre_faces = ["l"]
            return "l", cube_map["l"]
        if face in pre_faces:
            continue
        pre_faces.append(face)
        return face, cube_map[face]


# if __name__ == '__main__':
#     while True:
#         face, color = get_face_color()
#         print(face, color)
#         time.sleep(1)
if __name__ == '__main__':

    face = "l"
    color = "G"

    serial_arduino = SerialArduino("COM4")
    serial_arduino.send_msg("0")
    serial_arduino.send_msg(face)

    camera_id = "rtsp://admin:admin@192.168.101.6:8554/live"

    thread = CameraThreadCollection(camera_id=camera_id, color=color, file_root_path="imgs/")
    thread.start()
    st = datetime.now()
    time = 1

    while True:
        thread_lock.acquire()
        frame = thread.get_frame()
        thread_lock.release()
        et = datetime.now()
        dur = (et - st).seconds
        if dur == 10:

            print(f'正在收集第{time}次 --> 面:{face} 颜色{color} ')
            st = et
            frame = thread.collection_frame(frame)

            time += 1
            if time % 6 == 0:
                serial_arduino.shake_hand()
                face, color = get_face_color()

                serial_arduino.send_msg(face)

                thread_lock.acquire()
                thread.set_color(color)
                thread_lock.release()

        cv2.imshow('data_collection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            thread_lock.acquire()
            thread.set_thread_exit(True)
            thread_lock.release()
            break

    thread.join()
