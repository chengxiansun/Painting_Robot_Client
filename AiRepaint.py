import os
import requests
import time
import base64
import mimetypes
import tempfile
import logging
from PIL import Image
from http import HTTPStatus
from typing import List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Image_repainter.log', encoding='utf-8'),  # 日志文件
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger('AliyunImageRepainter')


class ImageRepainter:
    """阿里云万相风格重绘工具类"""

    def __init__(self, api_key: Optional[str] = None):
        # 初始化API Key
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请设置环境变量 DASHSCOPE_API_KEY 或直接传入api_key参数")

        # 类变量：存储下载的图片临时文件路径
        self.generated_image_paths: List[str] = []
        # 任务ID
        self.task_id: Optional[str] = None
        self.ai_repaint_image = None

    def __del__(self):
        self.cleanup_images()

    def get_ai_repaint_image(self):
        return self.ai_repaint_image

    @staticmethod
    def _encode_file(file_path: str) -> str:
        """私有方法：将图片文件编码为base64格式（带MIME头）"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError("不支持或无法识别的图像格式")

        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        return f"data:{mime_type};base64,{encoded_string}"

    @staticmethod
    def _download_image(image_url: str) -> str:
        """私有方法：下载图片到临时文件并返回文件路径"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # 创建临时文件保存图片
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(response.content)
            temp_file.close()

            return temp_file.name
        except Exception as e:
            logger.error(f"下载图片失败: {str(e)}")
            raise RuntimeError(f"下载图片失败: {str(e)}")

    def submit_task(self, image_path: str, style_index: int = 0) -> bool:
        """
        提交风格重绘任务
        :param image_path: 原始图片路径
        :param style_index: 风格索引（0=复古漫画, 1=3D童话, 2=二次元, 3=小清新, 4=未来科技...）
        :return: 任务提交是否成功
        """
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

        body = {
            "model": "wanx-style-repaint-v1",
            "input": {
                "image_url": self._encode_file(image_path),
                "style_index": style_index
            }
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            if response.status_code == HTTPStatus.OK:
                self.task_id = response.json().get('output', {}).get('task_id')
                logger.info(f"任务提交成功，任务ID为: {self.task_id}")
                return True
            else:
                logger.error(f"任务提交失败，状态码: {response.status_code}, 响应: {response.text}")
                return False
        except Exception as e:
            logger.error(f"提交任务时发生异常: {str(e)}")
            return False

    def query_task_result(self, show_images: bool = True) -> bool:
        """
        轮询查询任务结果并下载图片
        :param show_images: 是否展示生成的图片（默认展示）
        :return: 任务是否执行成功
        """
        if not self.task_id:
            logger.warning("未提交任务，无法查询结果")
            return False

        url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{self.task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        logger.info("开始查询任务状态...")
        try:
            while True:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code != HTTPStatus.OK:
                    logger.error(f"查询失败，状态码: {response.status_code}, 响应: {response.text}")
                    return False

                response_data = response.json()
                task_status = response_data.get('output', {}).get('task_status')

                if task_status == 'SUCCEEDED':
                    logger.info("任务成功完成！")
                    # 下载所有生成的图片
                    results = response_data.get('output', {}).get('results', [])
                    for i, result in enumerate(results):
                        image_url = result.get('url')
                        if image_url:
                            ai_repaint_path = self._download_image(image_url)
                            self.generated_image_paths.append(ai_repaint_path)
                            logger.info(f"生成图片_{i + 1}已下载至: {ai_repaint_path}")

                            self.ai_repaint_image = Image.open(ai_repaint_path)
                    break
                elif task_status == 'FAILED':
                    logger.error(f"任务失败。错误信息: {response_data}")
                    return False
                else:
                    logger.info(f"任务正在处理中，当前状态: {task_status}...")
                    time.sleep(5)
            return True
        except Exception as e:
            logger.error(f"查询任务结果时发生异常: {str(e)}")
            return False

    def cleanup_images(self):
        """清理下载的图片文件"""
        if self.generated_image_paths:
            logger.info("开始清理临时图片文件...")
            for file_path in self.generated_image_paths:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"已删除文件: {file_path}")
                except Exception as e:
                    logger.error(f"删除文件 {file_path} 失败: {str(e)}")
            # 清空列表
            self.generated_image_paths.clear()


# 使用示例
if __name__ == '__main__':
    # 初始化重绘工具
    repainter = ImageRepainter()

    # 提交任务（指定原始图片路径和风格索引）
    if repainter.submit_task(image_path="camera/test.png", style_index=0):
        # 查询结果并下载图片（默认展示图片）
        # 如果不想展示图片，可传入 show_images=False
        # repainter.query_task_result(show_images=False)
        repainter.query_task_result()

        # 手动清理图片（也可以等待析构函数自动清理）
        repainter.cleanup_images()
