import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import DialogFactory
#import modnet.ModnetManager
#import deep_image_matting.DeepImageMattingManger

class BackgroundAdjustDialog(DialogFactory.BaseDialog):
    """背景调节对话框：中部是融合按钮+加载背景图按钮"""

    def _build_mid_controls(self):
        """构建背景调节相关按钮"""
        ttk.Button(
            self.mid_frame,
            text="加载前景图片",
            command=self._load_foreground_image,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.mid_frame,
            text="背景融合（未实现）",
            command=self._background_blend,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

        # 背景图相关变量
        self.bg_image = None
        self.bg_photo = None
        self.bg_x = 0
        self.bg_y = 0

    def _load_foreground_image(self):
        """加载背景图片（限制大小）"""
        img_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp")]
        )
        if img_path:
            # 限制背景图最大尺寸为画布大小
            self.bg_image = Image.open(img_path).convert("RGBA")
            self.bg_image.thumbnail((600, 400), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            # 绑定拖动事件
            self.canvas.bind("<Button-1>", self._start_drag)
            self.canvas.bind("<B1-Motion>", self._drag_bg)
            self._update_background_display()

    def _start_drag(self, event):
        """开始拖动背景图"""
        if self.bg_image:
            self.dragging = True
            self.drag_x = event.x
            self.drag_y = event.y

    def _drag_bg(self, event):
        """拖动背景图"""
        if self.dragging and self.bg_image:
            # 计算拖动偏移量
            dx = event.x - self.drag_x
            dy = event.y - self.drag_y
            self.bg_x += dx
            self.bg_y += dy
            self.drag_x = event.x
            self.drag_y = event.y
            self._update_background_display()

    def _update_background_display(self):
        """更新背景图显示"""
        if self.bg_image:
            self.canvas.delete("all")
            # 绘制背景图
            self.canvas.create_image(
                self.bg_x, self.bg_y,
                image=self.bg_photo,
                anchor=tk.NW
            )
            # 如果有前景图，叠加显示
            if self.display_image:
                fg_photo = ImageTk.PhotoImage(self.display_image)
                self.canvas.create_image(
                    self.canvas.winfo_width() // 2,
                    self.canvas.winfo_height() // 2,
                    image=fg_photo,
                    anchor=tk.CENTER
                )
                # 保存引用防止被GC回收
                self.canvas.fg_photo = fg_photo

    def _background_blend(self):
        """背景融合（仅占位）"""
        tk.messagebox.showinfo("提示", "背景融合功能暂未实现")


class BackgroundAdjustDialogFactory(DialogFactory.AbstractDialogFactory):
    """背景调节对话框工厂"""

    def create_dialog(self, parent, title="背景图片调节对话框",image=None):
        dialog = BackgroundAdjustDialog(parent, title)
        dialog.load_image(image)
        return dialog