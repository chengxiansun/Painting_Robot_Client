import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import ttkbootstrap as ttkbs  # 需确保版本≥1.10.0


class Form1(ttkbs.Window):
    def __init__(self):
        # 选择兼容主题（cosmo=微软风格，darkly=苹果风格）
        super().__init__(themename="cosmo")
        self.title("ABBDrawFace")
        self.geometry("1280x768")
        self.minsize(1280, 768)

        # ====================== 核心修改1：配置全局样式（含字体） ======================
        self.style = ttkbs.Style()
        # 定义字体（适配Windows/苹果）
        font_family = "Microsoft YaHei UI" if "Microsoft YaHei UI" in tkfont.families() else "SF Pro Display"
        # 配置不同控件的字体样式
        self.style.configure(
            "Normal.TLabel",  # 普通标签样式
            font=(font_family, 11)
        )
        self.style.configure(
            "Bold.TLabel",  # 粗体标签样式
            font=(font_family, 11, "bold")
        )
        self.style.configure(
            "Small.TLabel",  # 小字体标签样式
            font=(font_family, 10)
        )
        self.style.configure(
            "Normal.TButton",  # 普通按钮样式
            font=(font_family, 11)
        )
        self.style.configure(
            "Normal.TEntry",  # 输入框样式
            font=(font_family, 11)
        )
        self.style.configure(
            "Normal.TCombobox",  # 下拉框样式
            font=(font_family, 11)
        )
        self.style.configure(
            "Normal.TCheckbutton",  # 复选框样式
            font=(font_family, 11)
        )
        self.style.configure(
            "Normal.TRadiobutton",  # 单选框样式
            font=(font_family, 11)
        )

        # 初始化组件（已移除font参数）
        self.initialize_component()
        # 绑定按钮事件
        self.bind_events()

    def initialize_component(self):
        # ====================== 核心容器：SplitContainer（图片区域总拆分） ======================
        self.splitC_img_all = ttkbs.Panedwindow(self, orient=tk.HORIZONTAL, bootstyle="light")
        self.splitC_img_all.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # -------------------- splitC_img_all.Panel1：左侧拆分容器 --------------------
        self.splitContainer2 = ttkbs.Panedwindow(self.splitC_img_all, orient=tk.HORIZONTAL, bootstyle="light")
        self.splitC_img_all.add(self.splitContainer2)

        # 1. tp_img_debug（调试图片面板）
        self.tp_img_debug = ttkbs.Frame(self.splitContainer2, bootstyle="light", padding=8)
        self.splitContainer2.add(self.tp_img_debug, weight=1)

        # - gray_pb（二值化图片框） + label2（改用样式名绑定字体）
        self.label2 = ttkbs.Label(self.tp_img_debug, text="二值化", style="Bold.TLabel", bootstyle="secondary")
        self.label2.pack(side=tk.TOP, anchor=tk.CENTER, pady=4)
        self.gray_pb = ttkbs.Canvas(self.tp_img_debug, bd=0, relief=tk.FLAT, bg="#f8f9fa", highlightthickness=1,
                                    highlightbackground="#dee2e6")
        self.gray_pb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # - face_src_pb（面部图片框） + label1
        self.label1 = ttkbs.Label(self.tp_img_debug, text="面部", style="Bold.TLabel", bootstyle="secondary")
        self.label1.pack(side=tk.TOP, anchor=tk.CENTER, pady=4)
        self.face_src_pb = ttkbs.Canvas(self.tp_img_debug, bd=0, relief=tk.FLAT, bg="#f8f9fa", highlightthickness=1,
                                        highlightbackground="#dee2e6")
        self.face_src_pb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # 2. tp_img_release（发布图片面板）
        self.tp_img_release = ttkbs.Frame(self.splitContainer2, bootstyle="light", padding=8)
        self.splitContainer2.add(self.tp_img_release, weight=1)

        # - fit_pb（拟合图片框） + label4
        self.label4 = ttkbs.Label(self.tp_img_release, text="拟合", style="Bold.TLabel", bootstyle="secondary")
        self.label4.pack(side=tk.TOP, anchor=tk.CENTER, pady=4)
        self.fit_pb = ttkbs.Canvas(self.tp_img_release, bd=0, relief=tk.FLAT, bg="#f8f9fa", highlightthickness=1,
                                   highlightbackground="#dee2e6")
        self.fit_pb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # - svg_pb（预览图片框） + label3
        self.label3 = ttkbs.Label(self.tp_img_release, text="预览", style="Bold.TLabel", bootstyle="secondary")
        self.label3.pack(side=tk.TOP, anchor=tk.CENTER, pady=4)
        self.svg_pb = ttkbs.Canvas(self.tp_img_release, bd=0, relief=tk.FLAT, bg="#f8f9fa", highlightthickness=1,
                                   highlightbackground="#dee2e6")
        self.svg_pb.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # - bt_show_img_d（显示图片调试按钮：移除font参数，改用样式）
        self.bt_show_img_d = ttkbs.Button(self.tp_img_release, text="显示调试图", style="Normal.TButton",
                                          bootstyle="primary")
        self.bt_show_img_d.pack(side=tk.BOTTOM, pady=8, ipady=4, padx=20, fill=tk.X)

        # ====================== 功能面板区域 ======================
        # 统一面板样式配置
        panel_padding = {"padx": 12, "pady": 8}
        grid_padding = {"padx": 6, "pady": 6}

        # 1. panel1（相机控制面板）
        self.panel1 = ttkbs.LabelFrame(self, text="相机控制", style="Bold.TLabel", bootstyle="info", padding=10)
        self.panel1.pack(side=tk.BOTTOM, fill=tk.X, **panel_padding)

        # - 相机选择组（移除font参数）
        self.label9 = ttkbs.Label(self.panel1, text="相机：", style="Normal.TLabel")
        self.label9.grid(row=0, column=0, sticky=tk.W, **grid_padding)
        self.cb_cam_selector = ttkbs.Combobox(self.panel1, style="Normal.TCombobox", state="readonly",
                                              bootstyle="secondary")
        self.cb_cam_selector.grid(row=0, column=1, sticky=tk.W + tk.E, **grid_padding)
        self.cb_is_cam_fixed = ttkbs.Checkbutton(self.panel1, text="固定的相机？", style="Normal.TCheckbutton",
                                                 bootstyle="round-toggle")
        self.cb_is_cam_fixed.grid(row=0, column=2, sticky=tk.W, **grid_padding)

        # - 相机操作按钮（移除font参数）
        self.btn_camera_preview = ttkbs.Button(self.panel1, text="预览", style="Normal.TButton", bootstyle="success",
                                               width=10)
        self.btn_camera_preview.grid(row=1, column=0, **grid_padding)
        self.bt_choose_img = ttkbs.Button(self.panel1, text="选择图片", style="Normal.TButton", bootstyle="success",
                                          width=10)
        self.bt_choose_img.grid(row=1, column=1, **grid_padding)
        self.bt_last_src_image = ttkbs.Button(self.panel1, text="上张照片", style="Normal.TButton", bootstyle="success",
                                              width=10)
        self.bt_last_src_image.grid(row=1, column=2, **grid_padding)

        # 2. panel2（阈值调节面板）
        self.panel2 = ttkbs.LabelFrame(self, text="阈值调节", style="Bold.TLabel", bootstyle="info", padding=10)
        self.panel2.pack(side=tk.BOTTOM, fill=tk.X, **panel_padding)

        # - 自适应窗口大小阈值（移除font参数）
        self.label6 = ttkbs.Label(self.panel2, text="自适应窗口大小：", style="Normal.TLabel")
        self.label6.grid(row=0, column=0, sticky=tk.W, **grid_padding)
        self.trackb_th_blksize = ttkbs.Scale(self.panel2, from_=1, to=255, orient=tk.HORIZONTAL, length=200,
                                             bootstyle="primary")
        self.trackb_th_blksize.grid(row=0, column=1, sticky=tk.W, **grid_padding)
        self.tb_th_blksize = ttkbs.Entry(self.panel2, style="Normal.TEntry", width=10, bootstyle="secondary")
        self.tb_th_blksize.grid(row=0, column=2, sticky=tk.W, **grid_padding)
        self.l_th_blk_minval = ttkbs.Label(self.panel2, text="1", style="Small.TLabel", bootstyle="muted")
        self.l_th_blk_minval.grid(row=0, column=3, sticky=tk.W, padx=2, pady=6)
        self.l_th_blk_maxval = ttkbs.Label(self.panel2, text="255", style="Small.TLabel", bootstyle="muted")
        self.l_th_blk_maxval.grid(row=0, column=4, sticky=tk.W, padx=2, pady=6)
        self.bt_apply_blksize = ttkbs.Button(self.panel2, text="应用", style="Normal.TButton",
                                             bootstyle="outline-primary", width=8)
        self.bt_apply_blksize.grid(row=0, column=5, **grid_padding)

        # - 全局颜色阈值（移除font参数）
        self.label8 = ttkbs.Label(self.panel2, text="全局阈值：", style="Normal.TLabel")
        self.label8.grid(row=1, column=0, sticky=tk.W, **grid_padding)
        self.trackb_th_color = ttkbs.Scale(self.panel2, from_=0, to=255, orient=tk.HORIZONTAL, length=200,
                                           bootstyle="primary")
        self.trackb_th_color.grid(row=1, column=1, sticky=tk.W, **grid_padding)
        self.tb_th_color = ttkbs.Entry(self.panel2, style="Normal.TEntry", width=10, bootstyle="secondary")
        self.tb_th_color.grid(row=1, column=2, sticky=tk.W, **grid_padding)
        self.l_th_color_minval = ttkbs.Label(self.panel2, text="0", style="Small.TLabel", bootstyle="muted")
        self.l_th_color_minval.grid(row=1, column=3, sticky=tk.W, padx=2, pady=6)
        self.l_th_color_maxval = ttkbs.Label(self.panel2, text="255", style="Small.TLabel", bootstyle="muted")
        self.l_th_color_maxval.grid(row=1, column=4, sticky=tk.W, padx=2, pady=6)

        # - 自适应偏移阈值（移除font参数）
        self.label7 = ttkbs.Label(self.panel2, text="自适应偏移：", style="Normal.TLabel")
        self.label7.grid(row=2, column=0, sticky=tk.W, **grid_padding)
        self.trackb_th_off = ttkbs.Scale(self.panel2, from_=0, to=100, orient=tk.HORIZONTAL, length=200,
                                         bootstyle="primary")
        self.trackb_th_off.grid(row=2, column=1, sticky=tk.W, **grid_padding)
        self.tb_th_off = ttkbs.Entry(self.panel2, style="Normal.TEntry", width=10, bootstyle="secondary")
        self.tb_th_off.grid(row=2, column=2, sticky=tk.W, **grid_padding)
        self.l_th_off_minval = ttkbs.Label(self.panel2, text="0", style="Small.TLabel", bootstyle="muted")
        self.l_th_off_minval.grid(row=2, column=3, sticky=tk.W, padx=2, pady=6)
        self.l_th_off_maxval = ttkbs.Label(self.panel2, text="100", style="Small.TLabel", bootstyle="muted")
        self.l_th_off_maxval.grid(row=2, column=4, sticky=tk.W, padx=2, pady=6)

        # - 小图模式复选框（移除font参数）
        self.use_bm_sml = ttkbs.Checkbutton(self.panel2, text="使用小图模式", style="Normal.TCheckbutton",
                                            bootstyle="round-toggle")
        self.use_bm_sml.grid(row=2, column=5, sticky=tk.W, **grid_padding)

        # 3. panel3（路径操作面板）
        self.panel3 = ttkbs.LabelFrame(self, text="路径操作", style="Bold.TLabel", bootstyle="info", padding=10)
        self.panel3.pack(side=tk.BOTTOM, fill=tk.X, **panel_padding)

        # - 路径按钮组（移除font参数）
        self.bt_gen_path = ttkbs.Button(self.panel3, text="生成路径", style="Normal.TButton", bootstyle="warning",
                                        width=12)
        self.bt_gen_path.grid(row=0, column=0, **grid_padding)
        self.bt_path_doall = ttkbs.Button(self.panel3, text="执行所有路径", style="Normal.TButton", bootstyle="warning",
                                          width=12)
        self.bt_path_doall.grid(row=0, column=1, **grid_padding)
        self.bt_send_path = ttkbs.Button(self.panel3, text="发送路径", style="Normal.TButton", bootstyle="warning",
                                         width=12)
        self.bt_send_path.grid(row=0, column=2, **grid_padding)
        self.cb_face_detect = ttkbs.Checkbutton(self.panel3, text="面部抽取", style="Normal.TCheckbutton",
                                                bootstyle="round-toggle")
        self.cb_face_detect.grid(row=0, column=3, sticky=tk.W, **grid_padding)

        # 4. panel4（模式选择面板）
        self.panel4 = ttkbs.LabelFrame(self, text="模式选择", style="Bold.TLabel", bootstyle="info", padding=10)
        self.panel4.pack(side=tk.BOTTOM, fill=tk.X, **panel_padding)

        # - 单选框+按钮（移除font参数）
        self.mode_var = tk.IntVar(value=0)
        self.nomal_mode = ttkbs.Radiobutton(self.panel4, text="普通模式", style="Normal.TRadiobutton",
                                            variable=self.mode_var, value=0, bootstyle="primary")
        self.nomal_mode.grid(row=0, column=0, sticky=tk.W, **grid_padding)
        self.reinforce_mode = ttkbs.Radiobutton(self.panel4, text="强化模式", style="Normal.TRadiobutton",
                                                variable=self.mode_var, value=1, bootstyle="primary")
        self.reinforce_mode.grid(row=0, column=1, sticky=tk.W, **grid_padding)
        self.smileface = ttkbs.Button(self.panel4, text="笑脸处理", style="Normal.TButton", bootstyle="danger",
                                      width=12)
        self.smileface.grid(row=0, column=2, **grid_padding)

        # 5. panel5（姿态控制面板）
        self.panel5 = ttkbs.LabelFrame(self, text="姿态控制", style="Bold.TLabel", bootstyle="info", padding=10)
        self.panel5.pack(side=tk.BOTTOM, fill=tk.X, **panel_padding)

        # - 姿态按钮（移除font参数）
        self.label10 = ttkbs.Label(self.panel5, text="姿态：", style="Normal.TLabel")
        self.label10.grid(row=0, column=0, sticky=tk.W, **grid_padding)
        self.StartPose = ttkbs.Button(self.panel5, text="开始姿态", style="Normal.TButton", bootstyle="success",
                                      width=12)
        self.StartPose.grid(row=0, column=1, **grid_padding)
        self.EndPose = ttkbs.Button(self.panel5, text="结束姿态", style="Normal.TButton", bootstyle="danger", width=12)
        self.EndPose.grid(row=0, column=2, **grid_padding)

        # ====================== TrackBar和输入框联动逻辑（保持不变） ======================
        def sync_blksize(event):
            val = self.trackb_th_blksize.get()
            if val % 2 == 0:
                val += 1
                self.trackb_th_blksize.set(val)
            self.tb_th_blksize.delete(0, tk.END)
            self.tb_th_blksize.insert(0, str(val))

        def sync_blksize_input(event):
            try:
                val = int(self.tb_th_blksize.get())
                if val < 1: val = 1
                if val > 255: val = 255
                if val % 2 == 0: val += 1
                self.trackb_th_blksize.set(val)
            except ValueError:
                messagebox.showwarning("错误", "自适应窗口大小输入错误！")
                self.tb_th_blksize.delete(0, tk.END)
                self.tb_th_blksize.insert(0, str(self.trackb_th_blksize.get()))

        self.trackb_th_blksize.bind("<Motion>", sync_blksize)
        self.tb_th_blksize.bind("<FocusOut>", sync_blksize_input)
        self.bt_apply_blksize.config(command=sync_blksize_input)

        def sync_color(event):
            val = self.trackb_th_color.get()
            self.tb_th_color.delete(0, tk.END)
            self.tb_th_color.insert(0, str(val))

        def sync_color_input(event):
            try:
                val = int(self.tb_th_color.get())
                if val < 0: val = 0
                if val > 255: val = 255
                self.trackb_th_color.set(val)
            except ValueError:
                messagebox.showwarning("错误", "全局阈值输入错误！")
                self.tb_th_color.delete(0, tk.END)
                self.tb_th_color.insert(0, str(self.trackb_th_color.get()))

        self.trackb_th_color.bind("<Motion>", sync_color)
        self.tb_th_color.bind("<FocusOut>", sync_color_input)

        def sync_off(event):
            val = self.trackb_th_off.get()
            self.tb_th_off.delete(0, tk.END)
            self.tb_th_off.insert(0, str(val))

        def sync_off_input(event):
            try:
                val = int(self.tb_th_off.get())
                if val < 0: val = 0
                if val > 100: val = 100
                self.trackb_th_off.set(val)
            except ValueError:
                messagebox.showwarning("错误", "自适应偏移输入错误！")
                self.tb_th_off.delete(0, tk.END)
                self.tb_th_off.insert(0, str(self.trackb_th_off.get()))

        self.trackb_th_off.bind("<Motion>", sync_off)
        self.tb_th_off.bind("<FocusOut>", sync_off_input)

        # ====================== 初始化控件默认值 ======================
        self.trackb_th_blksize.set(15)
        self.trackb_th_color.set(127)
        self.trackb_th_off.set(50)
        sync_blksize(None)
        sync_color(None)
        sync_off(None)
        self.mode_var.set(0)

    def bind_events(self):
        """绑定所有按钮的点击事件"""
        self.bt_show_img_d.config(command=self.on_show_img_d)
        self.btn_camera_preview.config(command=self.on_camera_preview)
        self.bt_choose_img.config(command=self.on_choose_img)
        self.bt_last_src_image.config(command=self.on_last_src_image)
        self.bt_gen_path.config(command=self.on_gen_path)
        self.bt_path_doall.config(command=self.on_path_doall)
        self.bt_send_path.config(command=self.on_send_path)
        self.smileface.config(command=self.on_smileface)
        self.StartPose.config(command=self.on_start_pose)
        self.EndPose.config(command=self.on_end_pose)

    # -------------------- 事件回调函数 --------------------
    def on_show_img_d(self):
        messagebox.showinfo("提示", "显示调试图功能已触发！")

    def on_camera_preview(self):
        messagebox.showinfo("提示", "相机预览功能已触发！")

    def on_choose_img(self):
        messagebox.showinfo("提示", "选择图片功能已触发！")

    def on_last_src_image(self):
        messagebox.showinfo("提示", "切换上张照片功能已触发！")

    def on_gen_path(self):
        messagebox.showinfo("提示", "生成路径功能已触发！")

    def on_path_doall(self):
        messagebox.showinfo("提示", "执行所有路径功能已触发！")

    def on_send_path(self):
        messagebox.showinfo("提示", "发送路径功能已触发！")

    def on_smileface(self):
        messagebox.showinfo("提示", "笑脸处理功能已触发！")

    def on_start_pose(self):
        messagebox.showinfo("提示", "开始姿态控制功能已触发！")

    def on_end_pose(self):
        messagebox.showinfo("提示", "结束姿态控制功能已触发！")


# 运行界面
if __name__ == "__main__":
    app = Form1()
    app.mainloop()