from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLineEdit, QApplication, QScrollArea, QSizePolicy, QGridLayout, QPushButton, QTextEdit, QLabel, QSystemTrayIcon, QMenu, QLayout
from PyQt6.QtGui import QRegularExpressionValidator, QFontDatabase, QCursor, QIcon, QAction
from PyQt6.QtCore import Qt, QRegularExpression, QEvent, QPointF
from Dict import Dict
import json
import sys
import os
import platform
from datetime import datetime
from CustomTitleBar import CustomTitleBar

reference_dict = Dict()
data = {}
current_date = datetime.now().strftime('%d-%m-%Y')
new_window = None
replace_dictionary = {
    '--dm-border': 'white',
    '--dm-button-default': 'rgb(22, 14, 70)',
    '--dm-button-hover': 'rgb(39, 30, 90)',
    '--dm-button-pressed': 'rgb(59, 48, 124)',
    '--dm-text': 'white',
    '--lm-border': 'rgb(31, 11, 0)',
    '--lm-button-default': 'rgb(252, 229, 189)',
    '--lm-button-hover': 'rgb(255, 237, 207)',
    '--lm-button-pressed': 'rgb(255, 240, 214)',
    '--lm-text': 'rgb(31, 11, 0)'
}
theme = ''
basedir = os.path.dirname(__file__)
API_KEY = os.environ["api_key"]
print(API_KEY)

try:
    from ctypes import windll
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

with open(os.path.join(basedir, 'settings.json'), 'r') as file:
    file_data = json.load(file)
