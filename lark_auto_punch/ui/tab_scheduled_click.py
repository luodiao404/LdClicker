"""
定时图片点击任务 - Tab 3
基于 pyautogui 和 opencv 实现定时图片识别和点击
"""
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QDateTimeEdit, QTableWidget, QTableWidgetItem,
    QGroupBox, QHeaderView, QMessageBox, QSpinBox, QLineEdit
)
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QTimer, Qt
from PyQt5.QtGui import QPixmap, QDoubleValidator


class ImageClickWorker(QThread):
    """图片点击执行线程"""
    log_signal = pyqtSignal(str, str)  # (message, level)
    status_signal = pyqtSignal(int, str)  # (task_id, status)
    finished_signal = pyqtSignal(int, bool, str)  # (task_id, success, message)

    def __init__(self, task_id, image_path, confidence=0.8, retry=3, retry_interval=1):
        super().__init__()
        self.task_id = task_id
        self.image_path = image_path
        self.confidence = confidence
        self.retry = retry
        self.retry_interval = retry_interval
        self.is_running = True

    def run(self):
        """执行图片识别和点击"""
        self.log_signal.emit(f"任务 {self.task_id}: 开始执行", "START")
        self.status_signal.emit(self.task_id, "执行中")

        # 检查图片文件
        if not Path(self.image_path).exists():
            error_msg = f"图片文件不存在: {self.image_path}"
            self.log_signal.emit(f"任务 {self.task_id}: {error_msg}", "ERROR")
            self.finished_signal.emit(self.task_id, False, error_msg)
            return

        # 重试机制
        for attempt in range(1, self.retry + 1):
            if not self.is_running:
                self.log_signal.emit(f"任务 {self.task_id}: 被中断", "STOP")
                self.finished_signal.emit(self.task_id, False, "任务被中断")
                return

            self.log_signal.emit(f"任务 {self.task_id}: 第 {attempt}/{self.retry} 次尝试", "INFO")

            try:
                # 使用 OpenCV 模板匹配
                success, x, y, confidence = self._find_image_opencv()

                if success:
                    # 执行点击
                    pyautogui.click(x, y)
                    success_msg = f"成功点击 ({x}, {y}), 相似度: {confidence:.2f}"
                    self.log_signal.emit(f"任务 {self.task_id}: {success_msg}", "SUCCESS")
                    self.finished_signal.emit(self.task_id, True, success_msg)
                    return
                else:
                    self.log_signal.emit(
                        f"任务 {self.task_id}: 未找到目标图片 (相似度 < {self.confidence})",
                        "WARNING"
                    )

            except Exception as e:
                self.log_signal.emit(f"任务 {self.task_id}: 异常 - {str(e)}", "ERROR")

            # 重试前等待
            if attempt < self.retry:
                time.sleep(self.retry_interval)

        # 所有重试失败
        error_msg = f"经过 {self.retry} 次尝试仍未找到目标图片"
        self.log_signal.emit(f"任务 {self.task_id}: {error_msg}", "FAIL")
        self.finished_signal.emit(self.task_id, False, error_msg)

    def _find_image_opencv(self):
        """使用 OpenCV 查找图片"""
        # 读取模板图片
        template = cv2.imread(self.image_path)
        if template is None:
            return False, 0, 0, 0.0

        h, w = template.shape[:2]

        # 截取屏幕
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
            return True, center_x, center_y, max_val

        return False, 0, 0, max_val

    def stop(self):
        """停止任务"""
        self.is_running = False


