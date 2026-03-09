import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps
import DialogFactory


# ===================== 具体实现层 - 二值调节对话框 =====================
class BinaryAdjustDialog(DialogFactory.BaseDialog):
    """二值调节对话框：中部是滑块控件"""

    def _build_mid_controls(self):
        """构建二值调节滑块"""
        ttk.Label(
            self.mid_frame,
            text="二值化阈值调节：",
            style="Normal.TLabel"
        ).pack(side=tk.LEFT, padx=5)

        self.slider = ttk.Scale(
            self.mid_frame,
            from_=0, to=255,
            orient=tk.HORIZONTAL,
            command=self._on_slider_change,
            length=300,
            style="Custom.Horizontal.TScale"
        )
        self.slider.set(128)  # 默认阈值
        self.slider.pack(side=tk.LEFT, padx=5)

        self.threshold_label = ttk.Label(
            self.mid_frame,
            text="阈值：128",
            style="Normal.TLabel"
        )
        self.threshold_label.pack(side=tk.LEFT, padx=5)

    def _on_slider_change(self, value):
        """滑块调节二值化阈值"""
        threshold = int(float(value))
        self.threshold_label.config(text=f"阈值：{threshold}")

        if self.original_image:
            # 转灰度图后二值化
            gray_img = ImageOps.grayscale(self.original_image)
            binary_img = gray_img.point(lambda x: 255 if x > threshold else 0)
            # 转回RGBA以便和其他功能兼容
            self.display_image = Image.merge("RGBA",
                                             (binary_img, binary_img, binary_img, self.original_image.split()[3]))
            self._update_canvas_image()


class BinaryDialogFactory(DialogFactory.AbstractDialogFactory):
    """二值调节对话框工厂"""

    def create_dialog(self, parent, title="二值调节对话框", image=None):
        dialog = BinaryAdjustDialog(parent, title)
        dialog.load_image(image)
        return dialog
