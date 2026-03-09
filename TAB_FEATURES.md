# Tab 2 和 Tab 3 功能说明文档

## 📦 新增模块

### 1. Tab 2: 键鼠动作录制器 (`tab_recorder.py`)
**文件位置**: `lark_auto_punch/ui/tab_recorder.py`

#### 功能特性
- ✅ **全局键鼠监听**：基于 pynput 实现，可捕获所有键盘和鼠标事件
- ✅ **精确时间记录**：记录每个动作的相对时间间隔（Delta Time）
- ✅ **完整动作支持**：
  - 鼠标移动、点击（左/右/中键）、滚轮
  - 键盘按键按下/释放
- ✅ **回放功能**：严格按照时间间隔重现所有动作
- ✅ **中断保护**：回放时按 ESC 键可立即中断
- ✅ **保存/加载**：支持将录制保存为 JSON 文件，方便复用

#### 核心类

**RecorderWorker (QThread)**
- 录制工作线程，运行 pynput 监听器
- 捕获所有键鼠事件并记录时间戳
- 信号：
  - `log_signal(str, str)` - 日志输出
  - `status_signal(str)` - 状态更新
  - `action_count_signal(int)` - 动作计数

**PlayerWorker (QThread)**
- 回放工作线程，重现录制的动作
- 使用 pynput Controller 模拟键鼠操作
- 监听 ESC 键实现中断
- 信号：
  - `log_signal(str, str)` - 日志输出
  - `status_signal(str)` - 状态更新
  - `progress_signal(int, int)` - 回放进度
  - `finished_signal(bool)` - 完成信号

**TabRecorder (QWidget)**
- 主界面组件
- 提供录制、停止、回放、保存、加载功能
- 实时显示录制状态和动作数量

#### 使用流程
```
1. 点击"开始录制" → 执行需要录制的操作
2. 点击"停止录制" → 查看录制摘要
3. 点击"开始回放" → 自动重现操作（按 ESC 中断）
4. 可选：保存录制到文件，下次直接加载使用
```

---

### 2. Tab 3: 定时图片点击任务 (`tab_scheduled_click.py`)
**文件位置**: `lark_auto_punch/ui/tab_scheduled_click.py`

#### 功能特性
- ✅ **定时触发**：精确到秒的任务调度
- ✅ **图像识别**：基于 OpenCV 模板匹配
- ✅ **自动点击**：找到图片后自动点击中心位置
- ✅ **重试机制**：支持自定义重试次数和间隔
- ✅ **多任务并发**：支持同时添加多个任务
- ✅ **任务管理**：可视化任务列表，实时状态更新
- ✅ **批量操作**：清除已完成/清除全部

#### 核心类

**ImageClickWorker (QThread)**
- 图片识别和点击执行线程
- 使用 OpenCV 进行模板匹配
- 支持重试机制和自定义相似度阈值
- 信号：
  - `log_signal(str, str)` - 日志输出
  - `status_signal(int, str)` - 状态更新
  - `finished_signal(int, bool, str)` - 完成信号

**TaskScheduler (QThread)**
- 任务调度器，后台轮询任务列表
- 每秒检查一次是否有任务到达触发时间
- 自动触发符合条件的任务
- 信号：
  - `task_trigger_signal(int)` - 任务触发信号
  - `log_signal(str, str)` - 日志输出

**TabScheduledClick (QWidget)**
- 主界面组件
- 任务配置：图片选择、时间设定、高级参数
- 任务列表：QTableWidget 展示所有任务
- 任务管理：添加、删除、批量清除

#### 使用流程
```
1. 点击"选择图片" → 选择要查找的目标图片
2. 设置"触发时间" → 指定任务执行时间
3. 调整高级参数（可选）：相似度、重试次数、重试间隔
4. 点击"添加任务" → 任务进入等待队列
5. 到达设定时间后自动执行 → 查看执行结果
```

---

## 🔧 技术实现

