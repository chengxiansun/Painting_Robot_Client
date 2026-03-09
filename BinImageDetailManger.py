import cv2
import matplotlib.pyplot as plt
import numpy as np


class BinImageDetailManger:
    """
    二进制图像细节管理类，支持Canny边缘检测、膨胀、腐蚀操作
    处理OpenCV格式的图片，提供get方法获取处理后的图片
    """

    def __init__(self, image):
        """
        初始化函数，读取图片并存储原始图像
        :param image: 图片文件
        """
        # 读取彩色图片
        self.img = image
        if self.img is None:
            raise ValueError(f"图片为空")

        # 存储处理后的图像（初始为None）
        self.processed_img = None
        # 存储灰度图（供后续操作使用）
        self.gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

    def canny_edge_detection(self, low_threshold=50, high_threshold=150, save_result=False):
        """
        使用Canny算法检测彩色图片的边缘，并将结果黑白颜色互换（白底黑边）
        :param low_threshold: Canny低阈值
        :param high_threshold: Canny高阈值
        :param save_result: 是否保存检测结果
        :return: self (支持链式调用)
        """
        # 高斯模糊降噪
        blurred_img = cv2.GaussianBlur(self.gray_img, (5, 5), 0)

        # Canny边缘检测（黑底白边）
        edge_image_original = cv2.Canny(blurred_img, low_threshold, high_threshold)

        # 黑白颜色互换（白底黑边）
        self.processed_img = 255 - edge_image_original

        # 可视化结果
        self._visualize_result("Canny边缘检测结果（白底黑边）", self.processed_img)

        # 保存结果（可选）
        if save_result:
            cv2.imwrite('canny_edge_result_inverted.png', self.processed_img)
            print("颜色互换后的边缘检测结果已保存为 canny_edge_result_inverted.png")

        return self  # 链式调用支持

    def dilate(self, kernel_size=(3, 3), iterations=1, save_result=False):
        """
        膨胀操作（对处理后的图像或灰度图进行膨胀）
        :param kernel_size: 膨胀核大小
        :param iterations: 膨胀迭代次数
        :param save_result: 是否保存结果
        :return: self (支持链式调用)
        """
        # 创建膨胀核
        kernel = np.ones(kernel_size, np.uint8)

        # 如果已有处理后的图像，对其膨胀；否则对灰度图膨胀
        src_img = self.processed_img if self.processed_img is not None else self.gray_img
        self.processed_img = cv2.dilate(src_img, kernel, iterations=iterations)

        # 可视化结果
        self._visualize_result("膨胀处理结果", self.processed_img)

        # 保存结果（可选）
        if save_result:
            cv2.imwrite('dilate_result.png', self.processed_img)
            print("膨胀处理结果已保存为 dilate_result.png")

        return self  # 链式调用支持

    def erode(self, kernel_size=(3, 3), iterations=1, save_result=False):
        """
        腐蚀操作（对处理后的图像或灰度图进行腐蚀）
        :param kernel_size: 腐蚀核大小
        :param iterations: 腐蚀迭代次数
        :param save_result: 是否保存结果
        :return: self (支持链式调用)
        """
        # 创建腐蚀核
        kernel = np.ones(kernel_size, np.uint8)

        # 如果已有处理后的图像，对其腐蚀；否则对灰度图腐蚀
        src_img = self.processed_img if self.processed_img is not None else self.gray_img
        self.processed_img = cv2.erode(src_img, kernel, iterations=iterations)

        # 可视化结果
        self._visualize_result("腐蚀处理结果", self.processed_img)

        # 保存结果（可选）
        if save_result:
            cv2.imwrite('erode_result.png', self.processed_img)
            print("腐蚀处理结果已保存为 erode_result.png")

        return self  # 链式调用支持

    def get_image(self):
        """
        获取处理后的图片
        :return: 处理后的图像数组（numpy.ndarray）
        """
        if self.processed_img is None:
            print("警告：尚未进行任何图像处理，返回原始灰度图")
            return self.gray_img
        return self.processed_img

    def _visualize_result(self, title, processed_img):
        """
        内部可视化函数，对比原图和处理后的图像
        :param title: 处理结果的标题
        :param processed_img: 处理后的图像
        """
        plt.figure(figsize=(12, 6))

        # 显示原图（转换为RGB格式）
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
        plt.title('原始彩色图片')
        plt.axis('off')

        # 显示处理后的结果
        plt.subplot(1, 2, 2)
        plt.imshow(processed_img, cmap='gray')
        plt.title(title)
        plt.axis('off')

        plt.tight_layout()
        plt.show()


# ------------------- 测试代码 -------------------
if __name__ == "__main__":
    # 替换为你的图片路径
    image_path = "camera/test.png"
    img=cv2.imread(image_path, cv2.IMREAD_COLOR)
    try:
        # 1. 创建类实例
        img_manager = BinImageDetailManger(img)

        # 2. 执行Canny边缘检测（支持链式调用）
        img_manager.canny_edge_detection(
            low_threshold=50,
            high_threshold=150,
            save_result=False
        )

        # 3. 对边缘检测结果进行膨胀操作
        img_manager.dilate(kernel_size=(3, 3), iterations=2, save_result=False)

        # 4. 对膨胀后的结果进行腐蚀操作
        img_manager.erode(kernel_size=(3, 3), iterations=1, save_result=False)

        # 5. 获取最终处理后的图片
        final_img = img_manager.get_image()
        print(f"处理后的图片形状：{final_img.shape}")

    except Exception as e:
        print(f"执行出错：{e}")