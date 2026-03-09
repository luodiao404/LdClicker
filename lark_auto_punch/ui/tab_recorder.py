"""
Tab 2: 键鼠动作录制器
"""
import time
import json
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QGroupBox, QFileDialog, QMessageBox, QComboBox, QSpinBox, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController

from ..config import LOG_COLORS


class RecorderWorker(QThread):
    """录制工作线程"""
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str)
    action_count_signal = pyqtSignal(int)
    stop_signal = pyqtSignal()  # 新增：停止录制信号

    def __init__(self):
        super().__init__()
        self.actions = []
        self.is_recording = False
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.stop_hotkey_listener = None

    def run(self):
        self.actions = []
        self.is_recording = True
        self.start_time = time.time()

        self.log_signal.emit("开始录制键鼠动作...", "START")
        self.log_signal.emit("提示: 按 F9 键可停止录制", "INFO")
        self.status_signal.emit("正在录制...")

        # 启动停止快捷键监听器
        self.stop_hotkey_listener = keyboard.Listener(on_press=self.on_stop_hotkey)
        self.stop_hotkey_listener.start()

        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

        while self.is_recording:
            time.sleep(0.1)

        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.stop_hotkey_listener:
            self.stop_hotkey_listener.stop()

        self.log_signal.emit(f"录制完成，共记录 {len(self.actions)} 个动作", "SUCCESS")
        self.status_signal.emit(f"录制完成 ({len(self.actions)} 个动作)")

    def on_stop_hotkey(self, key):
        """监听 F9 键停止录制"""
        try:
            if key == keyboard.Key.f9:
                self.log_signal.emit("检测到 F9 键，停止录制", "STOP")
                self.is_recording = False
                self.stop_signal.emit()  # 发送停止信号
        except AttributeError:
            pass

    def on_mouse_move(self, x, y):
        if not self.is_recording:
            return
        delta_time = time.time() - self.start_time
        action = {"type": "mouse_move", "x": x, "y": y, "time": delta_time}
        self.actions.append(action)
        self.action_count_signal.emit(len(self.actions))

    def on_mouse_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
        delta_time = time.time() - self.start_time
        action = {
            "type": "mouse_click",
            "x": x, "y": y,
            "button": str(button),
            "pressed": pressed,
            "time": delta_time
        }
        self.actions.append(action)
        self.action_count_signal.emit(len(self.actions))

        button_name = "左键" if button == Button.left else "右键" if button == Button.right else "中键"
        action_name = "按下" if pressed else "释放"
        self.log_signal.emit(f"鼠标{button_name}{action_name} at ({x}, {y})", "INFO")

    def on_mouse_scroll(self, x, y, dx, dy):
        if not self.is_recording:
            return
        delta_time = time.time() - self.start_time
        action = {"type": "mouse_scroll", "x": x, "y": y, "dx": dx, "dy": dy, "time": delta_time}
        self.actions.append(action)
        self.action_count_signal.emit(len(self.actions))

    def on_key_press(self, key):
        if not self.is_recording:
            return
        delta_time = time.time() - self.start_time
        try:
            key_char = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_char = str(key)
        action = {"type": "key_press", "key": key_char, "time": delta_time}
        self.actions.append(action)
        self.action_count_signal.emit(len(self.actions))
        self.log_signal.emit(f"按键按下: {key_char}", "INFO")

    def on_key_release(self, key):
        if not self.is_recording:
            return
        delta_time = time.time() - self.start_time
        try:
            key_char = key.char if hasattr(key, 'char') else str(key)
        except AttributeError:
            key_char = str(key)
        action = {"type": "key_release", "key": key_char, "time": delta_time}
        self.actions.append(action)
        self.action_count_signal.emit(len(self.actions))

    def stop(self):
        self.is_recording = False

    def get_actions(self):
        return self.actions