### 线程安全设计
- **UI 线程**：只负责界面渲染和用户交互
- **工作线程**：所有耗时操作（监听、回放、图像识别）都在独立线程
- **信号槽通信**：使用 PyQt 信号槽机制安全地跨线程通信

### 关键技术点

#### Tab 2 - 键鼠录制
```python
# 动作数据结构
{
    "type": "mouse_click",  # 动作类型
    "x": 100,               # 坐标
    "y": 200,
    "button": "Button.left", # 按钮
    "pressed": True,        # 按下/释放
    "time": 1.234           # 相对时间（秒）
}
```

#### Tab 3 - 图片点击
```python
# 任务数据结构
{
    "id": 1,
    "image_path": "/path/to/image.png",
    "trigger_time": datetime(2026, 3, 9, 14, 30, 0),
    "status": "等待中",  # 等待中/执行中/已完成/失败
    "result": "",
    "confidence": 0.8,   # 相似度阈值
    "retry": 3,          # 重试次数
    "retry_interval": 1  # 重试间隔（秒）
}
```

---

## 📝 集成到主窗口

### 方法 1: 修改 `image_config.py`

在 `ImageConfigWidget` 的 `init_ui` 方法中添加：

```python
from .tab_recorder import TabRecorder
from .tab_scheduled_click import TabScheduledClick

# 在创建 Tab 控件后添加
tab_widget = QTabWidget()

# 原有的 Tab
tab_widget.addTab(images_tab, "📷 图片配置")

# 新增 Tab 2
self.recorder_tab = TabRecorder()
tab_widget.addTab(self.recorder_tab, "🎬 键鼠录制")

# 新增 Tab 3
self.scheduled_click_tab = TabScheduledClick()
tab_widget.addTab(self.scheduled_click_tab, "⏰ 定时点击")

# 原有的高级设置
tab_widget.addTab(settings_tab, "⚙️ 高级设置")
```

### 方法 2: 连接日志到主窗口

在 `MainWindow` 中连接信号：

```python
# 在 init_ui 方法中
self.image_config = ImageConfigWidget(self.images_dir)

# 连接日志信号
if hasattr(self.image_config, 'recorder_tab'):
    self.image_config.recorder_tab.log_signal.connect(self.append_log)

if hasattr(self.image_config, 'scheduled_click_tab'):
    self.image_config.scheduled_click_tab.log_signal.connect(self.append_log)
```

---

## 🎯 使用场景

### Tab 2 - 键鼠录制器
- **重复性操作自动化**：录制一次，多次回放
- **测试脚本录制**：快速生成测试用例
- **演示录制**：记录操作步骤用于演示
- **游戏辅助**：录制游戏操作序列

### Tab 3 - 定时图片点击
- **定时签到**：每天固定时间点击签到按钮
- **定时提醒**：到达时间后点击弹窗确认
- **批量任务**：设置多个时间点执行不同操作
- **监控告警**：定时检查特定图标并点击

---

## ⚠️ 注意事项

### Tab 2 注意事项
1. **权限要求**：某些系统需要授予辅助功能权限
2. **回放速度**：严格按照录制时的时间间隔回放
3. **中断机制**：回放时按 ESC 键可立即中断
4. **文件格式**：保存为 JSON 格式，可手动编辑

### Tab 3 注意事项
1. **图片质量**：截图应清晰，避免模糊
2. **分辨率一致**：截图和执行时的分辨率应一致
3. **相似度调整**：如果识别失败，可降低相似度阈值
4. **时间设置**：触发时间必须晚于当前时间
5. **任务清理**：定期清除已完成的任务

---

## 📦 依赖库

已添加到 `requirements.txt`：
```
pynput>=1.7.0  # 键鼠监听和控制
```

其他依赖（已有）：
- PyQt5 - GUI 框架
- opencv-python - 图像识别
- numpy - 数组处理
- pyautogui - 屏幕截图和点击

