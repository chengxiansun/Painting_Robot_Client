import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont
import cv2
from PIL import Image, ImageTk
from typing import Dict, Union
import ComponentFactory
import DialogFactory
import DialogFactoryManager
import AiRepaint
import ImageBrowserDialog


class FaceDrawingApp(tk.Tk):
    """人脸绘制应用主类"""

    def __init__(self):
        super().__init__()

        # 基础配置
        self.title("ABBDrawFace")
        self._setup_window_size()

        # 画布比例 (420mm × 594mm) -> 宽高比 = 420/594 ≈ 0.707
        self.A2_ASPECT_RATIO = 420 / 594

        # 样式配置
        self._setup_style_config()
        self._setup_ttk_styles()

        # 初始化组件工厂
        self.component_factory = ComponentFactory.ComponentFactory(self, self.style_config)

        # 初始化状态变量
        self.camera_capture = None
        self.camera_is_running = False
        self.ai_repaint_style = 0

        # 创建UI组件
        self._create_ui_components()

        # 绑定事件
        self._bind_events()

        # 变量
        self.origin_image_path = 'camera/test.png'
        self.origin_image = None
        # self.background_image = None
        self.ai_repaint_image = None
        self.preview_image = None

    def _setup_window_size(self):
        """设置窗口尺寸（自适应屏幕）"""
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 设置窗口为屏幕90%大小
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.7)
        self.geometry(f"{window_width}x{window_height}")

        # 设置最小尺寸为屏幕60%
        self.minsize(int(screen_width * 0.6), int(screen_height * 0.6))

    def _setup_style_config(self):
        """配置样式常量（颜色、字体）"""
        # 颜色配置（Windows 11风格）
        self.style_config: Dict[str, Union[str, tuple[str, int], tuple[str, int, str]]] = {
            'color_primary': "#0078d4",
            'color_success': "#107c10",
            'color_warning': "#ffb900",
            'color_danger': "#d13438",
            'color_info': "#0066cc",
            'color_light': "#f8f9fa",
            'color_gray': "#dee2e6",
            'color_muted': "#6c757d"
        }

        # 字体配置（适配Windows/Mac）
        font_family = "Microsoft YaHei UI" if "Microsoft YaHei UI" in tkfont.families() else "SF Pro Display"
        self.style_config['font_normal'] = (font_family, 11)
        self.style_config['font_bold'] = (font_family, 11, "bold")
        self.style_config['font_small'] = (font_family, 10)

    def _setup_ttk_styles(self):
        """配置TTK组件样式"""
        style = ttk.Style(self)

        # 标签框架样式
        style.configure("Custom.TLabelframe",
                        font=self.style_config['font_bold'],
                        foreground=self.style_config['color_info'])
        style.configure("Custom.TLabelframe.Label",
                        font=self.style_config['font_bold'],
                        foreground=self.style_config['color_info'])

        # 下拉框样式
        style.configure("Custom.TCombobox",
                        font=self.style_config['font_normal'])

        # 滑块样式
        style.configure("Custom.Horizontal.TScale",
                        troughcolor=self.style_config['color_gray'],
                        background=self.style_config['color_primary'],
                        bordercolor=self.style_config['color_info'])

        # 标签样式
        style.configure("Custom.TLabel",
                        font=self.style_config['font_normal'])

    def _create_ui_components(self):
        """创建所有UI组件（通过工厂模式）"""
        # 面板间距配置
        self.panel_padding = {"padx": 12, "pady": 8}
        self.grid_padding = {"padx": 6, "pady": 6}

        # ====================== 主容器布局 ======================
        # 顶部：图片显示区域
        self.top_container = ttk.Frame(self)
        self.top_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        # 底部：功能面板区域（AI重绘区 + 图片调节区 左右布局）
        self.bottom_container = ttk.Frame(self)
        self.bottom_container.pack(fill=tk.X, padx=10, pady=10)

        # 底部容器布局：AI重绘区（左），图片调节区（右）
        self.bottom_container.grid_columnconfigure(0, weight=1)
        self.bottom_container.grid_columnconfigure(1, weight=1)
        self.bottom_container.grid_rowconfigure(0, weight=1)

        # ====================== 核心容器：图片区域 ======================
        # 修改为1×4横向排列的核心布局
        self.image_container_main = ttk.PanedWindow(self.top_container, orient=tk.HORIZONTAL)
        self.image_container_main.pack(fill=tk.BOTH, expand=True)

        # 1. AI重绘面板（第一个画布）
        self.panel_ai_repaint = ttk.Frame(self.image_container_main)
        self.image_container_main.add(self.panel_ai_repaint, weight=1)
        self.panel_ai_repaint.grid_rowconfigure(0, weight=0)
        self.panel_ai_repaint.grid_rowconfigure(1, weight=1)
        self.panel_ai_repaint.grid_columnconfigure(0, weight=1)

        self.label_ai_repaint_area = self.component_factory.create_label(
            self.panel_ai_repaint,
            text="AI重绘",
            style="Custom.TLabel",
            foreground=self.style_config['color_info']
        )
        self.label_ai_repaint_area.grid(row=0, column=0, sticky="ew", pady=(10, 2))

        self.canvas_ai_repaint = self.component_factory.create_canvas(
            self.panel_ai_repaint,
            bg_color=self.style_config['color_light'],
            highlight_color=self.style_config['color_gray']
        )
        self.canvas_ai_repaint.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        # self.canvas_ai_repaint.bind("<Configure>",
        #                             lambda e,
        #                                    c=self.canvas_ai_repaint: self.component_factory._maintain_canvas_aspect_ratio(
        #                                 c, self.A2_ASPECT_RATIO))

        # 2. 原图面板（第二个画布）
        self.panel_original_face = ttk.Frame(self.image_container_main)
        self.image_container_main.add(self.panel_original_face, weight=1)
        self.panel_original_face.grid_rowconfigure(0, weight=0)
        self.panel_original_face.grid_rowconfigure(1, weight=1)
        self.panel_original_face.grid_columnconfigure(0, weight=1)

        self.label_original_image = self.component_factory.create_label(
            self.panel_original_face,
            text="原图",
            style="Custom.TLabel",
            foreground=self.style_config['color_info']
        )
        self.label_original_image.grid(row=0, column=0, sticky="ew", pady=(10, 2))

        self.canvas_original_face = self.component_factory.create_canvas(
            self.panel_original_face,
            bg_color=self.style_config['color_light'],
            highlight_color=self.style_config['color_gray']
        )
        self.canvas_original_face.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        # self.canvas_original_face.bind("<Configure>",
        #                                lambda e,
        #                                       c=self.canvas_original_face: self.component_factory._maintain_canvas_aspect_ratio(
        #                                    c, self.A2_ASPECT_RATIO))

        # 3. 背景面板（第三个画布）
        # self.panel_background = ttk.Frame(self.image_container_main)
        # self.image_container_main.add(self.panel_background, weight=1)
        # self.panel_background.grid_rowconfigure(0, weight=0)
        # self.panel_background.grid_rowconfigure(1, weight=1)
        # self.panel_background.grid_columnconfigure(0, weight=1)

        # self.label_background_image = self.component_factory.create_label(
        #     self.panel_background,
        #     text="背景",
        #     style="Custom.TLabel",
        #     foreground=self.style_config['color_info']
        # )
        # self.label_background_image.grid(row=0, column=0, sticky="ew", pady=(10, 2))

        # self.canvas_background = self.component_factory.create_canvas(
        #     self.panel_background,
        #     bg_color=self.style_config['color_light'],
        #     highlight_color=self.style_config['color_gray']
        # )
        # self.canvas_background.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        # self.canvas_background.bind("<Configure>",
        #                             lambda e,
        #                                    c=self.canvas_background: self.component_factory._maintain_canvas_aspect_ratio(
        #                                 c, self.A2_ASPECT_RATIO))

        # 4. 预览面板（第四个画布）
        self.panel_preview = ttk.Frame(self.image_container_main)
        self.image_container_main.add(self.panel_preview, weight=1)
        self.panel_preview.grid_rowconfigure(0, weight=0)
        self.panel_preview.grid_rowconfigure(1, weight=1)
        self.panel_preview.grid_columnconfigure(0, weight=1)

        self.label_preview_image = self.component_factory.create_label(
            self.panel_preview,
            text="预览",
            style="Custom.TLabel",
            foreground=self.style_config['color_info']
        )
        self.label_preview_image.grid(row=0, column=0, sticky="ew", pady=(10, 2))

        self.canvas_preview = self.component_factory.create_canvas(
            self.panel_preview,
            bg_color=self.style_config['color_light'],
            highlight_color=self.style_config['color_gray']
        )
        self.canvas_preview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        # self.canvas_preview.bind("<Configure>",
        #                          lambda e, c=self.canvas_preview: self.component_factory._maintain_canvas_aspect_ratio(
        #                              c, self.A2_ASPECT_RATIO))

        # ====================== 功能面板区域（重新布局） ======================
        # 1. AI重绘面板（左侧）
        self.panel_ai_repaint_controls = self.component_factory.create_label_frame(
            self.bottom_container,
            text="AI重绘",
            style="Custom.TLabelframe",
            padding=10
        )
        self.panel_ai_repaint_controls.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        # 配置网格权重
        for i in range(3):
            self.panel_ai_repaint_controls.grid_columnconfigure(i, weight=1)

        # AI风格选择框架
        self.frame_ai_style = ttk.Frame(self.panel_ai_repaint_controls)
        self.frame_ai_style.grid(row=0, column=0, **self.grid_padding)

        self.label_ai_style_select = self.component_factory.create_label(
            self.frame_ai_style,
            text="风格选择",
            style="Custom.TLabel",
            foreground=self.style_config['color_info']
        )
        self.label_ai_style_select.pack(side=tk.LEFT, padx=(0, 5))

        # AI风格下拉框
        ai_style_values = [
            "复古漫画", "3D童话", "二次元", "小清新", "未来科技", "国画古风",
            "将军百战", "炫彩卡通", "清雅国风", "喜迎新年", "国风工笔", "恭贺新禧",
            "童话世界", "黏土世界", "像素世界", "冒险世界", "日漫世界", "3D世界",
            "二次元世界", "手绘世界", "蜡笔世界", "冰箱贴世界", "吧唧世界"
        ]
        self.combobox_ai_style = self.component_factory.create_combobox(
            self.frame_ai_style,
            values=ai_style_values,
            default_index=0,
            width=15
        )
        self.combobox_ai_style.pack(side=tk.LEFT)

        # AI重绘按钮
        self.button_ai_repaint = self.component_factory.create_button(
            self.panel_ai_repaint_controls,
            text="AI图片重绘",
            bg_color=self.style_config['color_success'],
            fg_color="white",
            width=15,
            command=self.on_ai_repaint_click
        )
        self.button_ai_repaint.grid(row=0, column=1, **self.grid_padding)
        # 取消AI绘制按钮
        self.button_ai_repaint_cancel = self.component_factory.create_button(
            self.panel_ai_repaint_controls,
            text="清空AI图片重绘",
            bg_color=self.style_config['color_danger'],
            fg_color="white",
            width=15,
            command=self.on_ai_repaint_cancel_click
        )
        self.button_ai_repaint_cancel.grid(row=0, column=2, **self.grid_padding)
        # 2. 图片调节面板（右侧）
        self.panel_image_adjust = self.component_factory.create_label_frame(
            self.bottom_container,
            text="图片调节",
            style="Custom.TLabelframe",
            padding=10
        )
        self.panel_image_adjust.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        # 配置网格权重
        for i in range(6):
            self.panel_image_adjust.grid_columnconfigure(i, weight=1)

        # 图片调节按钮
        self.button_binary_adjust = self.component_factory.create_button(
            self.panel_image_adjust,
            text="二值化调节",
            bg_color=self.style_config['color_primary'],
            fg_color="white",
            width=15,
            command=self.on_binary_adjust_click,
        )
        self.button_binary_adjust.config(state=tk.DISABLED)
        self.button_binary_adjust.grid(row=0, column=1, **self.grid_padding)

        self.button_portrait_adjust = self.component_factory.create_button(
            self.panel_image_adjust,
            text="人物抠图调节",
            bg_color=self.style_config['color_primary'],
            fg_color="white",
            width=15,
            command=self.on_portrait_adjust_click,
        )
        self.button_portrait_adjust.config(state=tk.DISABLED)
        self.button_portrait_adjust.grid(row=0, column=2, **self.grid_padding)

        # self.button_background_adjust = self.component_factory.create_button(
        #     self.panel_image_adjust,
        #     text="背景抠图调节",
        #     bg_color=self.style_config['color_primary'],
        #     fg_color="white",
        #     width=15,
        #     command=self.on_background_adjust_click
        # )
        # self.button_background_adjust.config(state=tk.DISABLED)
        # self.button_background_adjust.grid(row=0, column=3, **self.grid_padding)

        self.button_robot_paint = self.component_factory.create_button(
            self.panel_image_adjust,
            text="机器人绘图",
            bg_color=self.style_config['color_success'],
            fg_color="white",
            width=15,
            command=self.on_robot_paint_click
        )
        self.button_robot_paint.config(state=tk.DISABLED)
        self.button_robot_paint.grid(row=0, column=4, **self.grid_padding)

        # 3. 相片选择面板（独立行）
        self.panel_photo_select = self.component_factory.create_label_frame(
            self,
            text="相片选择",
            style="Custom.TLabelframe",
            padding=10
        )
        self.panel_photo_select.pack(side=tk.BOTTOM, fill=tk.X, **self.panel_padding)

        # 配置网格权重
        for i in range(2):
            self.panel_photo_select.grid_columnconfigure(i, weight=1)

        # 本地相册按钮
        self.button_local_album = self.component_factory.create_button(
            self.panel_photo_select,
            text="本地相册",
            bg_color=self.style_config['color_primary'],
            fg_color="white",
            width=12,
            command=self.on_local_album_click
        )
        self.button_local_album.grid(row=0, column=0, **self.grid_padding)

        # 相机拍摄按钮
        self.button_camera_shoot = self.component_factory.create_button(
            self.panel_photo_select,
            text="相机拍摄",
            bg_color=self.style_config['color_primary'],
            fg_color="white",
            width=12,
            command=self.on_camera_shoot_click
        )
        self.button_camera_shoot.grid(row=0, column=1, **self.grid_padding)

        # # 背景选择按钮
        # self.button_background_select = self.component_factory.create_button(
        #     self.panel_photo_select,
        #     text="背景选择",
        #     bg_color=self.style_config['color_primary'],
        #     fg_color="white",
        #     width=12,
        #     command=self.on_background_select_click
        # )
        # self.button_background_select.grid(row=0, column=2, **self.grid_padding)

    def open_adjust_dialog(self, dialog_type):
        """打开指定类型的对话框"""
        factory = DialogFactoryManager.DialogFactoryManager.get_factory(dialog_type)

        if factory:
            if self.ai_repaint_image is not None:
                img = self.ai_repaint_image
            else:
                img = self.origin_image

            if dialog_type == "binary" and self.preview_image is not None:
                img = self.ai_repaint_image
            elif dialog_type == "portrait":
                # 抠图选择原始图片或AI图片
                pass

            dialog = factory.create_dialog(self, image=img)

            self.wait_window(dialog)
            if dialog.result:
                self.preview_image = dialog.result
                current_state = self.button_robot_paint.cget("state")
                if current_state == tk.DISABLED:
                    self.button_robot_paint.config(state=tk.NORMAL)

    def _bind_events(self):
        """绑定所有组件事件"""
        # AI风格下拉框选择事件
        self.combobox_ai_style.bind("<<ComboboxSelected>>", self.on_ai_style_select)

    # -------------------- 核心功能事件 --------------------
    def on_ai_style_select(self, event):
        """AI风格选择事件"""
        selected_style = self.combobox_ai_style.get()
        style_index_map = {
            "复古漫画": 0, "3D童话": 1, "二次元": 2, "小清新": 3, "未来科技": 4, "国画古风": 5,
            "将军百战": 6, "炫彩卡通": 7, "清雅国风": 8, "喜迎新年": 9, "国风工笔": 14, "恭贺新禧": 15,
            "童话世界": 30, "黏土世界": 31, "像素世界": 32, "冒险世界": 33, "日漫世界": 34,
            "3D世界": 35, "二次元世界": 36, "手绘世界": 37, "蜡笔世界": 38, "冰箱贴世界": 39,
            "吧唧世界": 40
        }
        self.ai_repaint_style = style_index_map.get(selected_style, 0)

    def on_binary_adjust_click(self):
        self.open_adjust_dialog("binary")

    # def on_background_adjust_click(self):
    #     self.open_adjust_dialog("background")

    def on_portrait_adjust_click(self):
        self.open_adjust_dialog("portrait")

    def on_choose_image(self):
        """选择本地图片并显示"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.origin_image_path = file_path
            try:
                # 获取画布尺寸
                canvas_width = self.canvas_original_face.winfo_width()
                canvas_height = self.canvas_original_face.winfo_height()

                # 默认尺寸（画布未渲染时）
                if canvas_width < 10 or canvas_height < 10:
                    canvas_width = 300
                    canvas_height = int(300 / self.A2_ASPECT_RATIO)  # 保持A2比例

                # 加载并调整图片大小
                self.origin_image = Image.open(file_path)
                img = self.origin_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # 显示图片
                self.canvas_original_face.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas_original_face.image = photo
            except Exception as e:
                messagebox.showerror("错误", f"加载图片失败：{str(e)}")

    def on_camera_preview_toggle(self):
        """切换摄像头预览/拍摄状态"""
        if not self.camera_is_running:
            # 启动摄像头预览
            try:
                # 使用默认摄像头0
                camera_index = 0
                self.camera_capture = cv2.VideoCapture(camera_index, cv2.CAP_ANY)

                if not self.camera_capture.isOpened():
                    raise Exception("无法打开摄像头")

                # 设置摄像头参数（保持A2比例）
                self.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(640 / self.A2_ASPECT_RATIO))

                self.camera_is_running = True
                self.button_camera_shoot.config(text="停止/拍摄")
                self._update_camera_frame()
                messagebox.showinfo("提示", "摄像头预览已启动，再次点击按钮拍摄照片！")
            except Exception as e:
                messagebox.showerror("错误", f"启动摄像头失败：{str(e)}")
        else:
            # 停止预览并拍摄
            if self.camera_capture:
                ret, frame = self.camera_capture.read()
                if ret:
                    # 转换颜色空间并显示
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)

                    # 调整尺寸
                    canvas_width = self.canvas_original_face.winfo_width()
                    canvas_height = self.canvas_original_face.winfo_height()
                    if canvas_width < 10 or canvas_height < 10:
                        canvas_width = 300
                        canvas_height = int(300 / self.A2_ASPECT_RATIO)

                    img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.canvas_original_face.create_image(0, 0, anchor=tk.NW, image=photo)
                    self.canvas_original_face.image = photo

                # 释放摄像头
                self.camera_capture.release()
                self.camera_is_running = False
                self.button_camera_shoot.config(text="相机拍摄")
                messagebox.showinfo("提示", "照片拍摄完成！" if ret else "拍摄失败，未捕获到画面！")

    def _update_camera_frame(self):
        """更新摄像头帧显示"""
        if self.camera_is_running and self.camera_capture:
            ret, frame = self.camera_capture.read()
            if ret:
                # 转换并调整尺寸
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)

                canvas_width = self.canvas_original_face.winfo_width()
                canvas_height = self.canvas_original_face.winfo_height()
                if canvas_width < 10 or canvas_height < 10:
                    canvas_width = 300
                    canvas_height = int(300 / self.A2_ASPECT_RATIO)

                img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # 显示帧
                self.canvas_original_face.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas_original_face.image = photo

            # 定时更新（30ms）
            self.after(30, self._update_camera_frame)

    # -------------------- 按钮点击事件 --------------------

    def on_local_album_click(self):
        """本地相册按钮点击事件"""
        self.on_choose_image()
        if self.canvas_original_face is not None:
            current_state_binary = self.button_binary_adjust.cget("state")
            if current_state_binary == tk.DISABLED:
                self.button_binary_adjust.config(state=tk.NORMAL)
            current_state_portrait = self.button_portrait_adjust.cget("state")

            if current_state_portrait == tk.DISABLED:
                self.button_portrait_adjust.config(state=tk.NORMAL)

    def on_camera_shoot_click(self):
        """相机拍摄按钮点击事件"""
        self.on_camera_preview_toggle()
        if self.canvas_original_face is not None:
            current_state = self.button_binary_adjust.cget("state")
            if current_state == tk.DISABLED:
                self.button_binary_adjust.config(state=tk.NORMAL)
                self.button_portrait_adjust.config(state=tk.NORMAL)

    # def _bind_background_image(self, image):
    #     """回调函数：将选中的图片绑定到类属性，并转换为Tkinter可显示格式"""
    #     self.background_image = image

    # def on_background_select_click(self):
    #     """背景选择按钮点击事件"""
    #     dialog = ImageBrowserDialog.ImageBrowserDialog(self, r"database", self._bind_background_image)
    #     self.wait_window(dialog)  # 阻塞直到对话框关闭
    #     # 获取画布尺寸
    #     canvas_width = self.canvas_background.winfo_width()
    #     canvas_height = self.canvas_background.winfo_height()
    #
    #     # 默认尺寸（画布未渲染时）
    #     if canvas_width < 10 or canvas_height < 10:
    #         canvas_width = 300
    #         canvas_height = int(300 / self.A2_ASPECT_RATIO)  # 保持A2比例
    #     img = self.background_image
    #     img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    #     photo = ImageTk.PhotoImage(img)
    #
    #     # 显示图片
    #     self.canvas_background.create_image(0, 0, anchor=tk.NW, image=photo)
    #     self.canvas_background.image = photo
    #
    #     if self.canvas_background.image is not None:
    #         current_state = self.button_background_adjust.cget("state")
    #         if current_state == tk.DISABLED:
    #             self.button_background_adjust.config(state=tk.NORMAL)

    def on_ai_repaint_cancel_click(self):
        if self.ai_repaint_image:
            self.canvas_ai_repaint.delete(self.ai_repaint_image)  # 删除指定图片
            self.ai_repaint_image = None  # 重置
            self.canvas_ai_repaint.image = None  # 清空图片引用

    def on_ai_repaint_click(self):
        # """AI重绘按钮点击事件"""
        image_repaint = AiRepaint.ImageRepainter()
        if image_repaint.submit_task(image_path=self.origin_image_path, style_index=0):
            # 查询结果并下载图片（默认展示图片）
            image_repaint.query_task_result(show_images=False)
            self.ai_repaint_image = image_repaint.get_ai_repaint_image()
            # 手动清理图片（也可以等待析构函数自动清理）
            image_repaint.cleanup_images()
        canvas_width = self.canvas_ai_repaint.winfo_width()
        canvas_height = self.canvas_ai_repaint.winfo_height()

        # 默认尺寸（画布未渲染时）
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = 300
            canvas_height = int(300 / self.A2_ASPECT_RATIO)  # 保持A2比例

        img = self.ai_repaint_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.canvas_ai_repaint.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas_ai_repaint.image = photo

    def on_robot_paint_click(self):
        """机器人绘图按钮点击事件"""
        messagebox.showinfo("提示", "机器人绘图功能已触发！")

    def __del__(self):
        """析构函数：释放摄像头资源"""
        if self.camera_capture:
            self.camera_capture.release()
        cv2.destroyAllWindows()
