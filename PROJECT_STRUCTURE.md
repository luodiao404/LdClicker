"""
项目结构说明
"""

# Lark 自动打卡助手 - 项目结构

## 目录结构

```
lark/
├── lark_auto_punch/              # 主包目录
│   ├── __init__.py               # 包初始化文件
│   ├── config.py                 # 全局配置文件
│   │
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   └── automation.py         # 自动化执行线程（图像识别+点击）
│   │
│   ├── ui/                       # 用户界面模块
│   │   ├── __init__.py
│   │   ├── image_config.py       # 图片配置组件（Tab切换、上传、保存）
│   │   └── main_window.py        # 主窗口（任务控制、日志显示）
│   │
│   └── utils/                    # 工具类模块
│       ├── __init__.py
│       ├── config_manager.py     # 配置导入导出管理器
│       └── settings.py           # 设置持久化管理器
│
├── images/                       # 图片存储目录（运行时自动创建）
│   ├── lark.png
│   ├── 工作台.png
│   ├── 假勤.png
│   ├── 上班.png
│   └── 下班.png
│
├── main.py                       # 程序入口文件
├── requirements.txt              # Python 依赖列表
├── README.md                     # 项目说明文档
└── demo.py                       # 旧版命令行脚本（保留）
```

## 模块说明

### 1. config.py - 全局配置
- 应用信息（名称、版本）
- 目录路径配置
- 默认参数设置
- 日志颜色配置

### 2. core/automation.py - 自动化核心
- `AutomationWorker` 类：QThread 工作线程
- 图像识别：OpenCV 模板匹配
- 自动点击：PyAutoGUI 鼠标控制
- 任务链执行：按步骤执行打卡流程

### 3. ui/image_config.py - 图片配置界面
- `ImageConfigWidget` 类：图片配置组件
- Tab 1：图片上传、保存、导入导出
- Tab 2：高级设置（识别精度、延迟、通知）
- 缩略图预览、状态显示

### 4. ui/main_window.py - 主窗口
- `MainWindow` 类：应用主窗口
- 时间任务配置区
- 任务控制区（启动、停止、测试）
- 日志显示区
- 定时任务调度

### 5. utils/config_manager.py - 配置管理
- `ConfigManager` 类：配置导入导出
- 导出：打包图片为 zip 文件
- 导入：解压 zip 并恢复图片

### 6. utils/settings.py - 设置管理
- `SettingsManager` 类：设置持久化
- 使用 QSettings 保存到本地
- 支持加载、保存、清除操作

## 运行方式

### 开发模式
```bash
python main.py
```

### 打包为可执行文件（可选）
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="Lark自动打卡" main.py
```

## 模块依赖关系

```
main.py
  └── ui/main_window.py
        ├── ui/image_config.py
        │     ├── utils/config_manager.py
        │     └── utils/settings.py
        ├── core/automation.py
        └── config.py
```

## 扩展建议

### 添加新功能
1. 在 `core/` 下添加新的功能模块
2. 在 `ui/` 下添加对应的界面组件
3. 在 `config.py` 中添加相关配置

### 添加新的打卡流程
1. 修改 `config.py` 中的 `IMAGE_NAMES`
2. 在 `core/automation.py` 中调整 `task_list`
3. 在 `ui/image_config.py` 中更新图片配置列表

### 添加数据库支持
1. 在 `utils/` 下创建 `database.py`
2. 实现打卡记录的存储和查询
3. 在主窗口添加历史记录查看功能

## 代码规范

- 使用 Python 3.7+ 特性
- 遵循 PEP 8 代码风格
- 类名使用大驼峰命名
- 函数名使用小写+下划线
- 添加详细的中文注释
- 每个模块包含 docstring

## 测试建议

1. **单元测试**：测试各个工具类的功能
2. **集成测试**：测试完整的打卡流程
3. **UI 测试**：测试界面交互和响应
4. **性能测试**：测试图像识别速度和准确率