---

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python main.py
```

### 测试 Tab 2
1. 切换到"键鼠录制"标签页
2. 点击"开始录制"
3. 执行一些鼠标和键盘操作
4. 点击"停止录制"
5. 点击"开始回放"查看效果

### 测试 Tab 3
1. 切换到"定时点击"标签页
2. 截取一张屏幕上的图标
3. 点击"选择图片"选择该图标
4. 设置触发时间（如 1 分钟后）
5. 点击"添加任务"
6. 等待任务自动执行

---

## 🎨 界面预览

### Tab 2 - 键鼠录制器
```
┌─────────────────────────────────────┐
│ 🎬 键鼠动作录制器                    │
├─────────────────────────────────────┤
│ 💡 录制键盘和鼠标的所有操作...       │
├─────────────────────────────────────┤
│ 控制面板                             │
│ [🔴 开始录制] [⏹ 停止录制] [▶ 开始回放] │
│ [💾 保存录制] [📂 加载录制]          │
├─────────────────────────────────────┤
│ 状态信息                             │
│ 就绪                                 │
│ 已录制动作: 0                        │
├─────────────────────────────────────┤
│ 动作详情                             │
│ (录制摘要显示区域)                   │
└─────────────────────────────────────┘
```

### Tab 3 - 定时图片点击
```
┌─────────────────────────────────────┐
│ ⏰ 定时图片点击任务                  │
├─────────────────────────────────────┤
│ 💡 设定时间后自动在屏幕上查找...     │
├─────────────────────────────────────┤
│ 新建任务                             │
│ 目标图片: [____________] [📁 选择]   │
│ (图片预览区域)                       │
│ 触发时间: [2026-03-09 14:30:00]     │
│ 相似度: [0.8] 重试: [3] 间隔: [1秒] │
│ [➕ 添加任务]                        │
├─────────────────────────────────────┤
│ 任务列表                             │
│ ┌──┬────────┬──────────┬────┬────┐ │
│ │ID│图片路径│触发时间  │状态│操作│ │
│ ├──┼────────┼──────────┼────┼────┤ │
│ │1 │icon.png│14:30:00  │等待│删除│ │
│ └──┴────────┴──────────┴────┴────┘ │
│ [🗑️ 清除已完成] [🗑️ 清除全部]      │
└─────────────────────────────────────┘
```

---

## 📚 API 文档

### TabRecorder

#### 信号
- `log_signal(message: str, level: str)` - 发送日志

#### 方法
- `start_recording()` - 开始录制
- `stop_recording()` - 停止录制
- `start_playing()` - 开始回放
- `save_recording()` - 保存录制
- `load_recording()` - 加载录制

### TabScheduledClick

#### 信号
- `log_signal(message: str, level: str)` - 发送日志

#### 方法
- `select_image()` - 选择图片
- `add_task()` - 添加任务
- `delete_task(task_id: int)` - 删除任务
- `clear_completed_tasks()` - 清除已完成任务
- `clear_all_tasks()` - 清除所有任务

---

## 🐛 常见问题

### Q1: pynput 监听器无法启动
**A**: 检查系统权限设置，某些系统需要授予辅助功能权限。

### Q2: 图片识别失败
**A**:
1. 检查图片文件是否存在
2. 降低相似度阈值（如从 0.8 降到 0.7）
3. 确保截图和执行时的分辨率一致
4. 增加重试次数

### Q3: 回放时鼠标失控
**A**: 按 ESC 键立即中断回放。

### Q4: 任务没有自动执行
**A**:
1. 检查触发时间是否正确
2. 确保任务状态为"等待中"
3. 查看日志输出的错误信息

---

## 🔄 更新日志

### v1.0.0 (2026-03-09)
- ✅ 实现 Tab 2: 键鼠动作录制器
- ✅ 实现 Tab 3: 定时图片点击任务
- ✅ 完整的线程安全设计
- ✅ 详细的中文注释和文档

---

## 📞 技术支持

如有问题，请查看：
1. 代码中的详细注释
2. `INTEGRATION_EXAMPLE.py` 集成示例
3. 本文档的常见问题部分
