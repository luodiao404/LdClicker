"""
现代化 UI 样式库 - 简洁版
提供统一的样式和组件，使用克制的配色
"""

# 颜色方案 - 简洁版
COLORS = {
    # 主色调 - 蓝色系
    "primary": "#2196F3",
    "primary_hover": "#1976D2",
    "primary_light": "#BBDEFB",
    "primary_dark": "#0D47A1",

    # 辅助色 - 只保留必要的
    "success": "#4CAF50",
    "success_hover": "#45a049",
    "danger": "#f44336",
    "danger_hover": "#d32f2f",

    # 中性色 - 灰色系
    "dark": "#212121",
    "text": "#333333",
    "text_secondary": "#666666",
    "text_light": "#999999",
    "border": "#E0E0E0",
    "border_light": "#F0F0F0",
    "bg": "#FAFAFA",
    "bg_white": "#FFFFFF",
    "bg_hover": "#F5F5F5",
    "bg_card": "#FFFFFF",

    # 日志颜色
    "log_bg": "#263238",
    "log_text": "#CFD8DC",
}

# 统一样式
STYLES = {
    # 主按钮 - 蓝色
    "button_primary": f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_hover']});
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['primary_hover']};
        }}
        QPushButton:pressed {{
            background: {COLORS['primary_dark']};
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 成功按钮 - 绿色
    "button_success": f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['success']}, stop:1 {COLORS['success_hover']});
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['success_hover']};
        }}
        QPushButton:pressed {{
            background: #2E7D32;
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 危险按钮 - 红色
    "button_danger": f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['danger']}, stop:1 {COLORS['danger_hover']});
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['danger_hover']};
        }}
        QPushButton:pressed {{
            background: #B71C1C;
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 次要按钮 - 白色边框
    "button_secondary": f"""
        QPushButton {{
            background: white;
            color: {COLORS['text']};
            border: 2px solid {COLORS['border']};
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['bg_hover']};
            border-color: {COLORS['primary']};
            color: {COLORS['primary']};
        }}
        QPushButton:pressed {{
            background: {COLORS['primary_light']};
        }}
        QPushButton:disabled {{
            background: #F5F5F5;
            color: #BDBDBD;
            border-color: #E0E0E0;
        }}
    """,

    # 小按钮
    "button_small": f"""
        QPushButton {{
            background: {COLORS['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background: {COLORS['primary_hover']};
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 输入框
    "input": f"""
        QLineEdit, QTimeEdit, QSpinBox, QDateTimeEdit {{
            font-size: 14px;
            padding: 10px 12px;
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            background-color: white;
            color: {COLORS['text']};
        }}
        QLineEdit:focus, QTimeEdit:focus, QSpinBox:focus, QDateTimeEdit:focus {{
            border: 2px solid {COLORS['primary']};
            background-color: white;
        }}
        QLineEdit:hover, QTimeEdit:hover, QSpinBox:hover, QDateTimeEdit:hover {{
            border-color: {COLORS['primary_light']};
        }}
    """,

    # 分组框
    "group_box": f"""
        QGroupBox {{
            font-weight: bold;
            font-size: 15px;
            color: {COLORS['text']};
            border: 2px solid {COLORS['border']};
            border-radius: 12px;
            margin-top: 20px;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:1 {COLORS['bg']});
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 10px;
            background-color: white;
        }}
    """,

    # 卡片
    "card": f"""
        QFrame {{
            background-color: white;
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 16px;
        }}
        QFrame:hover {{
            border: 1px solid {COLORS['primary']};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:1 {COLORS['bg']});
        }}
    """,

    # 日志文本框
    "log_text": f"""
        QTextEdit {{
            background-color: {COLORS['log_bg']};
            color: {COLORS['log_text']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            border: none;
            border-radius: 12px;
            padding: 16px;
            selection-background-color: #37474F;
        }}
        QScrollBar:vertical {{
            background: #37474F;
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: #546E7A;
            border-radius: 6px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #607D8B;
        }}
    """,

    # 表格
    "table": f"""
        QTableWidget {{
            background-color: white;
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            gridline-color: {COLORS['border']};
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {COLORS['border']};
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS['primary_light']};
            color: {COLORS['text']};
        }}
        QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_hover']});
            color: white;
            padding: 12px;
            border: none;
            font-weight: bold;
            font-size: 13px;
        }}
        QHeaderView::section:first {{
            border-top-left-radius: 12px;
        }}
        QHeaderView::section:last {{
            border-top-right-radius: 12px;
        }}
    """,

    # 标题
    "title_large": f"""
        QLabel {{
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 16px;
        }}
    """,

    "title_medium": f"""
        QLabel {{
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 12px;
        }}
    """,

    "title_small": f"""
        QLabel {{
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 8px;
        }}
    """,

    # 信息提示框
    "info_box": f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: 13px;
            padding: 16px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary_light']}, stop:1 white);
            border-radius: 10px;
            border-left: 4px solid {COLORS['primary']};
        }}
    """,

    # Tab 样式
    "tab_widget": f"""
        QTabWidget::pane {{
            border: none;
            background-color: {COLORS['bg']};
        }}
        QTabBar::tab {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #E0E0E0, stop:1 #BDBDBD);
            color: {COLORS['text_secondary']};
            padding: 16px 32px;
            margin-right: 4px;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            font-size: 15px;
            font-weight: bold;
            min-width: 140px;
        }}
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:1 {COLORS['bg']});
            color: {COLORS['primary']};
            border-bottom: 3px solid {COLORS['primary']};
        }}
        QTabBar::tab:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #F5F5F5, stop:1 #E0E0E0);
        }}
    """,

    # 复选框
    "checkbox": f"""
        QCheckBox {{
            font-size: 14px;
            color: {COLORS['text']};
            padding: 8px;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {COLORS['border']};
            border-radius: 4px;
            background-color: white;
        }}
        QCheckBox::indicator:hover {{
            border-color: {COLORS['primary']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
        }}
    """,

    # 滚动条
    "scrollbar": f"""
        QScrollBar:vertical {{
            background: {COLORS['bg']};
            width: 14px;
            border-radius: 7px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {COLORS['border']};
            border-radius: 7px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['text_light']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: {COLORS['bg']};
            height: 14px;
            border-radius: 7px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {COLORS['border']};
            border-radius: 7px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {COLORS['text_light']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """,
}