class PlayerWorker(QThread):
    """回放工作线程"""
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(bool)

    def __init__(self, actions, speed=1.0):
        super().__init__()
        self.actions = actions
        self.speed = speed  # 回放速度倍数
        self.is_playing = False
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.interrupt_listener = None
        self.interrupted = False

    def run(self):
        if not self.actions:
            self.log_signal.emit("没有可回放的动作", "WARNING")
            self.finished_signal.emit(False)
            return

        self.is_playing = True
        self.interrupted = False

        self.interrupt_listener = keyboard.Listener(on_press=self.on_interrupt_key)
        self.interrupt_listener.start()

        speed_text = f"{self.speed}x" if self.speed != 1.0 else "正常"
        self.log_signal.emit(f"开始回放 {len(self.actions)} 个动作 (速度: {speed_text})...", "START")
        self.log_signal.emit("提示: 按 ESC 键可中断回放", "INFO")
        self.status_signal.emit("正在回放...")

        last_time = 0
        success = True

        try:
            for i, action in enumerate(self.actions):
                if not self.is_playing or self.interrupted:
                    self.log_signal.emit("回放被中断", "STOP")
                    success = False
                    break

                delta = action["time"] - last_time
                if delta > 0:
                    # 根据速度调整延迟时间
                    time.sleep(delta / self.speed)
                last_time = action["time"]

                self._execute_action(action)
                self.progress_signal.emit(i + 1, len(self.actions))

            if success:
                self.log_signal.emit("回放完成", "SUCCESS")
                self.status_signal.emit("回放完成")

        except Exception as e:
            self.log_signal.emit(f"回放出错: {str(e)}", "ERROR")
            success = False

        finally:
            if self.interrupt_listener:
                self.interrupt_listener.stop()
            self.finished_signal.emit(success)

    def _execute_action(self, action):
        action_type = action["type"]

        if action_type == "mouse_move":
            self.mouse_controller.position = (action["x"], action["y"])

        elif action_type == "mouse_click":
            button_str = action["button"]
            if "left" in button_str.lower():
                button = Button.left
            elif "right" in button_str.lower():
                button = Button.right
            else:
                button = Button.middle

            if action["pressed"]:
                self.mouse_controller.press(button)
            else:
                self.mouse_controller.release(button)

        elif action_type == "mouse_scroll":
            self.mouse_controller.scroll(action["dx"], action["dy"])

        elif action_type == "key_press":
            key = self._parse_key(action["key"])
            if key:
                self.keyboard_controller.press(key)

        elif action_type == "key_release":
            key = self._parse_key(action["key"])
            if key:
                self.keyboard_controller.release(key)

    def _parse_key(self, key_str):
        if key_str.startswith("Key."):
            key_name = key_str.replace("Key.", "")
            try:
                return getattr(Key, key_name)
            except AttributeError:
                return None
        if len(key_str) == 1:
            return key_str
        return None

    def on_interrupt_key(self, key):
        if key == Key.esc:
            self.interrupted = True
            self.is_playing = False

    def stop(self):
        self.is_playing = False


