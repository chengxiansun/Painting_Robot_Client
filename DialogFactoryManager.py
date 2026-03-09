import tkinter as tk
from tkinter import ttk, filedialog
import BinaryAdjustDialog
import PortraitAdjustDialog
import BackgroundAdjustDialog


class DialogFactoryManager:
    """对话框工厂管理器：统一管理不同类型的对话框工厂"""

    @staticmethod
    def get_factory(dialog_type):
        """根据类型获取对应的工厂"""
        factories = {
            "binary": BinaryAdjustDialog.BinaryDialogFactory(),
            "portrait": PortraitAdjustDialog.PortraitAdjustDialogFactory(),
            "background": BackgroundAdjustDialog.BackgroundAdjustDialogFactory()
        }
        return factories.get(dialog_type, None)
