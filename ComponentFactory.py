import tkinter as tk
from tkinter import ttk


class ComponentFactory:
    """UI组件工厂类 - 负责所有UI主界面组件的创建"""

    def __init__(self, parent, style_config):
        self.parent = parent
        self.style_config = style_config  # 样式配置字典

    def create_canvas(self, parent, bg_color, highlight_color):
        """创建画布组件"""
        canvas = tk.Canvas(
            parent,
            bd=0,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground=highlight_color
        )
        return canvas

    def create_button(self, parent, text, bg_color, fg_color, width, command):
        """创建按钮组件"""
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

    def create_label(self, parent, text, style, foreground):
        """创建标签组件"""
        label = ttk.Label(
            parent,
            text=text,
            style=style,
            foreground=foreground
        )
        return label

    def create_combobox(self, parent, values, default_index, width):
        """创建下拉框组件"""
        combobox = ttk.Combobox(
            parent,
            font=("SimSun", 12),
            width=width,
            state="readonly"
        )
        combobox['values'] = values
        combobox.current(default_index)
        return combobox

    def create_label_frame(self, parent, text, style, padding):
        """创建带标签的框架组件"""
        label_frame = ttk.LabelFrame(
            parent,
            text=text,
            style=style,
            padding=padding
        )
        return label_frame

    def create_paned_window(self, parent, orient):
        """创建可拆分窗口组件"""
        paned_window = ttk.Panedwindow(parent, orient=orient)
        return paned_window