class TaskScheduler(QThread):
    """任务调度器"""
    task_trigger_signal = pyqtSignal(int)  # 触发任务信号 (task_id)
    log_signal = pyqtSignal(str, str)  # 日志信号

    def __init__(self):
        super().__init__()
        self.tasks = {}  # {task_id: task_info}
        self.is_running = True

    def run(self):
        """运行调度器"""
        self.log_signal.emit("任务调度器已启动", "INFO")

        while self.is_running:
            now = datetime.now()

            # 检查所有任务
            for task_id, task_info in list(self.tasks.items()):
                if task_info["status"] == "等待中":
                    trigger_time = task_info["trigger_time"]

                    # 检查是否到达触发时间
                    if now >= trigger_time:
                        self.log_signal.emit(f"触发任务 {task_id}", "SCHEDULE")
                        self.task_trigger_signal.emit(task_id)
                        # 更新状态为执行中（由主线程更新）

            # 每秒检查一次
            time.sleep(1)

        self.log_signal.emit("任务调度器已停止", "INFO")

    def add_task(self, task_id, task_info):
        """添加任务"""
        self.tasks[task_id] = task_info

    def remove_task(self, task_id):
        """移除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]

    def update_task_status(self, task_id, status):
        """更新任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status

    def stop(self):
        """停止调度器"""
        self.is_running = False


