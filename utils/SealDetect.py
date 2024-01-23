"""
此脚本用于对图像文件进行印章检测 裁剪
SealDetector：主要检测的印章包括，圆形印章、椭圆形印章、三角形印章、菱形印章、正方形印章
"""
import os
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR, VisRes


class SealDetector:
    def __init__(self, img):
        self.img = img

    def detection(self):
        img_contour = self.img.copy()

        img_gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)  # 转灰度图
        img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)  # 高斯模糊
        img_vanny = cv2.Canny(img_blur, 60, 60)  # Canny算子边缘检测

        contours, hierarchy = cv2.findContours(img_vanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 寻找轮廓点
        # 设置面积阈值（可以根据需要调整）
        min_contour_area = 3000
        max_contour_area = 30000
        # 筛选出符合面积阈值的轮廓
        filtered_contours = [cnt for cnt in contours if max_contour_area > cv2.contourArea(cnt) > min_contour_area]
        self.boxes_list = []
        for obj in filtered_contours:
            area = cv2.contourArea(obj)
            cv2.drawContours(img_contour, obj, -1, (255, 0, 0), 4)  # 绘制轮廓线
            perimeter = cv2.arcLength(obj, True)  # 计算轮廓周长
            approx = cv2.approxPolyDP(obj, 0.1 * perimeter, True)  # 获取轮廓角点坐标,根据实际情况调整系数
            corner_num = len(approx)  # 轮廓角点的数量
            x, y, w, h = cv2.boundingRect(approx)  # 获取坐标值和宽度、高度

            # 轮廓对象分类
            if corner_num == 3:
                obj_type = "三角形"
            elif corner_num == 4:
                obj_type = "菱形"
            elif corner_num > 4:
                obj_type = "圆形"
            else:
                obj_type = "None"

            # 保存检测结果 obj_type, perimeter, area, x, y, w, h
            self.boxes_list.append([obj_type, int(perimeter), int(area), x, y, w, h])  # 保存检测结果

            # # 裁切可视化
            # crop_img = img_contour[y:y + h, x:x + w]
            # cv2.imshow("cropped", crop_img)
            # cv2.waitKey(0)
            # # 原图检测可视化
            # cv2.rectangle(img_contour, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 绘制边界框
            # cv2.putText(img_contour, obj_type, (x + (w // 2), y + (h // 2)), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)  # 绘制文字
            # cv2.imshow("Original img", self.img)
            # cv2.imshow("imgGray", img_gray)
            # cv2.imshow("imgBlur", img_blur)
            # cv2.imshow("imgCanny", img_vanny)
            # cv2.imshow("shape Detection", img_contour)
            # cv2.waitKey(0)
        return self.boxes_list

    def crop_img(self):
        self.detection()
        img_list = []
        if len(self.boxes_list) == 0:
            return img_list
        for obj_type, perimeter, area, x, y, w, h in self.boxes_list:
            crop_img = self.img[y:y + h, x:x + w]
            # 检测出来的印章为扁的或者面积小于指定像素时，跳过
            if crop_img.shape[0] < crop_img.shape[1] / 20 or crop_img.shape[0] * crop_img.shape[1] < 100:
                continue
            # 检测出来的印章为圆形时，进行缩放，并将曲线部分的文字拉平后进行检测
            if obj_type == "圆形":
                resize_img = cv2.resize(crop_img, (640, 640))
                crop_flat_img = self.flat_seal(resize_img)
                img_list.append([crop_flat_img, obj_type, perimeter, area])
            img_list.append([crop_img, obj_type, perimeter, area])
        return img_list

    @staticmethod
    def clean_seal(circle_seal_img):
        """
        清除印章下面的干扰文字（黑色字体）
        :param circle_seal_img: 圆形印章图片
        :return:
        """
        # cleaned_circle_seal_img_list = []
        if circle_seal_img is not None:
            img_png = cv2.cvtColor(circle_seal_img.copy(), cv2.COLOR_RGB2RGBA)
            hue_image = cv2.cvtColor(circle_seal_img, cv2.COLOR_BGR2HSV)
            # 红色像素点区域
            # low_range = np.array([156, 43, 46])
            low_range = np.array([100, 5, 5])
            high_range = np.array([180, 255, 255])
            th = cv2.inRange(hue_image, low_range, high_range)
            element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            th = cv2.dilate(th, element)
            index1 = th == 255
            img1 = np.zeros(img_png.shape, np.uint8)
            img1[:, :, :] = (255, 255, 255, 0)
            img1[index1] = img_png[index1]  # (0,0,255)

            low_range = np.array([0, 5, 5])
            high_range = np.array([9, 255, 255])
            th = cv2.inRange(hue_image, low_range, high_range)
            element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            th = cv2.dilate(th, element)
            index1 = th == 255
            img2 = np.zeros(img_png.shape, np.uint8)
            img2[:, :, :] = (255, 255, 255, 0)
            img2[index1] = img_png[index1]

            img_real = cv2.add(img2, img1)

            white_px = np.asarray([255, 255, 255, 255])

            (row, col, _) = img_real.shape
            for r in range(row):
                for c in range(col):
                    px = img_real[r][c]
                    if all(px == white_px):
                        img_real[r][c] = img_png[r][c]

            # directory_path = os.path.join("visualized_result", file_hash.split("_")[0])
            # CommonUtil.prepare_directory(directory_path)
            # cv2.imwrite("visualized_result/{}/cleaned_seal.png".format(file_hash), img_real)

            # cleaned_circle_seal_img_list.append(img_real)
            # cv2.imshow("clean_seal", img_real)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            bgr_img = cv2.cvtColor(img_real, cv2.COLOR_BGRA2BGR)
            return bgr_img
        return None

    @staticmethod
    def flat_seal(seal_img, file_hash="test"):
        """
        圆形印章拉直
        :param seal_img: 预处理后的圆形印章图片
        :param file_hash: 文件hash
        :return:
        """
        # flatted_seal_list = []
        if seal_img is not None:
            # cv2.imshow("clean_seal", img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            gray = cv2.cvtColor(seal_img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            gray = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
            gray = cv2.warpPolar(gray, (-1, -1), (h // 2, h // 2), h // 2,
                                 cv2.INTER_CUBIC + cv2.WARP_POLAR_LINEAR)
            gray = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
            directory_path = os.path.join("visualized_result", file_hash.split("_")[0])
            file_path = os.path.join(directory_path, "flatted_seal_{}.png".format(file_hash))
            cv2.imwrite(file_path, gray)
            # flatted_seal_list.append(gray)
            bgr_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            return bgr_img
        return None


class FunctionalTesting:
    """
    功能测试 对裁剪函数 印章检测进行功能测试
    """

    def __init__(self):
        self.ocr = RapidOCR()
        self.vis = VisRes()
        self.font_path = "./assets/FZYTK.TTF"

    def testSealDetectorImage(self, image_path):
        img_list = SealDetector(cv2.imread(image_path)).crop_img()
        for img_array, obj_type, perimeter, area in img_list:
            img_array = SealDetector.clean_seal(img_array)
            result, elapse_list = self.ocr(img_array)
            print(result)
            if result is None:
                continue
            boxes, txts, scores = list(zip(*result))
            res = self.vis(img_array, boxes, txts, scores, font_path=self.font_path)
            cv2.imshow("img", res)
            cv2.waitKey(0)

    def testSealDetectorDir(self, image_dir='img'):
        """遍历 img 目录并检测目录下所有图片"""
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                print(os.path.join(root, file))
                img_list = SealDetector(cv2.imread(os.path.join(root, file))).crop_img()
                for img_array, obj_type, perimeter, area in img_list:
                    img_array = SealDetector.clean_seal(img_array)
                    result, elapse_list = self.ocr(img_array)
                    if result is None:
                        continue
                    boxes, txts, scores = list(zip(*result))
                    res = self.vis(img_array, boxes, txts, scores, font_path=self.font_path)
                    cv2.imshow("img", res)
                    cv2.waitKey(0)


if __name__ == '__main__':
    funtest = FunctionalTesting()
    # image_path = './assets/1.png'
    # funtest.testSealDetectorImage(image_path)
    # funtest.testSealDetectorDir('./utils/generate/generateData')
