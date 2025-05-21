from PyQt5.QtWidgets import QApplication, QLayout, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QFont, QColor ,QPainter,QPixmap,QMovie, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os
import time
import json

def safe_read_file(path, retries=3, delay=0.2):
    for attempt in range(retries):
        try:
            with open(path, "r", encoding='utf-8') as file:
                return file.read()
        except PermissionError:
            print(f"[Warning] File is busy. Retrying in {delay} sec...")
            time.sleep(delay)
    return None

env_vars = dotenv_values("Voice-Assistant/.env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\\Voice-Assistant\\frontend\\Files"
GraphicsDirPath = rf"{current_dir}\\Voice-Assistant\\frontend\\Graphics"
os.makedirs(TempDirPath, exist_ok=True)
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what’s", "where’s", "how’s"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1]
        else:
            new_query += "?"

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf"{TempDirPath}\\Mic.data", "w", encoding="utf-8") as file:
        file.write(Command)
def GetMicrophoneStatus():
    with open(rf"{TempDirPath}\\Mic.data", "r", encoding="utf-8") as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf"{TempDirPath}\Status.data", "r", encoding="utf-8") as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("True")

def MicButtonClosed():
    SetMicrophoneStatus("False")

def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path

def TempDirectoryPath(Filename):
    Path = rf'{TempDirPath}\{Filename}'
    return Path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding="utf-8") as file:
        file.write(Text)
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction) # NO TEXT INTERACTION
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Policy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath("P.gif"))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        self.toggled=True
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }
            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
                           }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            """)

    def loadMessages(self):

        global old_chat_message
        path = TempDirectoryPath("Responses.data")
        messages = safe_read_file(path)

        if messages and len(messages) > 1 and str(messages) != str(old_chat_message):
            self.addMessage(messages, "White")
            old_chat_message = messages
        # with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
        #     messages = file.read()

        #     if None == messages:
        #         pass
        #     elif len(messages) <= 1:
        #         pass
        #     elif str(old_chat_message) == str(messages):
        #         pass
        #     else:
        #         self.addMessage(messages, "White")
        #         old_chat_message = messages
    # def SpeechRecogText(self):
    #     with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
    #         messages = file.read()
    #         self.label.setText(messages)
    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except PermissionError:
            self.label.setText("⚠️ Cannot read file: Permission denied.")
        except FileNotFoundError:
            self.label.setText("❌ Status file not found.")
        except Exception as e:
            self.label.setText(f"⚠️ Unexpected error: {e}")

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("voice.png"),60,60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath("mic.png"), 60,60)
            MicButtonClosed()
        self.toggled = not self.toggled
    
    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format =QTextCharFormat()
        # format.setTopMargin(10)
        # format.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setCharFormat(format)
        cursor.insertText(message +"\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('P.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel()
        icon_path = GraphicsDirectoryPath("Mic_on.png")
        # print("Icon Path:", icon_path)
        # print("Exists:", os.path.exists(icon_path))
        pixmap = QPixmap(icon_path)
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom: 0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
                return
        except PermissionError:
            time.sleep(0.2)
    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("**")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget
        

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)

        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black;")

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height: 40px; line-height: 40px; background-color: white; color: black;")

        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color: white;")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png')) # Typo in image path, assuming 'Minimize.png' is intended for restore
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color: white;")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color: white;")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")

        title_label = QLabel(f"{str(Assistantname).capitalize()} AI   ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color: white;")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)
    def closeWindow(self):
        try:
            os.remove('Voice-Assistant/Data/ChatLog.json')
        except FileNotFoundError:
            pass
    
        
        self.parent().close()


    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
            self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
             layout.addWidget(initial_screen)
        self.current_screen = initial_screen
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
       
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        self.stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen(self)
        message_screen = MessageScreen(self)
        self.stacked_widget.addWidget(initial_screen)
        self.stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        self.top_bar= CustomTopBar(self, self.stacked_widget)
        # main_layout = QVBoxLayout()
        # main_layout.setContentsMargins(0,0,0,0)
        # main_layout.setSpacing(0)
        # main_layout.addWidget(top_bar)
        # main_layout.addWidget(self.stacked_widget)
        self.setMenuWidget(self.top_bar)
        self.setCentralWidget(self.stacked_widget)
    #  def __init__(self):
    #     super().__init__()
    #     self.setWindowTitle("Voice Assistant")
    #     self.setGeometry(100, 100, 1280, 720)
        
    #     central_widget = QWidget()
    #     self.setCentralWidget(central_widget)

    #     layout = QVBoxLayout(central_widget)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #     layout.setSpacing(0)

    #     self.stacked_widget = QStackedWidget()
    #     self.initial_screen = InitialScreen()
    #     self.message_screen = MessageScreen()

    #     self.stacked_widget.addWidget(self.initial_screen)
    #     self.stacked_widget.addWidget(self.message_screen)

    #     self.top_bar = CustomTopBar(self, self.stacked_widget)
    #     layout.addWidget(self.top_bar)                # Add top bar at the top
    #     layout.addWidget(self.stacked_widget)         # Then add the stacked widget below it

    #     # Optional: show a default screen
    #     self.stacked_widget.setCurrentWidget(self.initial_screen)

def GraphicalUserInterface():
   
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
   GraphicalUserInterface()
    


   
                           
        