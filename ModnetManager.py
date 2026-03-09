import os
import sys
import logging
import torch
import torch.nn as nn
from torchvision import transforms
import cv2
import numpy as np
from PIL import Image
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.models.modnet import MODNet

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 控制台输出
    ]
)
logger = logging.getLogger(__name__)


class ModnetManager:
    """MODNet 人像抠图管理类，用于图像的人像分割与抠图处理"""

    def __init__(self, model_path, output_dir='output', device=None):
        """
        初始化 MODNet 抠图器
        Args:
            model_path (str): 预训练模型文件路径
            output_dir (str): 结果输出目录，默认 'output'
            device (str): 运行设备，可选 'cuda'/'cpu'，默认自动检测
        """
        # 路径配置
        self.model_path = model_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # 设备配置
        self.device = self._get_device(device)
        logger.info(f'Running on device: {self.device}')

        # 加载模型
        self.model = self._load_model()

        # 图像预处理管道
        self.transform = self._get_transform()

        # 保存图片
        self.matte_image = None
        self.people_image = None

    def get_matte_image(self):
        return self.matte_image

    def get_people_image(self):
        return self.people_image

    @staticmethod
    def _get_device(device):
        """自动检测/验证运行设备"""
        if device is not None:
            if device == 'cuda' and not torch.cuda.is_available():
                logger.warning("CUDA 不可用，自动切换到 CPU")
                return torch.device('cpu')
            return torch.device(device)
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def _load_model(self):
        """加载 MODNet 模型并初始化权重"""
        logger.info('Loading MODNet model...')
        modnet = MODNet(backbone_pretrained=False)
        modnet = nn.DataParallel(modnet)

        # 加载权重（兼容 CPU/GPU）
        if self.device.type == 'cpu':
            weights = torch.load(self.model_path, map_location=torch.device('cpu'))
        else:
            weights = torch.load(self.model_path)

        modnet.load_state_dict(weights)
        modnet.to(self.device)
        modnet.eval()  # 设置评估模式
        return modnet

    @staticmethod
    def _get_transform():
        """获取图像预处理转换管道"""
        return transforms.Compose([
            transforms.Resize((512, 512), Image.BILINEAR),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

    def process_image(self, image_path, save_matte=True, save_composite=True):
        """
        处理单张图像，生成抠图蒙版和合成图像
        Args:
            image_path (str): 输入图像路径
            save_matte (bool): 是否保存蒙版图像
            save_composite (bool): 是否保存合成图像（最终会删除）
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"输入图像不存在: {image_path}")

        # 1. 读取并预处理图像
        logger.info(f'Processing image: {image_path}')
        image = Image.open(image_path).convert('RGB')
        original_size = image.size
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # 2. 模型推理
        with torch.no_grad():
            _, _, matte = self.model(input_tensor, True)

        # 3. 后处理蒙版
        # 转换为numpy数组并恢复原始尺寸
        matte_np = matte[0].data.cpu().numpy().transpose(1, 2, 0)
        matte_np = cv2.resize(matte_np, original_size, interpolation=cv2.INTER_LINEAR)
        # 归一化到 [0, 1]
        matte_np = (matte_np - matte_np.min()) / (matte_np.max() - matte_np.min())
        # 增加通道维度 (H, W) -> (H, W, 1)
        matte_np = matte_np[..., np.newaxis]

        # 5. 保存蒙版图像（OpenCV格式）
        if save_matte:
            # 转换为OpenCV格式并保存 (uint8 0-255)
            self.matte_image = (matte_np.squeeze() * 255).astype(np.uint8)
            cv2.imwrite(self.output_dir + '/matte.png', self.matte_image)

        # 6. 生成并保存人图像（OpenCV格式）
        if save_composite:
            # 转换原始图像为OpenCV格式 (RGB -> BGR)
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            # 合成前景（白色背景）
            composite_cv = image_cv * matte_np + (1 - matte_np) * 255
            self.people_image = composite_cv.astype(np.uint8)
            cv2.imwrite(self.output_dir + '/composite.png', self.people_image)

    def process_portrait_image(self, image:Image, save_matte=True, save_composite=True):
        """
        处理单张图像，生成抠图蒙版和合成图像
        Args:
            image (Image): 输入图像路径
            save_matte (bool): 是否保存蒙版图像
            save_composite (bool): 是否保存合成图像（最终会删除）
        """

        original_size = image.size
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # 2. 模型推理
        with torch.no_grad():
            _, _, matte = self.model(input_tensor, True)

        # 3. 后处理蒙版
        # 转换为numpy数组并恢复原始尺寸
        matte_np = matte[0].data.cpu().numpy().transpose(1, 2, 0)
        matte_np = cv2.resize(matte_np, original_size, interpolation=cv2.INTER_LINEAR)
        # 归一化到 [0, 1]
        matte_np = (matte_np - matte_np.min()) / (matte_np.max() - matte_np.min())
        # 增加通道维度 (H, W) -> (H, W, 1)
        matte_np = matte_np[..., np.newaxis]

        # 5. 保存蒙版图像（OpenCV格式）
        if save_matte:
            # 转换为OpenCV格式并保存 (uint8 0-255)
            self.matte_image = (matte_np.squeeze() * 255).astype(np.uint8)
            cv2.imwrite(self.output_dir + '/matte.png', self.matte_image)

        # 6. 生成并保存人图像（OpenCV格式）
        if save_composite:
            # 转换原始图像为OpenCV格式 (RGB -> BGR)
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            # 合成前景（白色背景）
            composite_cv = image_cv * matte_np + (1 - matte_np) * 255
            self.people_image = composite_cv.astype(np.uint8)
            cv2.imwrite(self.output_dir + '/composite.png', self.people_image)

    def batch_process(self, image_paths, save_matte=True, save_composite=True):
        """
        批量处理多张图像
        Args:
            image_paths (list): 图像路径列表
            save_matte (bool): 是否保存蒙版
            save_composite (bool): 是否生成（并删除）合成图像
        Returns:
            list: 每张图像的处理结果字典列表
        """
        results = []
        for img_path in image_paths:
            try:
                res = self.process_image(img_path, save_matte, save_composite)
                results.append(res)
            except Exception as e:
                logger.error(f"处理图像失败 {img_path}: {str(e)}")
                results.append({'image_path': img_path, 'error': str(e)})
        return results


# -------------------------- 使用示例 --------------------------
if __name__ == '__main__':
    # 1. 初始化抠图管理器
    modnet_manager = ModnetManager(
        model_path='pretrained/modnet_photographic_portrait_matting.ckpt',
        output_dir='pretrained/output'
    )

    # 2. 处理单张图像
    modnet_manager.process_image(
        image_path='test.jpg',
        save_matte=True,
        save_composite=True
    )

    # 3. 批量处理图像（示例）
    # batch_results = modnet_manager.batch_process(
    #     image_paths=['pretrained/test1.jpg', 'pretrained/test2.jpg'],
    #     save_matte=True,
    #     save_composite=True
    # )

    logger.info('MODNet processing complete!')
