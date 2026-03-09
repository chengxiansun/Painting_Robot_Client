import math
import os
import logging
from logging.handlers import RotatingFileHandler

import cv2 as cv
import numpy as np


# -------------------------- 日志配置 --------------------------
def setup_logger(name='ImageMatting', log_file='image_matting.log', level=logging.INFO):
    """
    配置日志器：同时输出到控制台和文件，支持日志轮转
    :param name: 日志器名称
    :param log_file: 日志文件路径
    :param level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
    :return: 配置好的logger对象
    """
    # 定义日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # 避免重复输出

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # 文件处理器（轮转日志，避免文件过大）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 单个日志文件最大10MB
        backupCount=5,  # 最多保留5个备份
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # 添加处理器
    if not logger.handlers:  # 避免重复添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# 初始化全局日志器
logger = setup_logger()


class MatteBasedCompositor:
    """
    基于外部matte的图像合成类
    功能：读取前景图、matte蒙版 → 将前景合成到新背景
    """

    def __init__(self):
        """初始化类"""
        self.logger = logger  # 绑定日志器

    @staticmethod
    def ensure_folder(folder):
        """
        静态方法：确保文件夹存在，不存在则创建
        :param folder: 文件夹路径
        """
        if not os.path.exists(folder):
            os.makedirs(folder)
            logger.info(f"创建文件夹：{folder}")

    @staticmethod
    def resize_bg_to_fit_fg(bg, fg_h, fg_w):
        """
        静态方法：调整背景尺寸以适配前景
        :param bg: 背景图（np.array）
        :param fg_h: 前景高度
        :param fg_w: 前景宽度
        :return: 调整后的背景图
        """
        bg_h, bg_w = bg.shape[:2]
        wratio = fg_w / bg_w
        hratio = fg_h / bg_h
        ratio = max(wratio, hratio)
        if ratio > 1:
            new_bg_w = math.ceil(bg_w * ratio)
            new_bg_h = math.ceil(bg_h * ratio)
            bg = cv.resize(bg, (new_bg_w, new_bg_h), interpolation=cv.INTER_CUBIC)
            logger.info(f"背景图放大至：{new_bg_w}x{new_bg_h}（缩放比例：{ratio:.2f}）")
        return bg

    def load_matte(self, matte_path, fg_h, fg_w):
        """
        读取并预处理外部matte文件
        :param matte_path: matte蒙版文件路径（png/jpg等）
        :param fg_h: 前景图高度
        :param fg_w: 前景图宽度
        :return: 归一化后的alpha蒙版（0-1，np.array，shape=(h,w)）
        """
        # 读取matte（支持灰度/彩色图）
        matte = cv.imread(matte_path, cv.IMREAD_UNCHANGED)
        if matte is None:
            raise FileNotFoundError(f"无法读取matte文件：{matte_path}")

        # 转换为灰度图（如果是彩色/4通道图）
        if len(matte.shape) == 3:
            if matte.shape[2] == 4:  # RGBA图取Alpha通道
                matte = matte[:, :, 3]
            else:  # 彩色图转灰度
                matte = cv.cvtColor(matte, cv.COLOR_BGR2GRAY)

        # 调整matte尺寸与前景图一致
        if matte.shape[0] != fg_h or matte.shape[1] != fg_w:
            matte = cv.resize(matte, (fg_w, fg_h), interpolation=cv.INTER_LINEAR)
            self.logger.info(f"Matte尺寸调整为与前景一致：{fg_w}x{fg_h}")

        # 归一化到0-1范围
        alpha = matte.astype(np.float32) / 255.0
        # 确保alpha值在0-1之间（防止异常值）
        alpha = np.clip(alpha, 0.0, 1.0)

        self.logger.info("✅ Matte蒙版加载并预处理成功")
        return alpha

    def composite(self, fg_path, matte_path, bg_path, output_dir='output'):
        """
        核心方法：完成抠图+背景合成的完整流程
        :param fg_path: 前景图路径（含人物）
        :param matte_path: 外部matte蒙版文件路径
        :param bg_path: 新背景图路径
        :param output_dir: 结果保存目录
        :return: 合成后的图像（np.array）
        """
        self.logger.info(f"开始处理：前景={fg_path}，Matte={matte_path}，背景={bg_path}")

        # 1. 读取图片
        # 读取前景图
        fg = cv.imread(fg_path)
        if fg is None:
            self.logger.error(f"无法读取前景图：{fg_path}")
            raise FileNotFoundError(f"无法读取前景图：{fg_path}")
        fg_h, fg_w = fg.shape[:2]
        self.logger.info(f"前景图尺寸：{fg_w}x{fg_h}")

        # 读取背景图
        bg = cv.imread(bg_path)
        if bg is None:
            self.logger.error(f"无法读取背景图：{bg_path}")
            raise FileNotFoundError(f"无法读取背景图：{bg_path}")
        self.logger.info(f"背景图原始尺寸：{bg.shape[1]}x{bg.shape[0]}")

        # 2. 加载并预处理matte
        alpha = self.load_matte(matte_path, fg_h, fg_w)

        # 3. 合成前景到新背景
        # 调整背景尺寸适配前景
        bg_resized = self.resize_bg_to_fit_fg(bg, fg_h, fg_w)
        bg_h, bg_w = bg_resized.shape[:2]

        # 前景居中放置
        x = max(0, int((bg_w - fg_w) / 2))
        y = max(0, int((bg_h - fg_h) / 2))
        bg_crop = bg_resized[y:y + fg_h, x:x + fg_w].astype(np.float32)

        # 扩展alpha维度（从h,w → h,w,1），方便广播运算
        alpha_expanded = np.expand_dims(alpha, axis=-1)

        # 核心合成公式：合成图 = alpha*前景 + (1-alpha)*背景
        fg_float = fg.astype(np.float32)
        composite_crop = alpha_expanded * fg_float + (1 - alpha_expanded) * bg_crop

        # 将合成后的前景放回背景图
        composite = bg_resized.copy()
        composite[y:y + fg_h, x:x + fg_w] = composite_crop.astype(np.uint8)
        self.logger.info("✅ 图像合成成功")

        # 4. 保存结果
        self.ensure_folder(output_dir)
        composite_path = os.path.join(output_dir, 'compose.png')
        alpha_path = os.path.join(output_dir, 'alpha_matte.png')

        cv.imwrite(composite_path, composite)
        cv.imwrite(alpha_path, (alpha * 255).astype(np.uint8))

        self.logger.info(f"🎉 结果已保存到 {output_dir} 文件夹：")
        self.logger.info(f"- 最终合成图：{composite_path}")
        self.logger.info(f"- 输入的Matte蒙版（归一化后）：{alpha_path}")

        return composite


# -------------------------- 调用示例 --------------------------
if __name__ == '__main__':
    try:
        # 1. 初始化合成器
        compositor = MatteBasedCompositor()

        # 2. 执行合成（指定前景、matte、背景路径）
        composite_image = compositor.composite(
            fg_path='input/foreground.jpg',  # 你的前景图路径
            matte_path='input/foreground_matte.png',  # 你的matte蒙版路径
            bg_path='input/background.jpg',  # 你的新背景图路径
            output_dir='output'  # 结果保存目录
        )

        # 可选：展示合成结果
        cv.imshow('Composite Result', composite_image)
        cv.waitKey(0)
        cv.destroyAllWindows()

    except Exception as e:
        logger.critical(f"❌ 合成流程执行失败：{e}", exc_info=True)