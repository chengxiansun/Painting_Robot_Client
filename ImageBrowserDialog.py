import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


class ImageBrowserDialog(tk.Toplevel):
    def __init__(self, parent, image_dir=r"database", on_image_selected=None):
        super().__init__(parent)
        self.title("背景选择浏览器")
        self.geometry("800x600")
        self.resizable(True, True)

        # 初始化变量
        self.image_dir = os.path.abspath(image_dir)  # 固定图片文件夹路径
        self.image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        self.image_files = []  # 存储图片文件列表
        self.photo_images = []  # 保存PhotoImage引用，防止被GC回收
        self.selected_image = None  # 选中的图片路径

        # 核心：接收回调函数（用于将图片绑定到主程序属性）
        self.on_image_selected = on_image_selected

        # 创建UI
        self._create_widgets()
        # 加载图片列表
        self._load_images()

    def _create_widgets(self):
        # ========== 顶部按钮区域（仅保留添加、刷新、路径显示） ==========
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # 添加图片按钮
        self.add_btn = ttk.Button(
            top_frame,
            text="添加新图片",
            command=self._add_new_image
        )
        self.add_btn.pack(side=tk.LEFT)

        # 刷新按钮
        self.refresh_btn = ttk.Button(
            top_frame,
            text="刷新列表",
            command=self._load_images
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=10)

        # 显示文件夹路径
        path_label = ttk.Label(
            top_frame,
            text=f"当前目录: {self.image_dir}"
        )
        path_label.pack(side=tk.LEFT, padx=10)

        # 选中状态提示（移到顶部右侧）
        self.select_label = ttk.Label(
            top_frame,
            text="未选中任何图片",
            foreground="red"
        )
        self.select_label.pack(side=tk.RIGHT, padx=10)

        # ========== 中间图片展示区域（无变化） ==========
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 水平滚动条（可选）
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 画布用于展示图片
        self.canvas = tk.Canvas(
            main_frame,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            bg="#f0f0f0"
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 绑定滚动条
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)

        # 内部框架（用于放置所有图片）
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor=tk.NW
        )

        # 绑定大小变化事件
        self.inner_frame.bind("<Configure>", self._on_inner_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # ========== 底部区域（新增）- 放置确定按钮 ==========
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        # 确定按钮（初始禁用，放在底部居中）
        self.confirm_btn = ttk.Button(
            bottom_frame,
            text="确定",
            command=self._confirm_selection,
            state=tk.DISABLED,  # 初始禁用
            width=15  # 设置按钮宽度，更美观
        )
        self.confirm_btn.pack(side=tk.BOTTOM, pady=5)  # 居中显示

    def _on_inner_frame_configure(self, event):
        """更新画布滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """调整内部框架宽度以匹配画布"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _load_images(self):
        """加载指定文件夹下的所有图片"""
        # 清空原有内容
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.image_files.clear()
        self.photo_images.clear()
        self.selected_image = None  # 重置选中状态
        self.select_label.config(text="未选中任何图片", foreground="red")
        self.confirm_btn.config(state=tk.DISABLED)  # 重置按钮状态

        # 检查目录是否存在
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)  # 不存在则创建
            messagebox.showinfo("提示", f"目录不存在，已创建: {self.image_dir}")
            return

        # 获取所有图片文件
        try:
            all_files = os.listdir(self.image_dir)
            self.image_files = [
                f for f in all_files
                if f.lower().endswith(self.image_extensions)
            ]

            if not self.image_files:
                # 显示空提示
                empty_label = ttk.Label(
                    self.inner_frame,
                    text="当前目录暂无图片文件",
                    font=("Arial", 12)
                )
                empty_label.pack(pady=50)
                return

            # 展示图片（每行显示3张）
            row, col = 0, 0
            max_cols = 3
            thumbnail_size = (200, 200)  # 缩略图尺寸

            for idx, img_file in enumerate(self.image_files):
                # 拼接完整路径
                img_path = os.path.join(self.image_dir, img_file)

                try:
                    # 加载并调整图片大小
                    img = Image.open(img_path)
                    img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    # 保存引用防止被回收
                    self.photo_images.append(photo)

                    # 创建图片容器（用于选中高亮）
                    img_container = ttk.Frame(self.inner_frame, relief=tk.FLAT, borderwidth=2)
                    img_container.grid(row=row, column=col, padx=10, pady=10)

                    # 绑定点击事件
                    img_container.bind("<Button-1>",
                                       lambda e, path=img_path, container=img_container: self._select_image(path,
                                                                                                            container))

                    # 创建图片标签和文件名标签
                    img_label = ttk.Label(img_container, image=photo)
                    img_label.pack()
                    img_label.bind("<Button-1>",
                                   lambda e, path=img_path, container=img_container: self._select_image(path,
                                                                                                        container))

                    name_label = ttk.Label(
                        img_container,
                        text=img_file,
                        wraplength=180,
                        justify=tk.CENTER
                    )
                    name_label.pack(pady=5)
                    name_label.bind("<Button-1>",
                                    lambda e, path=img_path, container=img_container: self._select_image(path,
                                                                                                         container))

                    # 更新行列
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

                except Exception as e:
                    messagebox.warning("警告", f"加载图片 {img_file} 失败: {str(e)}")

        except Exception as e:
            messagebox.showerror("错误", f"读取目录失败: {str(e)}")

    def _select_image(self, img_path, container):
        """选中图片，高亮显示并激活确定按钮"""
        # 取消所有图片的选中状态
        for child in self.inner_frame.winfo_children():
            if isinstance(child, ttk.Frame):
                child.config(relief=tk.FLAT, borderwidth=2)

        # 设置当前图片为选中状态
        container.config(relief=tk.SOLID, borderwidth=2)
        self.selected_image = Image.open(img_path)

        # 更新提示信息
        file_name = os.path.basename(img_path)
        self.select_label.config(text=f"已选中: {file_name}", foreground="green")

        # 激活确定按钮
        self.confirm_btn.config(state=tk.NORMAL)

    def _add_new_image(self):
        """添加新图片到指定文件夹"""
        # 选择要添加的图片
        file_paths = filedialog.askopenfilenames(
            title="选择要添加的图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"), ("所有文件", "*.*")]
        )

        if not file_paths:
            return

        success_count = 0
        for file_path in file_paths:
            try:
                # 获取文件名
                file_name = os.path.basename(file_path)
                # 目标路径
                dest_path = os.path.join(self.image_dir, file_name)

                # 检查是否已存在
                if os.path.exists(dest_path):
                    # 询问是否覆盖
                    if not messagebox.askyesno("提示", f"文件 {file_name} 已存在，是否覆盖？"):
                        continue

                # 复制文件（避免移动原文件）
                with open(file_path, 'rb') as src_file, open(dest_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
                success_count += 1

            except Exception as e:
                messagebox.warning("警告", f"添加图片 {file_path} 失败: {str(e)}")

        if success_count > 0:
            messagebox.showinfo("成功", f"成功添加 {success_count} 张图片")
            # 刷新图片列表
            self._load_images()

    def _confirm_selection(self):
        """确认选择，加载OpenCV格式图片并通过回调绑定到主程序"""
        if self.selected_image is None:
            messagebox.warning("警告", "请先选择一张图片！")
            return

        try:

            # 核心：调用回调函数，将图片传递到主程序并绑定
            if self.selected_image:
                self.on_image_selected(self.selected_image)

            # 关闭对话框
            self.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"处理图片失败: {str(e)}")


# 测试代码
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 指定图片文件夹路径（修改为你的实际路径）
    IMAGE_DIR = r"database"

    # 创建并显示图片浏览器对话框
    dialog = ImageBrowserDialog(root, IMAGE_DIR)
    dialog.grab_set()  # 模态对话框
    root.mainloop()

    # 获取选中的OpenCV图片
    selected_img = dialog.get_selected_image()
    if selected_img is not None:
        print(f"选中图片的尺寸: {selected_img.shape}")
        # 可以在这里添加显示/处理图片的逻辑
        cv2.imshow("Selected Image", selected_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("未选中任何图片")
