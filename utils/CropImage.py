import cv2
import numpy as np


class Cutter:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        self.mask = np.zeros_like(self.image)

    def ellipse_cutter(self, center, axes, angle):
        """
        创建椭圆裁切掩码
        :param center: 圆形坐标
        :param axes: 长短轴长度
        :param angle: 旋转角度
        :return:
        """
        cv2.ellipse(self.mask, center, axes, angle, 0, 360, (255, 255, 255), thickness=-1)

    def triangle_cutter(self, vertices):
        """
        创建三角形裁切掩码
        :param vertices: 三角形定点坐标
        :return:
        """
        vertices = np.array(vertices, dtype=np.int32)
        cv2.fillPoly(self.mask, [vertices], (255, 255, 255))

    def rhombus_cutter(self, vertices):
        """
        创建菱形裁切掩码
        :param vertices: 菱形定点坐标
        :return:
        """
        vertices = np.array(vertices, dtype=np.int32)
        cv2.fillPoly(self.mask, [vertices], (255, 255, 255))

    def crop_and_save(self, output_path):
        """
        裁切并保存
        :param output_path: 裁切文件输出路径
        :return:
        """
        result = cv2.bitwise_and(self.image, self.mask)
        cv2.imwrite(output_path, result)


if __name__ == "__main__":
    image_path = './img/5.jpg'
    cutter = Cutter(image_path)
    ellipse_center = (300, 200)
    ellipse_axes = (100, 50)
    ellipse_angle = 300
    cutter.ellipse_cutter(ellipse_center, ellipse_axes, ellipse_angle)
    triangle_vertices = [(608, 831), (685, 960), (756, 832)]
    cutter.triangle_cutter(triangle_vertices)
    rhombus_vertices = [(253, 845), (252, 941), (348, 941), (348, 845)]
    cutter.triangle_cutter(rhombus_vertices)
    output_path = 'temp_img/temp.jpg'
    cutter.crop_and_save(output_path)
