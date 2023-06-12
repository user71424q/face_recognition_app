# -*- coding: utf-8 -*-
import os
import cv2
import face_recognition
import numpy as np


# for box in boxes:
#    for (x, y, w, h) in boxes:
#        cv2.rectangle(img, (h, w), (y, x), (0, 255, 0), 2)
# cv2.imshow("Frame", img)
# cv2.waitKey(0)


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
    check_img_boxes = face_recognition.face_locations(check_img)
    check_img_points = face_recognition.face_encodings(check_img, check_img_boxes)

    result = [(i, '???') for i in check_img_boxes]
    # цикл по папке с фото
    for filename in os.listdir(database_folder_path):
        # пропускаем файлы, не являющиеся изображениями
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue

        # чтение изображения из папки бд в нужный формат и расчет ключевых точек всех лиц
        db_bgr = cv2.imdecode(np.fromfile(os.path.join(database_folder_path, filename), dtype=np.uint8),
                              cv2.IMREAD_UNCHANGED)
        db_img = cv2.cvtColor(db_bgr, cv2.COLOR_BGR2RGB)
        db_img_box = face_recognition.face_locations(db_img)
        db_img_points = face_recognition.face_encodings(db_img, db_img_box)
        if not db_img_points:
            continue
        else:
            db_img_points = db_img_points[0]
        # массив True/False - результаты сравнения лица из БД с лицами на фото для проверки
        compare_res = face_recognition.compare_faces(check_img_points, db_img_points)
        for i in range(len(compare_res)):
            # если изображение из БД совпало с одним из лиц на фото для проверки, обновляем его имя
            if compare_res[i]:
                result[i] = (result[i][0], filename[:filename.rfind('.')])

    return result

def getImage(imgPath, dirPath, show_unknown=False):
    print(imgPath, dirPath, show_unknown, sep='\n')
    res = recognize_faces(imgPath, dirPath)
    img = cv2.imdecode(np.fromfile(imgPath, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for (x, y, w, h), name in res:

        if name == '???' and show_unknown:
            cv2.rectangle(img, (h, w), (y, x), (255, 0, 0), 2)
            cv2.putText(img, name, (h + 2, w + 20), cv2.FONT_HERSHEY_COMPLEX, 0.75, (255, 0, 0), 2)
        elif name != '???':
            cv2.rectangle(img, (h, w), (y, x), (0, 255, 0), 2)
            cv2.putText(img, name, (h + 2, w + 20), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 255, 0), 2)
    return img


