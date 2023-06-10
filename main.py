# -*- coding: utf-8 -*-
import os

import cv2
import face_recognition
import numpy as np

img = cv2.imread('2.jpg')
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img2 = cv2.imread('5.png')
rgb2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)


# for box in boxes:
#    for (x, y, w, h) in boxes:
#        cv2.rectangle(img, (h, w), (y, x), (0, 255, 0), 2)
# cv2.imshow("Frame", img)
# cv2.waitKey(0)

def compare_faces(database_img, check_img):
    """
        Сравнивает фотографию из базы данных со всеми лицами на другой фотографии

        :param database_img: Изображение с одним лицом. Массив пикселей, содержимое ячеек - значения каналов R, G, B
        :param check_img: Изображение для проверки. Массив пикселей, содержимое ячеек - значения каналов R, G, B
        :return: Кортеж координат границ совпавшего лица на check_img, либо None, если нет совпадений
    """
    db_img_box = face_recognition.face_locations(database_img)
    db_img_points = face_recognition.face_encodings(database_img, db_img_box)[0]
    check_img_boxes = face_recognition.face_locations(check_img)
    check_img_points = face_recognition.face_encodings(check_img, check_img_boxes)
    compare_res = face_recognition.compare_faces(check_img_points, db_img_points)
    for i in range(len(compare_res)):
        if compare_res[i]:
            return check_img_boxes[i]
    return None


def recognize_faces(check_img_path, database_folder_path):
    """
            Сравнивает фотографию, к которой указан путь, со всеми лицами с фотографий из выбранной папки

            :param check_img_path: путь к изображению для проверки
            :param database_folder_path: путь к папке с изображениями из БД
            :return: Массив пар (box, name)
        """
    img = cv2.imdecode(np.fromfile(check_img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    # конвертация в формат RGB для модели
    check_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result_boxes = []
    for filename in os.listdir(database_folder_path):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue
        db_bgr = cv2.imdecode(np.fromfile(os.path.join(database_folder_path, filename), dtype=np.uint8),
                              cv2.IMREAD_UNCHANGED)
        # конвертация в формат RGB для модели
        db_img = cv2.cvtColor(db_bgr, cv2.COLOR_BGR2RGB)
        box = compare_faces(db_img, check_img)
        if box:
            result_boxes.append((box, filename))
    return result_boxes


def get_res_image(check_img_path, res_boxes):

res = recognize_faces("C:\\Users\\Асмодей\\Desktop\\img_recgn_tests\\check2.jpg",
                      "C:\\Users\\Асмодей\\Desktop\\img_recgn_tests\\db")
img = img = cv2.imdecode(np.fromfile("C:\\Users\\Асмодей\\Desktop\\img_recgn_tests\\check2.jpg", dtype=np.uint8),
                         cv2.IMREAD_UNCHANGED)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
for (x, y, w, h), name in res:
    cv2.rectangle(img, (h, w), (y, x), (0, 255, 0), 2)
    cv2.putText(img, name, (h + 2, w + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
cv2.imshow("Frame", img)
cv2.waitKey(0)
