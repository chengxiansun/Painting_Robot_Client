import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps
import DialogFactory
import modnet.ModnetManager as ModnetManager
import ImageBrowserDialog


class PortraitAdjustDialog(DialogFactory.BaseDialog):
    """人物抠图对话框：中部是画笔/自动抠图按钮"""

    def _build_mid_controls(self):
        """构建抠图相关按钮"""
        ttk.Button(
            self.mid_frame,
            text="画笔模式",
            command=self._enable_brush_mode,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.mid_frame,
            text="自动抠图",
            command=self._auto_cutout,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.mid_frame,
            text="加载背景图片",
            command=self._choose_background,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

        # 画笔参数
        self.brush_mode = False
        self.brush_size = 5
        self.brush_color = self.style_config['color_danger']  # 使用配置的危险色

        # 背景图片参数
        self.background_image = None

    def _enable_brush_mode(self):
        """激活画笔模式"""
        self.brush_mode = not self.brush_mode
        if self.brush_mode:
            self.canvas.bind("<B1-Motion>", self._draw_on_canvas)
            print("画笔模式已激活：按住鼠标左键在图片上绘制")
        else:
            self.canvas.unbind("<B1-Motion>")
            print("画笔模式已关闭")

    def _draw_on_canvas(self, event):
        """在画布上绘制"""
        if self.brush_mode and self.display_image:
            # 计算画布上的相对坐标
            x = event.x
            y = event.y
            # 在画布上绘制圆形画笔痕迹
            self.canvas.create_oval(
                x - self.brush_size, y - self.brush_size,
                x + self.brush_size, y + self.brush_size,
                fill="red", outline="red"
            )

    def _auto_cutout(self):
        """自动抠图（仅占位，不实现具体功能）"""
        modnet_manager = ModnetManager.ModnetManager(
            model_path='pretrained/modnet_photographic_portrait_matting.ckpt',
            output_dir='pretrained/output'
        )
        modnet_manager.process_portrait_image(
            image=self.original_image,
            save_matte=True,
            save_composite=True
        )

    def _choose_background(self):
        dialog = ImageBrowserDialog.ImageBrowserDialog(self, r"database", self._bind_background_image)
        self.wait_window(dialog)  # 阻塞直到对话框关闭

    def _bind_background_image(self, image):
        """回调函数：将选中的图片绑定到类属性，并转换为Tkinter可显示格式"""
        self.background_image = image

    def get_portrait_image(self):
        pass

    def get_composite_image(self):
        pass


class PortraitAdjustDialogFactory(DialogFactory.AbstractDialogFactory):
    """人物抠图对话框工厂"""

    def create_dialog(self, parent, title="人物调节对话框", image=None):
        dialog = PortraitAdjustDialog(parent, title)
        dialog.load_image(image)
        return dialog
