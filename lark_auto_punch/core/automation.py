"""
自动化工作线程
负责图像识别和自动点击
"""
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from PyQt5.QtCore import QThread, pyqtSignal


class AutomationWorker(QThread):
    """
    自动化执行工作线程
    负责图像识别和自动点击，避免阻塞 UI 线程
    """
    # 信号定义
    log_signal = pyqtSignal(str, str)  # (message, level)
    task_finished = pyqtSignal(bool)  # 任务完成信号，参数为是否成功

    def __init__(self, images_dir, action_type, confidence=0.8, retry=3, step_delay=2.0):
        super().__init__()
        self.images_dir = Path(images_dir)
        self.action_type = action_type  # "上班" 或 "下班"
        self.confidence = confidence
        self.retry = retry
        self.step_delay = step_delay
        self.is_running = True

    def log(self, message, level="INFO"):
        """发送日志信号到主线程"""
        self.log_signal.emit(message, level)

    def find_and_click(self, template_path, wait_after=2.0):
        """
        在屏幕上寻找图片并点击
        :param template_path: 图片路径
        :param wait_after: 点击成功后的等待时间(秒)
        :return: Boolean (是否成功)
        """
        if not self.is_running:
            return False

        # 检查文件是否存在
        template_path = Path(template_path)
        if not template_path.exists():
            self.log(f"文件不存在: {template_path}", level="ERROR")
            return False

        self.log(f"正在寻找目标: {template_path.name}")

        # 读取模板图片
        template = cv2.imread(str(template_path))
        if template is None:
            self.log(f"无法读取图片: {template_path}", level="ERROR")
            return False

        h, w = template.shape[:2]

        # 重试循环
        for attempt in range(1, self.retry + 1):
            if not self.is_running:
                return False

            try:
                # 截图
                screenshot = pyautogui.screenshot()
                screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                # 模板匹配
                result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                # 判断相似度
                if max_val >= self.confidence:
                    # 计算中心坐标
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2

                    self.log(f"✓ 找到目标 (相似度: {max_val:.2f}) 坐标: ({center_x}, {center_y})", level="SUCCESS")

                    # 执行点击
                    pyautogui.moveTo(center_x, center_y)
                    pyautogui.click()

                    # 点击后等待
                    self.log(f"等待 {wait_after} 秒...")
                    time.sleep(wait_after)
                    return True
                else:
                    self.log(f"第 {attempt}/{self.retry} 次尝试 (相似度: {max_val:.2f} < {self.confidence})", level="WARNING")

            except Exception as e:
                self.log(f"异常: {e}", level="ERROR")

            # 重试前等待
            if attempt < self.retry:
                time.sleep(1)

        self.log(f"✗ 未找到目标: {template_path.name}", level="FAIL")
        return False

    def run(self):
        """执行自动化任务"""
        self.log("=" * 50, level="START")
        self.log("开始执行自动打卡任务", level="START")

        # 定义任务链路
        task_list = [
            (self.images_dir / "lark.png", self.step_delay, "打开 Lark"),
            (self.images_dir / "工作台.png", self.step_delay, "点击工作台"),
            (self.images_dir / "假勤.png", self.step_delay, "进入假勤应用"),
        ]

        # 根据动作类型添加最后一步
        if self.action_type == "上班":
            task_list.append((self.images_dir / "上班.png", 1.0, "点击上班打卡"))
        else:
            task_list.append((self.images_dir / "下班.png", 1.0, "点击下班打卡"))

        # 执行任务链
        success = True
        for i, (img_path, wait_time, description) in enumerate(task_list, 1):
            if not self.is_running:
                self.log("任务被用户中止", level="STOP")
                success = False
                break

            self.log(f"--- 步骤 {i}/{len(task_list)}: {description} ---", level="STEP")

            if not self.find_and_click(str(img_path), wait_after=wait_time):
                self.log(f"步骤 {i} 失败，任务中止", level="FAIL")
                success = False
                break

        if success:
            self.log("✓ 打卡任务执行成功！", level="SUCCESS")
        else:
            self.log("✗ 打卡任务执行失败", level="FAIL")

        self.log("=" * 50, level="END")
        self.task_finished.emit(success)

    def stop(self):
        """停止任务"""
        self.is_running = False
