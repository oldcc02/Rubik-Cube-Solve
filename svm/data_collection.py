# # -*- coding: utf-8 -*-
# # File: data_collection.py
# # @Author: 陈志洋
# # @Email:  chenzhiyang@sinontt.com
# # @Time: 2021/12/10 16:34
# import cv2
# import joblib
# import numpy as np
#
# img_path = "../imgs/green.jpg"
#
#
# def cv_show(img, name):
#     cv2.imshow(name, img)
#     cv2.waitKey()
#     cv2.destroyAllWindows()
#
#
# # 加载模型
# clf = joblib.load("../imgs/svm.model")
# # 读取
# img = cv2.imread(img_path)
# # 灰度
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# # 高斯模糊
# gs_img = cv2.GaussianBlur(gray, (5, 5), 0)
# # 二值操作，设置50位临界，高于为白色（255），低于为黑色
# _, thresh = cv2.threshold(gs_img, 40, 255, cv2.THRESH_BINARY)
# contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
#
# img = img.copy()
# for cnt in contours:
#     x, y, w, h = cv2.boundingRect(cnt)
#     rect_area = w * h
#     # print(rect_area)
#     if 30000 > rect_area > 3600:
#         mid_x = int(x + w / 2)
#         mid_y = int(y + h / 2)
#
#         img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         # img = cv2.rectangle(img, (mid_x - , mid_y - 5), (mid_x + 5, mid_y + 5), (0, 255, 0), 2)
#         # 基于中点要检测的位置
#         check_img = img[mid_y - 12:mid_y + 13, mid_x - 12:mid_x + 13]
#         check_img = np.array(check_img)
#         img_normlization = check_img / 255
#         img_arr2 = np.reshape(img_normlization, (1, -1))
#         res = clf.predict(img_arr2)
#         print(res)
#     else:
#         continue
#     # img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#
# cv_show(img, 'img')
#
#
# # draw_img = img.copy()
# # res = cv2.drawContours(draw_img, contours, -1, (0, 0, 255), 2)
# # cv_show(res, 'res')
#
#
