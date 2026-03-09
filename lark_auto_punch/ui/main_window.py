"""
主窗口
"""
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..config import APP_NAME, IMAGES_DIR
from .tab_auto_punch import TabAutoPunch
from .tab_recorder import TabRecorder
from .tab_scheduled_click import TabScheduledClick
from .tab_settings import TabSettings


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.images_dir = IMAGES_DIR
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1000, 650)

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建 Tab 控件
        tab_widget = QTabWidget()

        # Tab 1: 自动打卡
        self.auto_punch_tab = TabAutoPunch(self.images_dir)
        tab_widget.addTab(self.auto_punch_tab, "🎯 自动打卡")

        # Tab 2: 键鼠录制
        self.recorder_tab = TabRecorder()
        tab_widget.addTab(self.recorder_tab, "🎬 键鼠录制")

        # Tab 3: 定时点击
        self.scheduled_click_tab = TabScheduledClick()
        tab_widget.addTab(self.scheduled_click_tab, "⏰ 定时点击")

        # Tab 4: 高级设置
        self.settings_tab = TabSettings()
        tab_widget.addTab(self.settings_tab, "⚙️ 高级设置")

        main_layout.addWidget(tab_widget)

    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有正在运行的任务
        if hasattr(self.auto_punch_tab, 'timer') and self.auto_punch_tab.timer.isActive():
            self.auto_punch_tab.stop_task()

        if hasattr(self.scheduled_click_tab, 'scheduler') and self.scheduled_click_tab.scheduler:
            self.scheduled_click_tab.scheduler.stop()
            self.scheduled_click_tab.scheduler.wait()

        event.accept()
