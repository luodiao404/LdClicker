"""
配置文件
存储应用的全局配置和常量
"""
from pathlib import Path

# 应用信息
APP_NAME = "老登点点器"
APP_VERSION = "1.0.0"
APP_ORG = "LarkAutoPunch"

# 目录配置
BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "images"

# 图片配置
IMAGE_NAMES = ["lark", "工作台", "假勤", "上班", "下班"]

# 默认设置
DEFAULT_CONFIDENCE = 0.8  # 图像识别相似度阈值
DEFAULT_RETRY = 3  # 重试次数
DEFAULT_STEP_DELAY = 2  # 步骤间延迟（秒）
DEFAULT_JITTER_MINUTES = 5  # 时间偏差（分钟）

# 时间配置
DEFAULT_CHECKIN_TIME = "09:00"  # 默认上班时间
DEFAULT_CHECKOUT_TIME = "18:00"  # 默认下班时间

# 日志颜色配置
LOG_COLORS = {
    "INFO": "#d4d4d4",
    "SUCCESS": "#4CAF50",
    "WARNING": "#FFC107",
    "ERROR": "#f44336",
    "FAIL": "#f44336",
    "START": "#2196F3",
    "END": "#9C27B0",
    "STEP": "#00BCD4",
    "SCHEDULE": "#FF9800",
    "STOP": "#f44336",
}

# 确保目录存在
IMAGES_DIR.mkdir(exist_ok=True)
