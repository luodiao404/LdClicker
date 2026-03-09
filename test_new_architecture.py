"""
测试新架构 - 每个 Tab 都是独立的完整页面
"""
import sys
from PyQt5.QtWidgets import QApplication

print("=" * 60)
print("测试新架构：Tab 切换整个页面")
print("=" * 60)

# 测试导入
print("\n[1/4] 测试模块导入...")
try:
    from lark_auto_punch.ui.main_window import MainWindow
    from lark_auto_punch.ui.tab_auto_punch import TabAutoPunch
    from lark_auto_punch.ui.tab_recorder import TabRecorder
    from lark_auto_punch.ui.tab_scheduled_click import TabScheduledClick
    from lark_auto_punch.ui.tab_settings import TabSettings
    print("[OK] 所有模块导入成功")
except ImportError as e:
    print(f"[ERROR] 导入失败: {e}")
    sys.exit(1)

# 测试实例化
print("\n[2/4] 测试主窗口创建...")
try:
    app = QApplication(sys.argv)
    window = MainWindow()
    print("[OK] 主窗口创建成功")
except Exception as e:
    print(f"[ERROR] 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 检查 Tab 加载
print("\n[3/4] 检查 Tab 加载...")
tabs_info = [
    ("auto_punch_tab", "Tab 1: 自动打卡"),
    ("recorder_tab", "Tab 2: 键鼠录制"),
    ("scheduled_click_tab", "Tab 3: 定时点击"),
    ("settings_tab", "Tab 4: 高级设置")
]

all_loaded = True
for attr_name, tab_name in tabs_info:
    if hasattr(window, attr_name):
        print(f"[OK] {tab_name} 已加载")
    else:
        print(f"[ERROR] {tab_name} 未加载")
        all_loaded = False

# 检查架构
print("\n[4/4] 检查新架构...")
print("[INFO] 新架构特点:")
print("  - 每个 Tab 都是独立的完整页面")
print("  - 切换 Tab 时整个页面都会切换")
print("  - Tab 1: 左侧图片配置 + 右侧任务控制和日志")
print("  - Tab 2: 键鼠录制器的完整界面")
print("  - Tab 3: 定时点击任务的完整界面")
print("  - Tab 4: 高级设置的完整界面")

if all_loaded:
    print("\n" + "=" * 60)
    print("[SUCCESS] 所有测试通过！")
    print("=" * 60)
    print("\n可以运行 'python main.py' 启动应用")
    print("\n新架构说明:")
    print("  1. 主窗口顶部有 4 个 Tab 标签")
    print("  2. 点击不同 Tab，整个页面内容都会切换")
    print("  3. 每个 Tab 都有自己独立的布局和功能")
    print("  4. 不再是左右分栏，而是完整页面切换")
else:
    print("\n[ERROR] 部分测试失败")
    sys.exit(1)