theme = file_data['theme']

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Word Logger')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resizing = False
        self.margin = 10
        self._cursor = QCursor()
        self.resetPosition()
        self.setMouseTracking(True)

        self.input = QLineEdit(parent=self)
        self.input.setProperty('class', 'transparent-styling')
        input_validator = QRegularExpressionValidator(QRegularExpression('[A-Za-z]+'), self.input)

        self.input.setPlaceholderText('Enter word here.')
        self.input.returnPressed.connect(self.return_pressed)
        self.input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input.setValidator(input_validator)

        self.definition = QTextEdit()
        self.definition.setReadOnly(True)
        self.definition.setHtml('<b>Hello<b>')
        self.definition.setProperty('class', 'text-edit')

        self.grid_layout = QGridLayout()
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(1, 0)

        self.read_json()

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setProperty('class', 'transparent-styling')
        scroll_widget.setProperty('class', 'no-border-styling')

        scroll_widget.setLayout(self.grid_layout)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(300)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        self.title_bar = CustomTitleBar(self)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.input)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.definition)

        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(5, 5, 5, 5)
        central_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        central_layout.addWidget(self.title_bar)
        central_layout.addLayout(main_layout)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(central_layout)
        self.central_widget.setMouseTracking(True)
        self.central_widget.setObjectName('central-widget')
        self.central_widget.setStyleSheet("""#central-widget {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #051c2a stop:1 #44315f);
            border: 1px solid white;
            border-radius: 5px;
        }""")

        if theme == 'light':
            self.title_bar.set_title_bar_light_theme()
            self.set_light_theme()
        elif theme == 'dark':
            self.title_bar.set_title_bar_dark_theme()
            self.set_dark_theme()
        
        self.setCentralWidget(self.central_widget)
    
    def read_json(self):
        global data
        with open(os.path.join(basedir, 'data.json'), 'r') as f:
            try:
               data = json.load(f)
            except Exception as e:
                print('Error:', e)
        
        last_date = 0
        row = 0
        for key in reversed(data.keys()):
            entry_date = data[key]['entry_date']

            if last_date != entry_date:
                label = QLabel(entry_date)
                label.setProperty('class', 'label')
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.grid_layout.addWidget(label, row, 0, 1, 2)

                last_date = entry_date
                row += 1
            
            definition = data[key]['def']
            text_button, delete_button = self.create_row_buttons(key)
            self.grid_layout.addWidget(text_button, row, 0)
            self.grid_layout.addWidget(delete_button, row, 1)

            row += 1
    
    def create_row_buttons(self, entry):
        text_button = QPushButton(entry)
        text_button.setMinimumSize(100, 50)
        text_button.clicked.connect(lambda: self.show_definition('<hr>'.join(data[entry]['def'])))
        
        delete_button = QPushButton()
        delete_button.setProperty('isFlat', True)
        delete_button.setMinimumSize(50, 50)
        delete_button.clicked.connect(lambda: self.delete_entry(entry))

        return (text_button, delete_button)

    def insert_widget(self, widget, target_row, rowSpan=1, colSpan=1):
        for i in range((self.grid_layout.rowCount() - 1), target_row - 1, -1):
            moved_widget_left = self.grid_layout.itemAtPosition(i, 0).widget()
            moved_widget_right = self.grid_layout.itemAtPosition(i, 1).widget()

            if isinstance(moved_widget_left, QLabel):
                self.grid_layout.removeWidget(moved_widget_left)
                self.grid_layout.addWidget(moved_widget_left, i + 1, 0, 1, 2)
                continue
            
            self.grid_layout.removeWidget(moved_widget_left)
            self.grid_layout.removeWidget(moved_widget_right)
            self.grid_layout.addWidget(moved_widget_left, i + 1, 0)
            self.grid_layout.addWidget(moved_widget_right, i + 1, 1)

        self.grid_layout.addWidget(widget, target_row, 0, rowSpan, colSpan)

    def return_pressed(self):
        entry = self.input.text()
        self.input.setText('')
        

        if entry in data:
            self.show_definition('Word already in entries!')
        else:
            result = reference_dict.get_definition(entry)
            
            if result != None:
                data[entry] = dict()
                data[entry]['def'] = result
                data[entry]['entry_date'] = current_date
                
                text_button, delete_button = self.create_row_buttons(entry)

                if self.grid_layout.count() != 0:

                    if (isinstance(top_widget := self.grid_layout.itemAtPosition(0, 0).widget(), QLabel)):
                        if (current_date != top_widget.text()):
                            label = QLabel(current_date)
                            label.setProperty('class', 'label')
                            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.insert_widget(label, 0, 1, 2)

                        self.insert_widget(text_button, 1)
                        self.grid_layout.addWidget(delete_button, 1, 1)
                        self.show_definition('<hr>'.join(result))
                    else:
                        self.insert_widget(text_button, 0)
                        self.grid_layout.addWidget(delete_button, 0, 1)
                        self.show_definition('<hr>'.join(result))
                        
                else:
                    label = QLabel(current_date)
                    label.setProperty('class', 'label')
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.grid_layout.addWidget(label, 0, 0, 1, 2)

                    self.grid_layout.addWidget(text_button, 1, 0)
                    self.grid_layout.addWidget(delete_button, 1, 1)
            else:
                self.show_definition('No definition found!')
    
    def show_definition(self, definition):
        self.definition.setHtml(definition)
    
    def delete_entry(self, entry):
        global data

        button = self.sender()
        idx = self.grid_layout.indexOf(button)
        location = self.grid_layout.getItemPosition(idx)
        text_button = self.grid_layout.itemAtPosition(location[0], 0).widget()

        self.grid_layout.removeWidget(text_button)
        self.sender().setParent(None)

        del data[entry]

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.window_state_changed(self.windowState())
        super().changeEvent(event)
        event.accept()
    
    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)
        reference_dict.process_entries(data)
        self.update_theme()
        print('Entries processed!')

    def setCursorShape(self, pos):
        pos = QPointF.toPoint(pos)
        self.margin = 3
        if self.isMaximized() or self.isFullScreen():
            pass
        else:
            rect = self.rect()
            rect.setX(self.rect().x() + self.margin)
            rect.setY(self.rect().y() + self.margin)
            rect.setWidth(self.rect().width() - (self.margin * 2))
            rect.setHeight(self.rect().height() - (self.margin * 2))

            self.resizing = rect.contains(pos, proper=True)

            if self.resizing:
                self.unsetCursor()
                self.resetPosition()
                self._cursor = self.cursor()
            else:
                x = pos.x()
                y = pos.y()

                x1 = self.rect().x()
                y1 = self.rect().y()
                x2 = self.rect().width()
                y2 = self.rect().height()

                self.left = (abs(x - x1) <= self.margin)
                self.top = (abs(y - y1) <= self.margin)
                self.right = (abs(x - (x2 + y1)) <= self.margin)
                self.bottom = (abs(y - (y2 + x1)) <= self.margin)

                if self.top and self.left:
                    self._cursor.setShape(Qt.CursorShape.SizeFDiagCursor)
                elif self.top and self.right:
                    self._cursor.setShape(Qt.CursorShape.SizeBDiagCursor)
                elif self.bottom and self.left:
                    self._cursor.setShape(Qt.CursorShape.SizeBDiagCursor)
                elif self.bottom and self.right:
                    self._cursor.setShape(Qt.CursorShape.SizeFDiagCursor)
                elif self.left:
                    self._cursor.setShape(Qt.CursorShape.SizeHorCursor)
                elif self.top:
                    self._cursor.setShape(Qt.CursorShape.SizeVerCursor)
                elif self.right:
                    self._cursor.setShape(Qt.CursorShape.SizeHorCursor)
                elif self.bottom:
                    self._cursor.setShape(Qt.CursorShape.SizeVerCursor)
                self.setCursor(self._cursor)
            
            self.resizing = not self.resizing

    def resetPosition(self):
        self.top = False
        self.bottom = False
        self.left = False
        self.right = False

    def mouseMoveEvent(self, event):
        self.setCursorShape(event.position())
        return super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.resizing:
                self._resize()
        return super().mousePressEvent(event)

    def _resize(self):
        window = self.window().windowHandle()
        if self._cursor.shape() == Qt.CursorShape.SizeHorCursor:
            if self.left:
                window.startSystemResize(Qt.Edge.LeftEdge)
            elif self.right:
                window.startSystemResize(Qt.Edge.RightEdge)
        if self._cursor.shape() == Qt.CursorShape.SizeVerCursor:
            if self.top:
                window.startSystemResize(Qt.Edge.TopEdge)
            elif self.bottom:
                window.startSystemResize(Qt.Edge.BottomEdge)
        if self._cursor.shape() == Qt.CursorShape.SizeBDiagCursor:
            if self.top and self.right:
                window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.RightEdge)
            elif self.bottom and self.left:
                window.startSystemResize(Qt.Edge.BottomEdge | Qt.Edge.LeftEdge)
        if self._cursor.shape() == Qt.CursorShape.SizeFDiagCursor:
            if self.top and self.left:
                window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.LeftEdge)
            elif self.bottom and self.right:
                window.startSystemResize(Qt.Edge.BottomEdge | Qt.Edge.RightEdge)

    def set_light_theme(self):
        set_light_mode()
        self.title_bar.set_title_bar_light_theme()
        self.central_widget.setStyleSheet("""#central-widget {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 rgb(255, 248, 219) stop:1 rgb(255, 234, 201));
            border: 1px solid rgb(31, 11, 0);
            border-radius: 5px;
        }""")
    
    def set_dark_theme(self):
        set_dark_mode()
        self.title_bar.set_title_bar_dark_theme()
        self.central_widget.setStyleSheet("""#central-widget {
            background: qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #051c2a stop:1 #44315f);
            border: 1px solid white;
            border-radius: 5px;
        }""")
    
    def update_theme(self):
        with open(os.path.join(basedir, 'settings.json'), 'w') as file:
            json.dump({"theme": theme}, file)

class InputWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(' ')
        self.setContentsMargins(0, 0, 0, 0)

        self.input = QLineEdit(parent=self)
        self.input.setProperty('class', 'transparent-styling')
        input_validator = QRegularExpressionValidator(QRegularExpression('[A-Za-z]+'), self.input)

        self.title_bar = CustomTitleBar(self)
        self.title_bar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.input.setPlaceholderText('Enter word here.')
        self.input.returnPressed.connect(self.return_pressed)
        self.input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.input.setValidator(input_validator)

        self.definition = QLabel()
        self.definition.setWordWrap(True)
        self.definition.setTextFormat(Qt.TextFormat.RichText)
        self.definition.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.definition.setProperty('class', 'label')

        layout = QVBoxLayout()
        layout.addWidget(self.title_bar)
        layout.addWidget(self.input)
        layout.addWidget(self.definition)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        container_widget.setProperty('class', 'input-container')
        container_layout = QVBoxLayout()
        container_layout.addWidget(container_widget)

        if theme == 'light':
            self.title_bar.set_title_bar_light_theme_window()
        elif theme == 'dark':
            self.title_bar.set_title_bar_dark_theme_window()

        self.setLayout(container_layout)
    
    def return_pressed(self):
        # 278, 269
        entry = self.input.text()
        self.input.setText('')
    
        if entry in data:
            self.show_definition('Word already in entries!')
        else:
            result = reference_dict.get_definition(entry)
            
            if result != None:
                data[entry] = dict()
                data[entry]['def'] = result
                data[entry]['entry_date'] = current_date

                result = '<hr>'.join(result)

                self.show_definition(result)
            else:
                self.show_definition('No definition found!')
        
        print('Entry submitted!')
    
    def show_definition(self, definition):
        self.definition.setText(definition)
    
    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)
        reference_dict.process_entries(data)
        print('Entries processed!')