class TabRecorder(QWidget):
    """键鼠动作录制器 Tab"""
    log_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.recorder_worker = None
        self.player_worker = None
        self.recorded_actions = []
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 左侧：控制面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)

        # 标题
        title = QLabel("🎬 键鼠动作录制器")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        left_layout.addWidget(title)

        # 控制面板
        left_layout.addWidget(self.create_control_panel())

        # 状态信息
        left_layout.addWidget(self.create_status_panel())

        left_layout.addStretch()
        main_layout.addWidget(left_widget, 1)

        # 右侧：日志和说明
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # 说明
        info_group = QGroupBox("说明")
        info_layout = QVBoxLayout()
        info = QLabel("💡 录制键盘和鼠标的所有操作，并可精确回放\n\n"
                     "• 点击「开始录制」后，窗口会自动最小化\n"
                     "• 录制时按 F9 键可停止录制\n"
                     "• 停止录制后窗口会自动恢复\n"
                     "• 点击「开始回放」精确重现录制的操作\n"
                     "• 回放时按 ESC 键可中断")
        info.setWordWrap(True)
        info_layout.addWidget(info)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        # 日志
        right_layout.addWidget(self.create_log_panel(), 1)

        main_layout.addWidget(right_widget, 1)

        self.setLayout(main_layout)
        self.emit_log("录制器已加载", "INFO")

    def create_control_panel(self):
        group = QGroupBox("🎮 控制面板")

        layout = QVBoxLayout()

        # 主控制按钮
        btn_layout = QHBoxLayout()

        self.start_record_btn = QPushButton("🔴 开始录制")
        self.start_record_btn.setMinimumHeight(45)
        self.start_record_btn.clicked.connect(self.start_recording)

        self.stop_record_btn = QPushButton("⏹ 停止录制")
        self.stop_record_btn.setMinimumHeight(45)
        self.stop_record_btn.clicked.connect(self.stop_recording)
        self.stop_record_btn.setEnabled(False)

        self.play_btn = QPushButton("▶ 开始回放")
        self.play_btn.setMinimumHeight(45)
        self.play_btn.clicked.connect(self.start_playing)
        self.play_btn.setEnabled(False)

        btn_layout.addWidget(self.start_record_btn)
        btn_layout.addWidget(self.stop_record_btn)
        btn_layout.addWidget(self.play_btn)
        layout.addLayout(btn_layout)

        # 回放设置
        playback_group = QGroupBox("回放设置")
        playback_layout = QVBoxLayout()

        # 倍速设置
        speed_layout = QHBoxLayout()
        speed_label = QLabel("回放速度:")
        speed_label.setMinimumWidth(70)
        speed_layout.addWidget(speed_label)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "0.75x", "1x (正常)", "1.5x", "2x", "3x"])
        self.speed_combo.setCurrentIndex(2)  # 默认 1x
        speed_layout.addWidget(self.speed_combo)
        speed_layout.addStretch()
        playback_layout.addLayout(speed_layout)

        # 定时回放
        timer_layout = QHBoxLayout()
        self.enable_timer_checkbox = QCheckBox("定时回放")
        timer_layout.addWidget(self.enable_timer_checkbox)

        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 3600)
        self.delay_spin.setValue(5)
        self.delay_spin.setSuffix(" 秒后")
        self.delay_spin.setEnabled(False)
        timer_layout.addWidget(self.delay_spin)

        self.enable_timer_checkbox.toggled.connect(self.delay_spin.setEnabled)
        timer_layout.addStretch()
        playback_layout.addLayout(timer_layout)

        playback_group.setLayout(playback_layout)
        layout.addWidget(playback_group)

        # 文件操作
        file_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 保存录制")
        self.save_btn.clicked.connect(self.save_recording)
        self.save_btn.setEnabled(False)

        self.load_btn = QPushButton("📂 加载录制")
        self.load_btn.clicked.connect(self.load_recording)

        file_layout.addWidget(self.save_btn)
        file_layout.addWidget(self.load_btn)
        file_layout.addStretch()
        layout.addLayout(file_layout)

        group.setLayout(layout)
        return group

    def create_status_panel(self):
        group = QGroupBox("📊 状态信息")

        layout = QVBoxLayout()

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        info_layout = QHBoxLayout()

        self.action_count_label = QLabel("已录制动作: 0")
        self.progress_label = QLabel("")

        info_layout.addWidget(self.action_count_label)
        info_layout.addWidget(self.progress_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        group.setLayout(layout)
        return group

    def create_log_panel(self):
        group = QGroupBox("📋 运行日志")

        layout = QVBoxLayout()

        header = QHBoxLayout()
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        header.addStretch()
        header.addWidget(clear_btn)
        layout.addLayout(header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #ccc;
            }
        """)
        layout.addWidget(self.log_text)

        group.setLayout(layout)
        return group

    def start_recording(self):
        self.recorder_worker = RecorderWorker()
        self.recorder_worker.log_signal.connect(self.emit_log)
        self.recorder_worker.status_signal.connect(self.update_status)
        self.recorder_worker.action_count_signal.connect(self.update_action_count)
        self.recorder_worker.stop_signal.connect(self.on_recording_stopped)  # 连接停止信号
        self.recorder_worker.start()

        self.start_record_btn.setEnabled(False)
        self.stop_record_btn.setEnabled(True)
        self.play_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        self.emit_log("录制已启动", "START")

        # 最小化主窗口
        main_window = self.window()
        if main_window:
            main_window.showMinimized()
            self.emit_log("窗口已最小化，按 F9 停止录制", "INFO")

    def on_recording_stopped(self):
        """录制停止时的回调（由 F9 快捷键触发）"""
        self.stop_recording()

    def stop_recording(self):
        if self.recorder_worker:
            self.recorder_worker.stop()
            self.recorder_worker.wait()
            self.recorded_actions = self.recorder_worker.get_actions()

            self.start_record_btn.setEnabled(True)
            self.stop_record_btn.setEnabled(False)
            self.play_btn.setEnabled(len(self.recorded_actions) > 0)
            self.save_btn.setEnabled(len(self.recorded_actions) > 0)

            self.emit_log("录制已停止", "STOP")

            # 恢复主窗口
            main_window = self.window()
            if main_window:
                main_window.showNormal()
                main_window.activateWindow()
                self.emit_log("窗口已恢复", "INFO")

    def start_playing(self):
        if not self.recorded_actions:
            QMessageBox.warning(self, "警告", "没有可回放的动作！")
            return

        # 获取回放速度
        speed_text = self.speed_combo.currentText()
        speed_map = {
            "0.5x": 0.5,
            "0.75x": 0.75,
            "1x (正常)": 1.0,
            "1.5x": 1.5,
            "2x": 2.0,
            "3x": 3.0
        }
        speed = speed_map.get(speed_text, 1.0)

        # 检查是否启用定时回放
        if self.enable_timer_checkbox.isChecked():
            delay = self.delay_spin.value()
            self.emit_log(f"定时回放: {delay} 秒后开始", "INFO")
            self.play_btn.setEnabled(False)
            self.start_record_btn.setEnabled(False)

            # 使用 QTimer 实现延迟
            QTimer.singleShot(delay * 1000, lambda: self._execute_playback(speed))
        else:
            self._execute_playback(speed)

    def _execute_playback(self, speed):
        """执行回放"""
        self.player_worker = PlayerWorker(self.recorded_actions, speed)
        self.player_worker.log_signal.connect(self.emit_log)
        self.player_worker.status_signal.connect(self.update_status)
        self.player_worker.progress_signal.connect(self.update_progress)
        self.player_worker.finished_signal.connect(self.on_playback_finished)
        self.player_worker.start()

        self.start_record_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.emit_log("回放已启动", "START")

    def on_playback_finished(self, success):
        self.start_record_btn.setEnabled(True)
        self.play_btn.setEnabled(True)

        if success:
            self.emit_log("回放成功完成", "SUCCESS")
        else:
            self.emit_log("回放未完成", "WARNING")

    def update_status(self, status):
        self.status_label.setText(status)

    def update_action_count(self, count):
        self.action_count_label.setText(f"已录制动作: {count}")

    def update_progress(self, current, total):
        percentage = int((current / total) * 100)
        self.progress_label.setText(f"回放进度: {current}/{total} ({percentage}%)")

    def save_recording(self):
        if not self.recorded_actions:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存录制",
            f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON 文件 (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.recorded_actions, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "保存成功", f"录制已保存")
                self.emit_log(f"录制已保存", "SUCCESS")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存出错:\n{str(e)}")
                self.emit_log(f"保存失败: {str(e)}", "ERROR")

    def load_recording(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载录制", "", "JSON 文件 (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.recorded_actions = json.load(f)

                self.action_count_label.setText(f"已录制动作: {len(self.recorded_actions)}")
                self.play_btn.setEnabled(True)
                self.save_btn.setEnabled(True)

                QMessageBox.information(self, "加载成功", f"成功加载 {len(self.recorded_actions)} 个动作")
                self.emit_log(f"录制已加载", "SUCCESS")
            except Exception as e:
                QMessageBox.critical(self, "加载失败", f"加载出错:\n{str(e)}")
                self.emit_log(f"加载失败: {str(e)}", "ERROR")

    def emit_log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = LOG_COLORS.get(level, "#CFD8DC")
        formatted = f'<span style="color: #90A4AE;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{level}]</span> <span style="color: #CFD8DC;">{message}</span>'
        self.log_text.append(formatted)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        self.log_signal.emit(message, level)
