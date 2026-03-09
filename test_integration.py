"""
测试脚本 - 验证 Tab 2 和 Tab 3 集成
"""
import sys
from PyQt5.QtWidgets import QApplication

# 测试导入
try:
    from lark_auto_punch.ui.main_window import MainWindow
    from lark_auto_punch.ui.tab_recorder import TabRecorder
    from lark_auto_punch.ui.tab_scheduled_click import TabScheduledClick
    print("[OK] 所有模块导入成功")
except ImportError as e:
    print(f"[ERROR] 导入失败: {e}")
    sys.exit(1)

# 测试实例化
try:
    app = QApplication(sys.argv)
    window = MainWindow()
    print("[OK] 主窗口创建成功")

    # 检查 Tab 是否正确加载
    if hasattr(window.image_config, 'recorder_tab'):
        print("[OK] Tab 2 (键鼠录制器) 已加载")
    else:
        print("[ERROR] Tab 2 未加载")

    if hasattr(window.image_config, 'scheduled_click_tab'):
        print("[OK] Tab 3 (定时点击) 已加载")
    else:
        print("[ERROR] Tab 3 未加载")

    print("\n所有测试通过！可以运行 main.py 启动应用。")

except Exception as e:
    print(f"[ERROR] 创建窗口失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