def get_button_style(type="primary", size="normal"):
    """获取按钮样式"""
    if size == "small":
        return STYLES["button_small"]

    style_map = {
        "primary": STYLES["button_primary"],
        "success": STYLES["button_success"],
        "danger": STYLES["button_danger"],
        "secondary": STYLES["button_secondary"],
    }
    return style_map.get(type, STYLES["button_primary"])


def get_shadow_effect():
    """获取阴影效果"""
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    from PyQt5.QtGui import QColor

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setColor(QColor(0, 0, 0, 30))
    shadow.setOffset(0, 4)
    return shadow


# 统一样式
STYLES = {
    # 主按钮
    "button_primary": f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_hover']});
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['primary_hover']};
        }}
        QPushButton:pressed {{
            background: #0D47A1;
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 成功按钮
    "button_success": f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['success']}, stop:1 {COLORS['success_hover']});
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['success_hover']};
        }}
        QPushButton:pressed {{
            background: #2E7D32;
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 危险按钮 - 红色
    "button_danger": f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['danger']}, stop:1 {COLORS['danger_hover']});
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['danger_hover']};
        }}
        QPushButton:pressed {{
            background: #B71C1C;
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 次要按钮
    "button_secondary": f"""
        QPushButton {{
            background: white;
            color: {COLORS['text']};
            border: 2px solid {COLORS['border']};
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background: {COLORS['bg_hover']};
            border-color: {COLORS['primary']};
            color: {COLORS['primary']};
        }}
        QPushButton:pressed {{
            background: {COLORS['primary_light']};
        }}
        QPushButton:disabled {{
            background: #F5F5F5;
            color: #BDBDBD;
            border-color: #E0E0E0;
        }}
    """,

    # 小按钮
    "button_small": f"""
        QPushButton {{
            background: {COLORS['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background: {COLORS['primary_hover']};
        }}
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """,

    # 输入框
    "input": f"""
        QLineEdit, QTimeEdit, QSpinBox, QDateTimeEdit {{
            font-size: 14px;
            padding: 10px 12px;
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            background-color: white;
            color: {COLORS['text']};
        }}
        QLineEdit:focus, QTimeEdit:focus, QSpinBox:focus, QDateTimeEdit:focus {{
            border: 2px solid {COLORS['primary']};
            background-color: white;
        }}
        QLineEdit:hover, QTimeEdit:hover, QSpinBox:hover, QDateTimeEdit:hover {{
            border-color: {COLORS['primary_light']};
        }}
    """,

    # 分组框
    "group_box": f"""
        QGroupBox {{
            font-weight: bold;
            font-size: 15px;
            color: {COLORS['text']};
            border: 2px solid {COLORS['border']};
            border-radius: 12px;
            margin-top: 20px;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:1 {COLORS['bg']});
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 10px;
            background-color: white;
        }}
    """,

    # 卡片
    "card": f"""
        QFrame {{
            background-color: white;
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 16px;
        }}
        QFrame:hover {{
            border: 1px solid {COLORS['primary']};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:1 {COLORS['bg']});
        }}
    """,

    # 日志文本框
    "log_text": f"""
        QTextEdit {{
            background-color: {COLORS['log_bg']};
            color: {COLORS['log_text']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            border: none;
            border-radius: 12px;
            padding: 16px;
            selection-background-color: #37474F;
        }}
        QScrollBar:vertical {{
            background: #37474F;
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: #546E7A;
            border-radius: 6px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #607D8B;
        }}
    """,

    # 表格
    "table": f"""
        QTableWidget {{
            background-color: white;
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            gridline-color: {COLORS['border']};
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {COLORS['border']};
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS['primary_light']};
            color: {COLORS['text']};
        }}
        QHeaderView::section {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_hover']});
            color: white;
            padding: 12px;
            border: none;
            font-weight: bold;
            font-size: 13px;
        }}
        QHeaderView::section:first {{
            border-top-left-radius: 12px;
        }}
        QHeaderView::section:last {{
            border-top-right-radius: 12px;
        }}
    """,

    # 标题
    "title_large": f"""
        QLabel {{
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 16px;
        }}
    """,

    "title_medium": f"""
        QLabel {{
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 12px;
        }}
    """,

    "title_small": f"""
        QLabel {{
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 8px;
        }}
    """,

    # 信息提示框
    "info_box": f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: 13px;
            padding: 16px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary_light']}, stop:1 white);
            border-radius: 10px;
            border-left: 4px solid {COLORS['primary']};
        }}
    """,

    # Tab 样式
    "tab_widget": f"""
        QTabWidget::pane {{
            border: none;
            background-color: {COLORS['bg']};
        }}
        QTabBar::tab {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #E0E0E0, stop:1 #BDBDBD);
            color: {COLORS['text_secondary']};
            padding: 16px 32px;
            margin-right: 4px;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            font-size: 15px;
            font-weight: bold;
            min-width: 140px;
        }}
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 white, stop:1 {COLORS['bg']});
            color: {COLORS['primary']};
            border-bottom: 3px solid {COLORS['primary']};
        }}
        QTabBar::tab:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #F5F5F5, stop:1 #E0E0E0);
        }}
    """,

    # 复选框
    "checkbox": f"""
        QCheckBox {{
            font-size: 14px;
            color: {COLORS['text']};
            padding: 8px;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {COLORS['border']};
            border-radius: 4px;
            background-color: white;
        }}
        QCheckBox::indicator:hover {{
            border-color: {COLORS['primary']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }}
    """,

    # 滚动条
    "scrollbar": f"""
        QScrollBar:vertical {{
            background: {COLORS['bg']};
            width: 14px;
            border-radius: 7px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {COLORS['border']};
            border-radius: 7px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {COLORS['text_light']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: {COLORS['bg']};
            height: 14px;
            border-radius: 7px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background: {COLORS['border']};
            border-radius: 7px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {COLORS['text_light']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """,
}


def get_button_style(type="primary", size="normal"):
    """获取按钮样式"""
    if size == "small":
        return STYLES["button_small"]

    style_map = {
        "primary": STYLES["button_primary"],
        "success": STYLES["button_success"],
        "danger": STYLES["button_danger"],
        "secondary": STYLES["button_secondary"],
    }
    return style_map.get(type, STYLES["button_primary"])


def get_shadow_effect():
    """获取阴影效果"""
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    from PyQt5.QtGui import QColor

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setColor(QColor(0, 0, 0, 30))
    shadow.setOffset(0, 4)
    return shadow
