"""
Tab 4: 高级设置页面
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLabel, QSpinBox, QLineEdit, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

from ..utils.settings import SettingsManager


class TabSettings(QWidget):
    """高级设置 Tab"""

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 左侧：设置项
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)

        # 标题
        title = QLabel("⚙️ 高级设置")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        left_layout.addWidget(title)

        # 图像识别设置
        left_layout.addWidget(self.create_recognition_group())

        # 执行延迟设置
        left_layout.addWidget(self.create_delay_group())

        # 其他设置
        left_layout.addWidget(self.create_other_group())

        left_layout.addStretch()
        main_layout.addWidget(left_widget, 1)

        # 右侧：说明和操作
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # 说明
        info_group = QGroupBox("说明")
        info_layout = QVBoxLayout()
        info = QLabel("💡 配置图像识别参数、执行延迟和其他选项\n\n"
                     "• 相似度阈值：控制图像匹配的精确度，推荐 0.8\n"
                     "• 重试次数：识别失败时的重试次数\n"
                     "• 步骤间延迟：每个步骤完成后的等待时间")
        info.setWordWrap(True)
        info_layout.addWidget(info)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        # 保存按钮
        save_btn = QPushButton("💾 保存设置")
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.save_settings)
        right_layout.addWidget(save_btn)

        right_layout.addStretch()
        main_layout.addWidget(right_widget, 1)

        self.setLayout(main_layout)

        # 加载设置
        self.load_settings()

    def create_recognition_group(self):
        """图像识别设置组"""
        group = QGroupBox("🔍 图像识别")

        layout = QVBoxLayout()

        # 相似度阈值
        conf_layout = QHBoxLayout()
        conf_label = QLabel("相似度阈值:")
        conf_label.setMinimumWidth(100)
        conf_layout.addWidget(conf_label)

        self.confidence_input = QLineEdit()
        self.confidence_input.setText("0.8")
        self.confidence_input.setValidator(QDoubleValidator(0.0, 1.0, 2))
        conf_layout.addWidget(self.confidence_input)

        tip = QLabel("(0.0-1.0，推荐 0.8)")
        tip.setStyleSheet("color: #666;")
        conf_layout.addWidget(tip)
        conf_layout.addStretch()
        layout.addLayout(conf_layout)

        # 重试次数
        retry_layout = QHBoxLayout()
        retry_label = QLabel("重试次数:")
        retry_label.setMinimumWidth(100)
        retry_layout.addWidget(retry_label)

        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 10)
        self.retry_spin.setValue(3)
        self.retry_spin.setSuffix(" 次")
        retry_layout.addWidget(self.retry_spin)
        retry_layout.addStretch()
        layout.addLayout(retry_layout)

        group.setLayout(layout)
        return group

    def create_delay_group(self):
        """执行延迟设置组"""
        group = QGroupBox("⏱️ 执行延迟")

        layout = QVBoxLayout()

        # 步骤间延迟
        delay_layout = QHBoxLayout()
        delay_label = QLabel("步骤间延迟:")
        delay_label.setMinimumWidth(100)
        delay_layout.addWidget(delay_label)

        self.step_delay_spin = QSpinBox()
        self.step_delay_spin.setRange(1, 10)
        self.step_delay_spin.setValue(2)
        self.step_delay_spin.setSuffix(" 秒")
        delay_layout.addWidget(self.step_delay_spin)

        tip = QLabel("(每个步骤完成后的等待时间)")
        tip.setStyleSheet("color: #666;")
        delay_layout.addWidget(tip)
        delay_layout.addStretch()
        layout.addLayout(delay_layout)

        group.setLayout(layout)
        return group

    def create_other_group(self):
        """其他设置组"""
        group = QGroupBox("🔧 其他设置")

        layout = QVBoxLayout()

        # 启动时最小化
        self.minimize_checkbox = QCheckBox("启动任务后最小化窗口")
        layout.addWidget(self.minimize_checkbox)

        # 失败时通知
        self.notify_checkbox = QCheckBox("任务失败时系统通知")
        self.notify_checkbox.setChecked(True)
        layout.addWidget(self.notify_checkbox)

        group.setLayout(layout)
        return group

    def save_settings(self):
        """保存设置"""
        settings = {
            "confidence": self.confidence_input.text(),
            "retry": self.retry_spin.value(),
            "step_delay": self.step_delay_spin.value(),
            "minimize": self.minimize_checkbox.isChecked(),
            "notify": self.notify_checkbox.isChecked()
        }
        self.settings_manager.save_all(settings)
        QMessageBox.information(self, "保存成功", "设置已保存！")

    def load_settings(self):
        """加载设置"""
        settings = self.settings_manager.load_all()
        self.confidence_input.setText(str(settings["confidence"]))
        self.retry_spin.setValue(settings["retry"])
        self.step_delay_spin.setValue(settings["step_delay"])
        self.minimize_checkbox.setChecked(settings["minimize"])
        self.notify_checkbox.setChecked(settings["notify"])
