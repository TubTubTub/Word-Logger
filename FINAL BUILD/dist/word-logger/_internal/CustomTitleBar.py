from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QHBoxLayout, QToolButton, QGraphicsOpacityEffect
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
import os

basedir = os.path.dirname(__file__)

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initial_pos = None
        self.original_size = None

        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(1, 1, 1, 1)
        title_bar_layout.setSpacing(2)

        self.title = QLabel(f'{self.__class__.__name__}', self)
        self.title.setStyleSheet("""
            margin: 2px;
            margin-left: 48px;
            font-family: 'DM Mono';
            font-size: 10pt;
            font-weight: bold;
            color: white;
        """)
        # op = QGraphicsOpacityEffect()
        # op.setOpacity(1)
        
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if (title := parent.windowTitle()):
            self.title.setText(title)
        
        self.min_button = QToolButton(self)
        min_icon = QIcon()
        min_icon.addFile(os.path.join(basedir, 'assets', 'min_white.svg'))
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        self.max_button = QToolButton(self)
        # self.max_button.setGraphicsEffect(op)
        max_icon = QIcon()
        max_icon.addFile(os.path.join(basedir, 'assets', 'max_white.svg'))
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(lambda: self.max_button_clicked())

        self.close_button = QToolButton()
        # self.close_button.setGraphicsEffect(op)
        close_icon = QIcon()
        close_icon.addFile(os.path.join(basedir, 'assets', 'close_white.svg'))
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        self.normal_button = QToolButton(self)
        normal_icon = QIcon()
        normal_icon.addFile(os.path.join(basedir, 'assets', 'max_white.svg'))
        self.normal_button.setIcon(normal_icon)
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)

        if isinstance(self.window(), QMainWindow):
            self.switch_theme_button = QToolButton(self)
            self.switch_theme_button.setCheckable(True)
            moon_icon = QIcon()
            moon_icon.addFile(os.path.join(basedir, 'assets', 'moon.svg'))
            self.switch_theme_button.setIcon(moon_icon)
            self.switch_theme_button.clicked.connect(self.switch_theme)

            self.switch_theme_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.switch_theme_button.setFixedSize(QSize(20, 20))
            self.switch_theme_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 2px;
                border: 1px solid rgba(231, 231, 231, 0.5);
                border-radius: 2px;
            }
            QToolButton:hover {
                border-color: white;
                background-color: rgba(201, 201, 201, 0.5);          
            }
            QToolButton:pressed {
                background-color: rgba(201, 201, 201, 0.75);    
            }                                 
            """)

            title_bar_layout.addWidget(self.switch_theme_button)
            
        title_bar_layout.addWidget(self.title)
        buttons = [self.min_button, self.normal_button, self.max_button, self.close_button]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(20, 20))
            button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 2px;
            }
            """)
            title_bar_layout.addWidget(button)

    def max_button_clicked(self):
        self.original_size = self.window().size()
        self.window().showMaximized()

    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)

    def mousePressEvent(self, event):
        global_coords = self.mapToGlobal(event.position().toPoint())

        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = global_coords

        super().mousePressEvent(event)
        event.accept()
    
    def mouseMoveEvent(self, event):
        current_coords = self.mapToGlobal(event.position().toPoint())

        if self.initial_pos is not None:
            if self.window().isMaximized():
                self.window().setGeometry(current_coords.x() - int(self.original_size.width() / 2), current_coords.y(), self.original_size.width(), self.original_size.height())
                self.initial_pos = current_coords
                self.window_state_changed(self.window().windowState())

            delta = current_coords - self.initial_pos
            self.window().move(self.window().x() + delta.x(), self.window().y() + delta.y())
            self.initial_pos = current_coords

        super().mouseMoveEvent(event)
        event.accept()
        
    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        super().mouseReleaseEvent(event)
        event.accept()
    
    def set_title_bar_light_theme(self):
        dark_min = QIcon()
        dark_min.addFile(os.path.join(basedir, 'assets', 'min_black.svg'))
        dark_max = QIcon()
        dark_max.addFile(os.path.join(basedir, 'assets', 'max_black.svg'))
        dark_close = QIcon()
        dark_close.addFile(os.path.join(basedir, 'assets', 'close_black.svg'))
        self.min_button.setIcon(dark_min)
        self.max_button.setIcon(dark_max)
        self.close_button.setIcon(dark_close)
    
        sun_icon = QIcon()
        sun_icon.addFile(os.path.join(basedir, 'assets', 'sun.svg'))
        self.switch_theme_button.setIcon(sun_icon)
        self.switch_theme_button.setStyleSheet("""
        QToolButton {
            border: none;
            padding: 2px;
            border: 1px solid rgba(0, 0, 0, 0.5);
            border-radius: 2px;
        }
        QToolButton:hover {
            border-color: rgb(31, 11, 0);
            background-color: rgba(255, 204, 120, 0.5);          
        }
        QToolButton:pressed {
            background-color: rgba(255, 204, 120, 0.75);    
        }                                 
        """)
        self.title.setStyleSheet("""
            margin: 2px;
            margin-left: 48px;
            font-family: 'DM Mono';
            font-size: 10pt;
            font-weight: bold;
            color: rgb(31, 11, 0);
        """)

    def set_title_bar_dark_theme(self):
        light_min = QIcon()
        light_min.addFile(os.path.join(basedir, 'assets', 'min_white.svg'))
        light_max = QIcon()
        light_max.addFile(os.path.join(basedir, 'assets', 'max_white.svg'))
        light_close = QIcon()
        light_close.addFile(os.path.join(basedir, 'assets', 'close_white.svg'))
        self.min_button.setIcon(light_min)
        self.max_button.setIcon(light_max)
        self.close_button.setIcon(light_close)

        moon_icon = QIcon()
        moon_icon.addFile(os.path.join(basedir, 'assets', 'moon.svg'))
        self.switch_theme_button.setIcon(moon_icon)
        self.switch_theme_button.setStyleSheet("""
        QToolButton {
            border: none;
            padding: 2px;
            border: 1px solid rgba(231, 231, 231, 0.5);
            border-radius: 2px;
        }
        QToolButton:hover {
            border-color: white;
            background-color: rgba(201, 201, 201, 0.5);          
        }
        QToolButton:pressed {
            background-color: rgba(201, 201, 201, 0.75);    
        }                                 
        """)
        self.title.setStyleSheet("""
            margin: 2px;
            margin-left: 48px;
            font-family: 'DM Mono';
            font-size: 10pt;
            font-weight: bold;
            color: white;
        """)

    def set_title_bar_light_theme_window(self):
        dark_min = QIcon()
        dark_min.addFile(os.path.join(basedir, 'assets', 'min_black.svg'))
        dark_max = QIcon()
        dark_max.addFile(os.path.join(basedir, 'assets', 'max_black.svg'))
        dark_close = QIcon()
        dark_close.addFile(os.path.join(basedir, 'assets', 'close_black.svg'))
        self.min_button.setIcon(dark_min)
        self.max_button.setIcon(dark_max)
        self.close_button.setIcon(dark_close)
    
        self.title.setStyleSheet("""
            margin: 2px;
            margin-left: 48px;
            font-family: 'DM Mono';
            font-size: 10pt;
            font-weight: bold;
            color: rgb(31, 11, 0);
        """)

    def set_title_bar_dark_theme_window(self):
        light_min = QIcon()
        light_min.addFile(os.path.join(basedir, 'assets', 'min_white.svg'))
        light_max = QIcon()
        light_max.addFile(os.path.join(basedir, 'assets', 'max_white.svg'))
        light_close = QIcon()
        light_close.addFile(os.path.join(basedir, 'assets', 'close_white.svg'))
        self.min_button.setIcon(light_min)
        self.max_button.setIcon(light_max)
        self.close_button.setIcon(light_close)

        self.title.setStyleSheet("""
            margin: 2px;
            margin-left: 48px;
            font-family: 'DM Mono';
            font-size: 10pt;
            font-weight: bold;
            color: white;
        """)

    def switch_theme(self, checked):
        if checked == True:
            self.window().set_light_theme()
        else:
            self.window().set_dark_theme()