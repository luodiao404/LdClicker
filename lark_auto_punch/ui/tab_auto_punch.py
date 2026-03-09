"""
Tab 1: 自动打卡页面
包含图片配置、时间设置、任务控制和日志
"""
import random
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLabel, QTimeEdit, QSpinBox, QTextEdit, QMessageBox, QScrollArea,
    QFileDialog, QFrame, QLineEdit, QCheckBox
)
from PyQt5.QtCore import QTime, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QDoubleValidator

from ..config import (
    IMAGE_NAMES, IMAGES_DIR, LOG_COLORS,
    DEFAULT_CHECKIN_TIME, DEFAULT_CHECKOUT_TIME, DEFAULT_JITTER_MINUTES
)
from ..core.automation import AutomationWorker
from ..utils.config_manager import ConfigManager
from ..utils.settings import SettingsManager


class TabAutoPunch(QWidget):
    """自动打卡 Tab"""

    def __init__(self, images_dir):
        super().__init__()
        self.images_dir = Path(images_dir)
        self.images_dir.mkdir(exist_ok=True)

        self.current_image = None
        self.image_names = IMAGE_NAMES
        self.status_labels = {}
        self.preview_labels = {}
        self.settings_manager = SettingsManager()

        self.worker = None
        self.scheduled_times = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedule)

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 左侧：图片配置
        left_widget = self.create_left_panel()
        main_layout.addWidget(left_widget, 1)

        # 右侧：任务控制和日志
        right_widget = self.create_right_panel()
        main_layout.addWidget(right_widget, 2)

        self.setLayout(main_layout)

        # 加载已有图片
        self.load_existing_images()

        # 初始日志
        self.append_log("🚀 自动打卡模块已加载", "INFO")
        self.append_log("💡 提示: 请先配置所有图片，然后设置打卡时间", "INFO")

    def create_left_panel(self):
        """创建左侧面板"""
        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel("📷 图像配置")
        title_label
        layout.addWidget(title_label)

        # 工具栏
        toolbar_layout = QHBoxLayout()
        export_btn = QPushButton("📤 导出")
        export_btn.clicked.connect(self.export_config)

        import_btn = QPushButton("📥 导入")
        import_btn.clicked.connect(self.import_config)

        toolbar_layout.addWidget(export_btn)
        toolbar_layout.addWidget(import_btn)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # 上传按钮
        upload_btn = QPushButton("📁 选择图片")
        upload_btn.setMinimumHeight(40)
        upload_btn.clicked.connect(self.upload_image)
        layout.addWidget(upload_btn)

        # 预览
        self.preview_label = QLabel("未选择图片")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(120)
        self.preview_label
        layout.addWidget(self.preview_label)

        # 图片列表
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)

        for name in self.image_names:
            item = self.create_image_item(name)
            scroll_layout.addWidget(item)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        return widget

    def create_right_panel(self):
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # 时间配置
        layout.addWidget(self.create_time_config())

        # 控制按钮
        layout.addWidget(self.create_control_panel())

        # 日志
        layout.addWidget(self.create_log_panel(), 1)

        return widget

    def create_time_config(self):
        """创建时间配置组"""
        group = QGroupBox("⏰ 时间配置")

        layout = QVBoxLayout()

        # 启用选项
        enable_layout = QHBoxLayout()
        enable_label = QLabel("启用打卡:")
        enable_label.setMinimumWidth(80)
        enable_layout.addWidget(enable_label)

        self.enable_checkin_checkbox = QCheckBox("上班打卡")
        self.enable_checkin_checkbox.setChecked(True)
        enable_layout.addWidget(self.enable_checkin_checkbox)

        self.enable_checkout_checkbox = QCheckBox("下班打卡")
        self.enable_checkout_checkbox.setChecked(True)
        enable_layout.addWidget(self.enable_checkout_checkbox)

        enable_layout.addStretch()
        layout.addLayout(enable_layout)

        # 上班时间
        checkin_layout = QHBoxLayout()
        checkin_label = QLabel("上班时间:")
        checkin_label.setMinimumWidth(80)
        checkin_layout.addWidget(checkin_label)

        self.checkin_time_edit = QTimeEdit()
        self.checkin_time_edit.setDisplayFormat("HH:mm")
        self.checkin_time_edit.setTime(QTime.fromString(DEFAULT_CHECKIN_TIME, "HH:mm"))
        checkin_layout.addWidget(self.checkin_time_edit)
        checkin_layout.addStretch()
        layout.addLayout(checkin_layout)

        # 下班时间
        checkout_layout = QHBoxLayout()
        checkout_label = QLabel("下班时间:")
        checkout_label.setMinimumWidth(80)
        checkout_layout.addWidget(checkout_label)

        self.checkout_time_edit = QTimeEdit()
        self.checkout_time_edit.setDisplayFormat("HH:mm")
        self.checkout_time_edit.setTime(QTime.fromString(DEFAULT_CHECKOUT_TIME, "HH:mm"))
        checkout_layout.addWidget(self.checkout_time_edit)
        checkout_layout.addStretch()
        layout.addLayout(checkout_layout)

        # 时间偏差
        jitter_layout = QHBoxLayout()
        jitter_label = QLabel("时间偏差:")
        jitter_label.setMinimumWidth(80)
        jitter_layout.addWidget(jitter_label)

        self.jitter_spin = QSpinBox()
        self.jitter_spin.setRange(0, 30)
        self.jitter_spin.setValue(DEFAULT_JITTER_MINUTES)
        self.jitter_spin.setSuffix(" 分钟")
        jitter_layout.addWidget(self.jitter_spin)
        jitter_layout.addStretch()
        layout.addLayout(jitter_layout)

        # 提示信息
        info = QLabel("💡 勾选需要执行的打卡类型，启动后将自动执行")
        info.setWordWrap(True)
        layout.addWidget(info)

        group.setLayout(layout)
        return group

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox()
        group
        group

        layout = QVBoxLayout()

        title = QLabel("🎮 任务控制")
        title
        layout.addWidget(title)

        # 主控制按钮
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ 启动任务")
        self.start_btn.setMinimumHeight(55)
        self.start_btn
        self.start_btn.clicked.connect(self.start_task)

        self.stop_btn = QPushButton("⏹ 停止任务")
        self.stop_btn.setMinimumHeight(55)
        self.stop_btn
        self.stop_btn.clicked.connect(self.stop_task)
        self.stop_btn.setEnabled(False)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        # 测试按钮
        test_layout = QHBoxLayout()

        self.test_checkin_btn = QPushButton("⚡ 测试上班")
        self.test_checkin_btn.setMinimumHeight(45)
        self.test_checkin_btn
        self.test_checkin_btn.clicked.connect(lambda: self.execute_now("上班"))

        self.test_checkout_btn = QPushButton("⚡ 测试下班")
        self.test_checkout_btn.setMinimumHeight(45)
        self.test_checkout_btn
        self.test_checkout_btn.clicked.connect(lambda: self.execute_now("下班"))

        test_layout.addWidget(self.test_checkin_btn)
        test_layout.addWidget(self.test_checkout_btn)
        layout.addLayout(test_layout)

        group.setLayout(layout)
        return group

    def create_log_panel(self):
        """创建日志面板"""
        group = QGroupBox()
        group
        group

        layout = QVBoxLayout()

        header = QHBoxLayout()
        title = QLabel("📋 运行日志")
        title
        header.addWidget(title)

        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setFixedWidth(90)
        clear_btn
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        header.addWidget(clear_btn)
        layout.addLayout(header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text
        layout.addWidget(self.log_text)

        group.setLayout(layout)
        return group

    def create_image_item(self, name):
        """创建图片配置项"""
        frame = QFrame()
        frame

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)

        # 缩略图
        preview = QLabel()
        preview.setAlignment(Qt.AlignCenter)
        preview.setFixedSize(70, 70)
        preview
        self.preview_labels[name] = preview
        layout.addWidget(preview)

        # 信息
        info_layout = QVBoxLayout()
        name_label = QLabel(f"🏷️ {name}")
        name_label
        info_layout.addWidget(name_label)

        status_label = QLabel("未配置")
        status_label
        self.status_labels[name] = status_label
        info_layout.addWidget(status_label)

        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

        # 保存按钮
        btn = QPushButton("保存")
        btn.setFixedWidth(80)
        btn.setFixedHeight(36)
        btn.clicked.connect(lambda: self.save_as(name))
        btn
        layout.addWidget(btn)

        return frame

    # 图片相关方法（保持不变）
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.current_image = file_path
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(250, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled)

    def save_as(self, name):
        if not self.current_image:
            self.preview_label.setText("请先上传图片！")
            return

        import shutil
        dest = self.images_dir / f"{name}.png"
        try:
            shutil.copy(self.current_image, dest)
            self.update_image_status(name)
            self.append_log(f"✓ 图片 '{name}' 保存成功", "SUCCESS")
        except Exception as e:
            self.append_log(f"✗ 保存失败: {e}", "ERROR")

    def update_image_status(self, name):
        img_path = self.images_dir / f"{name}.png"
        if img_path.exists():
            self.status_labels[name].setText("✓ 已配置")
            pixmap = QPixmap(str(img_path))
            scaled = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_labels[name].setPixmap(scaled)
        else:
            self.status_labels[name].setText("未配置")
            self.preview_labels[name].clear()
            self.preview_labels[name].setText("无")

        # 更新复选框状态
        self.update_checkbox_states()

    def update_checkbox_states(self):
        """根据已上传的图片更新复选框的可用状态"""
        # 检查上班打卡所需的图片（lark, 工作台, 假勤, 上班）
        checkin_images = ["lark", "工作台", "假勤", "上班"]
        checkin_ready = all((self.images_dir / f"{name}.png").exists() for name in checkin_images)

        # 检查下班打卡所需的图片（lark, 工作台, 假勤, 下班）
        checkout_images = ["lark", "工作台", "假勤", "下班"]
        checkout_ready = all((self.images_dir / f"{name}.png").exists() for name in checkout_images)

        # 更新复选框状态
        self.enable_checkin_checkbox.setEnabled(checkin_ready)
        if not checkin_ready:
            self.enable_checkin_checkbox.setChecked(False)
            self.enable_checkin_checkbox.setToolTip("请先上传上班打卡所需的所有图片")
        else:
            self.enable_checkin_checkbox.setToolTip("")

        self.enable_checkout_checkbox.setEnabled(checkout_ready)
        if not checkout_ready:
            self.enable_checkout_checkbox.setChecked(False)
            self.enable_checkout_checkbox.setToolTip("请先上传下班打卡所需的所有图片")
        else:
            self.enable_checkout_checkbox.setToolTip("")

    def load_existing_images(self):
        for name in self.image_names:
            self.update_image_status(name)

    def export_config(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置",
            f"lark_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "配置文件 (*.zip)"
        )
        if file_path:
            success, message = ConfigManager.export_config(self.images_dir, self.image_names, file_path)
            if success:
                QMessageBox.information(self, "导出成功", message)
                self.append_log(f"✓ 配置已导出", "SUCCESS")
            else:
                QMessageBox.warning(self, "导出失败", message)

    def import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入配置", "", "配置文件 (*.zip)")
        if file_path:
            success, message, count = ConfigManager.import_config(file_path, self.images_dir, self.image_names)
            self.load_existing_images()
            if success:
                QMessageBox.information(self, "导入成功", message)
                self.append_log(f"✓ 配置已导入: {count} 张图片", "SUCCESS")
            else:
                QMessageBox.critical(self, "导入失败", message)

    def check_all_configured(self):
        """检查所有需要的图片是否已配置"""
        # 获取当前启用的打卡类型
        enable_checkin = self.enable_checkin_checkbox.isChecked()
        enable_checkout = self.enable_checkout_checkbox.isChecked()

        # 公共图片（lark, 工作台, 假勤）
        common_images = ["lark", "工作台", "假勤"]

        # 根据启用的打卡类型检查对应的图片
        required_images = common_images.copy()

        if enable_checkin:
            required_images.append("上班")

        if enable_checkout:
            required_images.append("下班")

        # 检查所需图片是否都已上传
        for name in required_images:
            if not (self.images_dir / f"{name}.png").exists():
                return False, name

        return True, None

    # 任务控制方法（保持不变，只更新日志输出）
    def start_task(self):
        # 检查是否至少启用了一个打卡类型
        enable_checkin = self.enable_checkin_checkbox.isChecked()
        enable_checkout = self.enable_checkout_checkbox.isChecked()

        if not enable_checkin and not enable_checkout:
            self.append_log("✗ 错误: 请至少启用一种打卡类型", "ERROR")
            QMessageBox.warning(self, "提示", "请至少勾选一种打卡类型（上班打卡或下班打卡）")
            return

        # 检查已启用的打卡类型所需的图片是否已配置
        all_configured, missing = self.check_all_configured()
        if not all_configured:
            self.append_log(f"✗ 错误: 图片 '{missing}' 未配置", "ERROR")
            QMessageBox.warning(self, "提示", f"请先上传图片: {missing}")
            return

        jitter = self.jitter_spin.value()
        now = datetime.now()
        self.scheduled_times = []

        # 只添加启用的打卡任务
        if enable_checkin:
            checkin = self.checkin_time_edit.time()
            checkin_dt = datetime(now.year, now.month, now.day, checkin.hour(), checkin.minute())
            checkin_dt += timedelta(minutes=random.randint(-jitter, jitter))
            if checkin_dt <= now:
                checkin_dt += timedelta(days=1)
            self.scheduled_times.append((checkin_dt, "上班"))

        if enable_checkout:
            checkout = self.checkout_time_edit.time()
            checkout_dt = datetime(now.year, now.month, now.day, checkout.hour(), checkout.minute())
            checkout_dt += timedelta(minutes=random.randint(-jitter, jitter))
            if checkout_dt <= now:
                checkout_dt += timedelta(days=1)
            self.scheduled_times.append((checkout_dt, "下班"))

        self.scheduled_times.sort(key=lambda x: x[0])
        self.timer.start(1000)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.test_checkin_btn.setEnabled(False)
        self.test_checkout_btn.setEnabled(False)

        self.append_log("=" * 60, "START")
        self.append_log("✓ 自动打卡任务已启动", "START")

        # 显示启用的打卡类型
        enabled_types = []
        if enable_checkin:
            enabled_types.append("上班打卡")
        if enable_checkout:
            enabled_types.append("下班打卡")
        self.append_log(f"  • 启用类型: {', '.join(enabled_types)}", "INFO")

        for dt, action in self.scheduled_times:
            remaining = (dt - now).total_seconds()
            self.append_log(f"  • {action}: {dt.strftime('%Y-%m-%d %H:%M:%S')} (剩余 {int(remaining)}秒)", "SCHEDULE")

    def stop_task(self):
        self.timer.stop()
        self.scheduled_times = []

        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.test_checkin_btn.setEnabled(True)
        self.test_checkout_btn.setEnabled(True)

        self.append_log("⏹ 任务已停止", "STOP")

    def check_schedule(self):
        if not self.scheduled_times:
            return

        now = datetime.now()
        for dt, action in self.scheduled_times[:]:
            if (dt - now).total_seconds() <= 0:
                self.scheduled_times.remove((dt, action))
                self.append_log(f"▶ 开始执行{action}打卡...", "START")
                self.execute_automation(action)

                if not self.scheduled_times:
                    self.reschedule_next_day()

    def reschedule_next_day(self):
        jitter = self.jitter_spin.value()
        tomorrow = datetime.now() + timedelta(days=1)
        self.scheduled_times = []

        # 只重新安排启用的打卡任务
        enable_checkin = self.enable_checkin_checkbox.isChecked()
        enable_checkout = self.enable_checkout_checkbox.isChecked()

        if enable_checkin:
            checkin = self.checkin_time_edit.time()
            checkin_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, checkin.hour(), checkin.minute())
            checkin_dt += timedelta(minutes=random.randint(-jitter, jitter))
            self.scheduled_times.append((checkin_dt, "上班"))

        if enable_checkout:
            checkout = self.checkout_time_edit.time()
            checkout_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, checkout.hour(), checkout.minute())
            checkout_dt += timedelta(minutes=random.randint(-jitter, jitter))
            self.scheduled_times.append((checkout_dt, "下班"))

        self.scheduled_times.sort(key=lambda x: x[0])
        self.append_log("📅 明日计划:", "SCHEDULE")
        for dt, action in self.scheduled_times:
            self.append_log(f"  • {action}: {dt.strftime('%Y-%m-%d %H:%M:%S')}", "SCHEDULE")

    def execute_now(self, action):
        all_configured, missing = self.check_all_configured()
        if not all_configured:
            self.append_log(f"✗ 错误: 图片 '{missing}' 未配置", "ERROR")
            return

        self.append_log(f"⚡ 立即执行{action}打卡（测试模式）", "START")
        self.execute_automation(action)

    def execute_automation(self, action):
        settings = self.settings_manager.load_all()

        self.worker = AutomationWorker(
            self.images_dir, action,
            confidence=settings["confidence"],
            retry=settings["retry"],
            step_delay=settings["step_delay"]
        )

        self.worker.log_signal.connect(self.append_log)
        self.worker.task_finished.connect(lambda success: self.on_task_finished(success, settings["notify"]))

        self.test_checkin_btn.setEnabled(False)
        self.test_checkout_btn.setEnabled(False)

        if settings["minimize"] and self.timer.isActive():
            self.window().showMinimized()

        self.worker.start()

    def on_task_finished(self, success, notify):
        if not self.timer.isActive():
            self.start_btn.setEnabled(True)
            self.test_checkin_btn.setEnabled(True)
            self.test_checkout_btn.setEnabled(True)

        if success:
            self.append_log("✓ 任务执行成功！", "SUCCESS")
            if notify:
                QMessageBox.information(self.window(), "打卡成功", "自动打卡任务执行成功！")
        else:
            self.append_log("✗ 任务执行失败", "FAIL")
            if notify:
                QMessageBox.warning(self.window(), "打卡失败", "自动打卡任务执行失败！")

    def append_log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = LOG_COLORS.get(level, "#CFD8DC")
        formatted = f'<span style="color: #90A4AE;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{level}]</span> <span style="color: #CFD8DC;">{message}</span>'
        self.log_text.append(formatted)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

