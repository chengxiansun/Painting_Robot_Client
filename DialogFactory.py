import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, font as tkfont
from typing import Dict, Union


class AbstractDialogFactory:
    """抽象对话框工厂：定义创建对话框的接口"""

    def create_dialog(self, parent, title="自定义对话框", image_path=""):
        raise NotImplementedError("子类必须实现create_dialog方法")


class BaseDialog(tk.Toplevel):
    """所有对话框的基类：封装通用UI和逻辑"""

    def __init__(self, parent, title):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.result = None
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()  # 模态对话框

        # 初始化画布相关变量
        self.canvas = None  # 替换原canvas变量名，匹配目标逻辑
        self.canvas_image = None
        self.original_image = None  # 原始图像
        self.display_image = None  # 显示用图像
        self.dragging = False  # 拖动标记（背景调节用）
        self.drag_x = 0
        self.drag_y = 0

        # 1. 配置样式常量（与原有代码格式统一）
        self._setup_style_config()
        # 2. 初始化ttk样式
        self._init_ttk_style()
        # 3. 构建通用UI框架
        self._build_ui()
        # 4. 窗口居中
        self._center_window()

    def _setup_style_config(self):
        """配置样式常量（颜色、字体）- 与原有代码格式统一"""
        # 颜色配置（Windows 11风格，保持与原有代码一致的基础配色）
        self.style_config: Dict[str, Union[str, tuple[str, int], tuple[str, int, str]]] = {
            'color_primary': "#0078d4",
            'color_success': "#107c10",
            'color_warning': "#ffb900",
            'color_danger': "#d13438",
            'color_info': "#0066cc",
            'color_light': "#f8f9fa",
            'color_gray': "#dee2e6",
            'color_muted': "#6c757d",
            'color_primary_hover': "#1686e0",
            'color_success_hover': "#148f14",
            'color_danger_hover': "#e53f43",
            'color_gray_dark': "#adb5bd",
            'color_white': "#ffffff"
        }

        # 字体配置（与原有代码完全一致）
        font_family = "Microsoft YaHei UI" if "Microsoft YaHei UI" in tkfont.families() else "SF Pro Display"
        self.style_config['font_normal'] = (font_family, 11)
        self.style_config['font_bold'] = (font_family, 11, "bold")
        self.style_config['font_small'] = (font_family, 10)

    def create_button(self, parent, text, bg_color, fg_color, width, command):
        """创建按钮组件 - 复用原有代码的按钮创建方式"""
        button = tk.Button(
            parent,
            text=text,
            font=self.style_config['font_normal'],
            bg=bg_color,
            fg=fg_color,
            width=width,
            command=command
        )
        return button

    def _init_ttk_style(self):
        """初始化ttk控件样式（保持原有格式，简化冗余配置）"""
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # clam主题支持最完整的样式自定义

        # 滑块样式（与原有代码格式完全一致）
        self.style.configure("Custom.Horizontal.TScale",
                             troughcolor=self.style_config['color_gray'],
                             background=self.style_config['color_primary'],
                             bordercolor=self.style_config['color_info'])

        # 标签样式（与原有代码格式完全一致）
        self.style.configure("Custom.TLabel",
                             font=self.style_config['font_normal'])

        # 保留必要的按钮样式（兼容原有ttk按钮使用场景）
        self.style.configure(
            "Success.TButton",
            foreground=self.style_config['color_white'],
            fieldbackground=self.style_config['color_success'],
            font=self.style_config['font_normal'],
            padding=(12, 6),
            borderwidth=0,
            relief="flat"
        )
        self.style.configure(
            "Danger.TButton",
            foreground=self.style_config['color_white'],
            fieldbackground=self.style_config['color_danger'],
            font=self.style_config['font_normal'],
            padding=(12, 6),
            borderwidth=0,
            relief="flat"
        )

    def _build_ui(self):
        """构建通用UI：顶部画布 + 中部自定义区域 + 底部按钮"""
        # 设置窗口背景色
        self.configure(bg=self.style_config['color_light'])

        canvas_frame = ttk.Frame(self, padding="10")
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.style_config['color_light'],
            width=600,
            height=400,
            highlightthickness=1,
            highlightbackground=self.style_config['color_gray']
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 2. 中部自定义控件区域（由子类实现）
        self.mid_frame = ttk.Frame(self, padding="10")
        self.mid_frame.pack(fill=tk.X)
        self._build_mid_controls()

        # 3. 底部按钮区域（改用统一的create_button方法创建）
        btn_frame = ttk.Frame(self, padding="10")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 使用统一的按钮创建方法（与原有AI重绘按钮格式一致）
        self.btn_confirm = self.create_button(
            btn_frame,
            text="确认",
            bg_color=self.style_config['color_success'],
            fg_color="white",
            width=15,
            command=self._on_ok
        )
        self.btn_confirm.pack(side=tk.RIGHT, padx=5)

        self.btn_cancel = self.create_button(
            btn_frame,
            text="取消",
            bg_color=self.style_config['color_danger'],
            fg_color="white",
            width=15,
            command=self._on_cancel
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=5)

    def _build_mid_controls(self):
        """中部自定义控件：添加与原有格式一致的滑块"""
        # 标签使用统一的Custom.TLabel样式
        scale_label = ttk.Label(self.mid_frame, text="示例滑块：", style="Custom.TLabel")
        scale_label.pack(side=tk.LEFT, padx=5, pady=5)

        # 滑块使用与原有代码一致的Custom.Horizontal.TScale样式
        demo_scale = ttk.Scale(
            self.mid_frame,
            orient=tk.HORIZONTAL,
            style="Custom.Horizontal.TScale",
            from_=0,
            to=100,
            value=50
        )
        demo_scale.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

    def _center_window(self):
        """窗口居中"""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_ok(self):
        """通用确认逻辑"""
        self.result = self.display_image
        self.destroy()

    def _on_cancel(self):
        """通用取消逻辑"""
        self.result = None
        self.destroy()

    def load_image(self, img):
        """修改后的加载图片逻辑：固定resize到画布尺寸，NW锚点显示"""
        try:
            # 1. 打开原始图片并转换为RGBA（保持原有格式兼容）
            self.original_image = img

            # 2. 获取画布的宽高（匹配目标逻辑的canvas_width/canvas_height）
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width < 10 or canvas_height < 10:
                canvas_width = 600
                canvas_height = 400

            # 3. 强制resize到画布尺寸（使用指定的LANCZOS采样）
            self.display_image = self.original_image.resize(
                (canvas_width, canvas_height),
                Image.Resampling.LANCZOS
            )

            # 4. 更新画布显示
            self._update_canvas_image()
        except Exception as e:
            print(f"加载图片失败：{e}")

    def _update_canvas_image(self):
        """修改后的画布更新逻辑：0,0位置、NW锚点显示"""
        if self.display_image:
            # 转换为tkinter可用的PhotoImage
            self.canvas_image = ImageTk.PhotoImage(self.display_image)
            # 清空画布并绘制图片（0,0位置，NW锚点）
            self.canvas.delete("all")
            self.canvas.create_image(
                0, 0,
                anchor=tk.NW,
                image=self.canvas_image
            )

            # 保留引用防止图片被GC回收（关键）
            self.canvas.image = self.canvas_image
# 测试代码
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 创建对话框并加载图片
    dialog = BaseDialog(root, "测试图片加载")
    dialog.load_image("test.png")  # 替换为你的图片路径

    root.mainloop()