class TabScheduledClick(QWidget):
    """定时图片点击任务 Tab"""
    log_signal = pyqtSignal(str, str)  # 向主窗口发送日志

    def __init__(self):
        super().__init__()
        self.tasks = {}  # {task_id: task_info}
        self.next_task_id = 1
        self.scheduler = None
        self.active_workers = {}  # {task_id: worker}

        self.init_ui()
        self.start_scheduler()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 左侧：任务配置
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)

        # 标题
        title_label = QLabel("⏰ 定时图片点击任务")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        left_layout.addWidget(title_label)

        # 任务配置组
        config_group = QGroupBox("新建任务")
        config_layout = QVBoxLayout()

        # 图片选择
        image_layout = QHBoxLayout()
        image_label = QLabel("目标图片:")
        image_label.setMinimumWidth(80)
        image_layout.addWidget(image_label)

        self.image_path_input = QLineEdit()
        self.image_path_input.setPlaceholderText("点击右侧按钮选择图片...")
        self.image_path_input.setReadOnly(True)
        image_layout.addWidget(self.image_path_input, 1)

        self.select_image_btn = QPushButton("📁 选择图片")
        self.select_image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.select_image_btn)

        config_layout.addLayout(image_layout)

        # 图片预览
        self.image_preview = QLabel()
        self.image_preview.setFixedHeight(100)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 1px solid #ccc; background-color: #fafafa;")
        self.image_preview.setText("未选择图片")
        config_layout.addWidget(self.image_preview)

        # 时间设定
        time_layout = QHBoxLayout()
        time_label = QLabel("触发时间:")
        time_label.setMinimumWidth(80)
        time_layout.addWidget(time_label)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(60))
        time_layout.addWidget(self.datetime_edit)
        time_layout.addStretch()
        config_layout.addLayout(time_layout)

        # 高级设置
        advanced_layout = QHBoxLayout()

        # 相似度
        conf_label = QLabel("相似度:")
        advanced_layout.addWidget(conf_label)

        self.confidence_input = QLineEdit()
        self.confidence_input.setText("0.8")
        self.confidence_input.setValidator(QDoubleValidator(0.0, 1.0, 2))
        self.confidence_input.setFixedWidth(60)
        advanced_layout.addWidget(self.confidence_input)

        # 重试次数
        retry_label = QLabel("重试次数:")
        advanced_layout.addWidget(retry_label)

        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 10)
        self.retry_spin.setValue(3)
        self.retry_spin.setFixedWidth(80)
        advanced_layout.addWidget(self.retry_spin)

        # 重试间隔
        interval_label = QLabel("重试间隔:")
        advanced_layout.addWidget(interval_label)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10)
        self.interval_spin.setValue(1)
        self.interval_spin.setSuffix(" 秒")
        self.interval_spin.setFixedWidth(80)
        advanced_layout.addWidget(self.interval_spin)

        advanced_layout.addStretch()
        config_layout.addLayout(advanced_layout)

        # 添加任务按钮
        self.add_task_btn = QPushButton("➕ 添加任务")
        self.add_task_btn.setMinimumHeight(40)
        self.add_task_btn.clicked.connect(self.add_task)
        config_layout.addWidget(self.add_task_btn)

        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)
        left_layout.addStretch()

        main_layout.addWidget(left_widget, 1)

        # 右侧：任务列表
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # 说明
        info_group = QGroupBox("说明")
        info_layout = QVBoxLayout()
        info = QLabel("💡 设定时间后自动在屏幕上查找图片并点击\n\n"
                     "• 支持多任务并发执行\n"
                     "• 可设置相似度阈值和重试次数\n"
                     "• 任务执行后会显示结果")
        info.setWordWrap(True)
        info_layout.addWidget(info)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        # 任务列表组
        list_group = QGroupBox("任务列表")
        list_layout = QVBoxLayout()

        # 任务表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels([
            "ID", "图片路径", "触发时间", "状态", "结果", "操作"
        ])
        self.task_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        list_layout.addWidget(self.task_table)

        # 批量操作按钮
        batch_layout = QHBoxLayout()

        self.clear_completed_btn = QPushButton("🗑️ 清除已完成")
        self.clear_completed_btn.clicked.connect(self.clear_completed_tasks)

        self.clear_all_btn = QPushButton("🗑️ 清除全部")
        self.clear_all_btn.clicked.connect(self.clear_all_tasks)

        batch_layout.addWidget(self.clear_completed_btn)
        batch_layout.addWidget(self.clear_all_btn)
        batch_layout.addStretch()
        list_layout.addLayout(batch_layout)

        list_group.setLayout(list_layout)
        right_layout.addWidget(list_group, 1)

        main_layout.addWidget(right_widget, 1)

        self.setLayout(main_layout)

    def start_scheduler(self):
        """启动任务调度器"""
        self.scheduler = TaskScheduler()
        self.scheduler.task_trigger_signal.connect(self.execute_task)
        self.scheduler.log_signal.connect(self.emit_log)
        self.scheduler.start()

    def select_image(self):
        """选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择目标图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.image_path_input.setText(file_path)

            # 显示预览
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(scaled_pixmap)

    def add_task(self):
        """添加任务"""
        # 验证输入
        image_path = self.image_path_input.text()
        if not image_path:
            QMessageBox.warning(self, "警告", "请先选择目标图片！")
            return

        if not Path(image_path).exists():
            QMessageBox.warning(self, "警告", "图片文件不存在！")
            return

        trigger_time = self.datetime_edit.dateTime().toPyDateTime()
        now = datetime.now()

        if trigger_time <= now:
            QMessageBox.warning(self, "警告", "触发时间必须晚于当前时间！")
            return

        # 创建任务
        task_id = self.next_task_id
        self.next_task_id += 1

        task_info = {
            "id": task_id,
            "image_path": image_path,
            "trigger_time": trigger_time,
            "status": "等待中",
            "result": "",
            "confidence": float(self.confidence_input.text() or 0.8),
            "retry": self.retry_spin.value(),
            "retry_interval": self.interval_spin.value()
        }

        self.tasks[task_id] = task_info

        # 添加到调度器
        self.scheduler.add_task(task_id, task_info)

        # 添加到表格
        self.add_task_to_table(task_info)

        # 清空输入
        self.image_path_input.clear()
        self.image_preview.clear()
        self.image_preview.setText("未选择图片")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(60))

        self.emit_log(f"任务 {task_id} 已添加，将在 {trigger_time.strftime('%Y-%m-%d %H:%M:%S')} 执行", "INFO")

    def add_task_to_table(self, task_info):
        """添加任务到表格"""
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)

        # ID
        self.task_table.setItem(row, 0, QTableWidgetItem(str(task_info["id"])))

        # 图片路径
        self.task_table.setItem(row, 1, QTableWidgetItem(task_info["image_path"]))

        # 触发时间
        time_str = task_info["trigger_time"].strftime("%Y-%m-%d %H:%M:%S")
        self.task_table.setItem(row, 2, QTableWidgetItem(time_str))

        # 状态
        status_item = QTableWidgetItem(task_info["status"])
        status_item.setForeground(Qt.blue)
        self.task_table.setItem(row, 3, status_item)

        # 结果
        self.task_table.setItem(row, 4, QTableWidgetItem(task_info["result"]))

        # 操作按钮
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.delete_task(task_info["id"]))
        self.task_table.setCellWidget(row, 5, delete_btn)

    def execute_task(self, task_id):
        """执行任务"""
        if task_id not in self.tasks:
            return

        task_info = self.tasks[task_id]

        # 更新状态
        self.update_task_status(task_id, "执行中")
        self.scheduler.update_task_status(task_id, "执行中")

        # 创建工作线程
        worker = ImageClickWorker(
            task_id,
            task_info["image_path"],
            confidence=task_info["confidence"],
            retry=task_info["retry"],
            retry_interval=task_info["retry_interval"]
        )

        worker.log_signal.connect(self.emit_log)
        worker.status_signal.connect(self.update_task_status)
        worker.finished_signal.connect(self.on_task_finished)

        self.active_workers[task_id] = worker
        worker.start()

    def on_task_finished(self, task_id, success, message):
        """任务完成回调"""
        if task_id in self.tasks:
            status = "已完成" if success else "失败"
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["result"] = message

            self.update_task_status(task_id, status)
            self.update_task_result(task_id, message)

            # 从调度器移除
            self.scheduler.remove_task(task_id)

        # 清理工作线程
        if task_id in self.active_workers:
            del self.active_workers[task_id]

    def update_task_status(self, task_id, status):
        """更新任务状态"""
        for row in range(self.task_table.rowCount()):
            id_item = self.task_table.item(row, 0)
            if id_item and int(id_item.text()) == task_id:
                status_item = QTableWidgetItem(status)

                # 设置颜色
                if status == "等待中":
                    status_item.setForeground(Qt.blue)
                elif status == "执行中":
                    status_item.setForeground(Qt.darkYellow)
                elif status == "已完成":
                    status_item.setForeground(Qt.darkGreen)
                elif status == "失败":
                    status_item.setForeground(Qt.red)

                self.task_table.setItem(row, 3, status_item)
                break

    def update_task_result(self, task_id, result):
        """更新任务结果"""
        for row in range(self.task_table.rowCount()):
            id_item = self.task_table.item(row, 0)
            if id_item and int(id_item.text()) == task_id:
                self.task_table.setItem(row, 4, QTableWidgetItem(result))
                break

    def delete_task(self, task_id):
        """删除任务"""
        # 从调度器移除
        self.scheduler.remove_task(task_id)

        # 停止工作线程
        if task_id in self.active_workers:
            self.active_workers[task_id].stop()
            self.active_workers[task_id].wait()
            del self.active_workers[task_id]

        # 从任务字典移除
        if task_id in self.tasks:
            del self.tasks[task_id]

        # 从表格移除
        for row in range(self.task_table.rowCount()):
            id_item = self.task_table.item(row, 0)
            if id_item and int(id_item.text()) == task_id:
                self.task_table.removeRow(row)
                break

        self.emit_log(f"任务 {task_id} 已删除", "INFO")

    def clear_completed_tasks(self):
        """清除已完成的任务"""
        completed_ids = [
            task_id for task_id, task_info in self.tasks.items()
            if task_info["status"] in ["已完成", "失败"]
        ]

        for task_id in completed_ids:
            self.delete_task(task_id)

        if completed_ids:
            QMessageBox.information(self, "清除完成", f"已清除 {len(completed_ids)} 个任务")

    def clear_all_tasks(self):
        """清除所有任务"""
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有任务吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            task_ids = list(self.tasks.keys())
            for task_id in task_ids:
                self.delete_task(task_id)

            QMessageBox.information(self, "清除完成", f"已清除 {len(task_ids)} 个任务")

    def emit_log(self, message, level="INFO"):
        """发送日志信号"""
        self.log_signal.emit(message, level)

    def closeEvent(self, event):
        """关闭事件"""
        # 停止调度器
        if self.scheduler:
            self.scheduler.stop()
            self.scheduler.wait()

        # 停止所有工作线程
        for worker in self.active_workers.values():
            worker.stop()
            worker.wait()

        event.accept()
