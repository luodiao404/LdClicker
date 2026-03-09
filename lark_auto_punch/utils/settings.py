"""
设置管理工具
负责保存和加载应用设置
"""
from PyQt5.QtCore import QSettings

from ..config import (
    APP_ORG, DEFAULT_CONFIDENCE, DEFAULT_RETRY,
    DEFAULT_STEP_DELAY
)


class SettingsManager:
    """设置管理器"""

    def __init__(self):
        self.settings = QSettings(APP_ORG, "Settings")

    def save(self, key, value):
        """保存单个设置"""
        self.settings.setValue(key, value)

    def load(self, key, default=None):
        """加载单个设置"""
        return self.settings.value(key, default)

    def save_all(self, settings_dict):
        """保存所有设置"""
        for key, value in settings_dict.items():
            self.settings.setValue(key, value)

    def load_all(self):
        """加载所有设置"""
        return {
            "confidence": float(self.settings.value("confidence", DEFAULT_CONFIDENCE)),
            "retry": int(self.settings.value("retry", DEFAULT_RETRY)),
            "step_delay": int(self.settings.value("step_delay", DEFAULT_STEP_DELAY)),
            "minimize": self.settings.value("minimize", False, type=bool),
            "notify": self.settings.value("notify", True, type=bool)
        }

    def clear(self):
        """清除所有设置"""
        self.settings.clear()