def create_new_window():
    global new_window
    if new_window == None:
        new_window = InputWindow()
    new_window.show()

def import_css(link):
    with open(link, 'r') as file:
        file_data = file.read()
    
    for key, value in replace_dictionary.items():
        file_data = file_data.replace(key, value)
        
    return file_data

def set_light_mode():
    global theme
    
    css = import_css(os.path.join(basedir, 'light-mode.css'))
    theme = 'light'
    app.setStyleSheet(css)
    
def set_dark_mode():
    global theme

    css = import_css(os.path.join(basedir, 'dark-mode.css'))
    theme = 'dark'
    app.setStyleSheet(css)

def read_theme():
    with open(os.path.join(basedir, 'settings.json'), 'r') as file:
        file_data = json.load(file)
    
    theme = file_data['theme']

    if theme == 'dark':
        return os.path.join(basedir, 'dark-mode.css')
    elif theme == 'light':
        return os.path.join(basedir, 'light-mode.css')

def main():
    global app

    if (platform.system() == 'Windows') or (platform.system() == 'Linux'):
        css_file = ''
        font_regular = os.path.join(basedir, 'assets', 'DM_Mono/DMMono-Regular.ttf')
        font_medium = os.path.join(basedir, 'assets', 'DM_Mono/DMMono-Medium.ttf')
    elif platform.system() == 'Darwin':
        css_file = ''
        font_regular = ''
        font_medium = ''

    app = QApplication(sys.argv)

    dm_mono_regular = QFontDatabase.addApplicationFont(font_regular)
    dm_mono_medium = QFontDatabase.addApplicationFont(font_medium)

    css_file = read_theme()
    css = import_css(css_file)
    app.setStyleSheet(css)
    
    tray = QSystemTrayIcon()
    tray_icon = QIcon(os.path.join(basedir, 'assets', 'enter.svg'))
    tray.setIcon(tray_icon)
    tray.setVisible(True)
    menu = QMenu()

    create_window = QAction('Input new word')
    create_window.setIcon(QIcon())
    create_window.triggered.connect(create_new_window)
    menu.addAction(create_window)

    quit_action = QAction('Quit app')
    quit_action.setIcon(QIcon())
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    menu.setStyleSheet("QMenu::item { padding: 2px 5px 2px 2px;} QMenu::item:selected { background-color: rgb(0, 85, 127); color: rgb(255, 255, 255); }")

    tray.setContextMenu(menu)
    app.setWindowIcon(QIcon(os.path.join(basedir, 'assets', 'enter.png')))

    window = MainWindow()
    window.show()
    app.setQuitOnLastWindowClosed(False)
    app.exec()

if __name__ == '__main__':
    try:
        main()
        print('Closed!')
    except KeyboardInterrupt:
        print('Interrupted!')