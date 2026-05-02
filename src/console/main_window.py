import os
import sys

# Fix for Qt platform plugin not found
try:
    import PySide6
    pyside6_dir = os.path.dirname(PySide6.__file__)
    plugin_path = os.path.join(pyside6_dir, 'plugins', 'platforms')
    if os.path.exists(plugin_path):
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
except ImportError:
    pass

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QSystemTrayIcon, QMenu, QDialog, QSlider,
    QApplication, QFrame
)
from PySide6.QtCore import Qt, QTimer, QSize, QPoint
from PySide6.QtGui import QIcon, QAction, QColor, QFont

from src.animation.animator import Animator
from src.games.manager import GameManager
from src.games.snake import SnakeGame
from src.games.pong import PongGame

class SettingsDialog(QDialog):
    def __init__(self, parent=None, animator=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)
        self.animator = animator
        
        layout = QVBoxLayout()
        
        # Pixel Scale
        layout.addWidget(QLabel("Pixel Scale:"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(2, 32)
        self.scale_slider.setValue(self.animator.pixel_size if self.animator else 8)
        self.scale_slider.valueChanged.connect(self.update_scale)
        layout.addWidget(self.scale_slider)
        
        self.scale_label = QLabel(f"Current: {self.scale_slider.value()}px")
        layout.addWidget(self.scale_label)
        
        # Close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    def update_scale(self, value):
        self.scale_label.setText(f"Current: {value}px")
        if self.animator:
            self.animator.pixel_size = value

class RetroConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WinArt Retro Console")
        self.setFixedSize(300, 450)
        
        # Remove title bar and borders for a cleaner "app" feel
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Setup Backend
        self.animator = Animator(pool_size=2000, pixel_size=8)
        self.animator.engine.set_transparency(True)
        self.manager = GameManager(self.animator)
        
        # Register Games
        self.manager.register_game(SnakeGame())
        self.manager.register_game(PongGame())
        
        # UI Setup
        self.setup_ui()
        self.setup_tray()
        
        # Timer for Game Updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.manager.update)
        self.timer.start(16) # ~60 FPS update logic
        
        # Dock to bottom-right
        self.dock_to_bottom_right()
        
        self.old_pos = None

    def setup_ui(self):
        # Central widget with styling
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainFrame")
        self.central_widget.setStyleSheet("""
            #mainFrame {
                background-color: rgba(30, 30, 35, 230);
                border: 2px solid #00ff00;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
            QLabel { color: #00ff00; font-family: 'Consolas'; font-size: 14px; }
            QPushButton { 
                background-color: #222; border: 1px solid #00ff00; color: #00ff00; 
                padding: 5px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #333; }
            QListWidget { background-color: #111; color: #00ff00; border: 1px solid #444; }
            #titleBar { background-color: #00ff00; color: #000; font-weight: bold; padding: 2px; }
        """)
        
        layout = QVBoxLayout(self.central_widget)
        
        # Drag Handle / Title
        title_label = QLabel(" WINART CONSOLE ")
        title_label.setObjectName("titleBar")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Game List
        layout.addWidget(QLabel("Available Games:"))
        self.game_list = QListWidget()
        for game_name in self.manager.games.keys():
            self.game_list.addItem(game_name)
        layout.addWidget(self.game_list)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        self.play_btn = QPushButton("PLAY")
        self.play_btn.clicked.connect(self.start_selected_game)
        ctrl_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.clicked.connect(self.stop_game)
        ctrl_layout.addWidget(self.stop_btn)
        layout.addLayout(ctrl_layout)
        
        # Extra Options
        opt_layout = QHBoxLayout()
        settings_btn = QPushButton("SETTINGS")
        settings_btn.clicked.connect(self.show_settings)
        opt_layout.addWidget(settings_btn)
        
        exit_btn = QPushButton("EXIT")
        exit_btn.clicked.connect(self.close_app)
        opt_layout.addWidget(exit_btn)
        layout.addLayout(opt_layout)
        
        self.setCentralWidget(self.central_widget)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # Use a dummy icon if no icon file exists
        self.tray_icon.setIcon(QIcon.fromTheme("games-highscores")) 
        
        menu = QMenu()
        show_action = QAction("Show Console", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def dock_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - self.width() - 20, 
                  screen.height() - self.height() - 40) # Slightly above taskbar

    def start_selected_game(self):
        selected = self.game_list.currentItem()
        if selected:
            self.manager.start_game(selected.text())

    def stop_game(self):
        self.manager.stop_game()

    def show_settings(self):
        dialog = SettingsDialog(self, self.animator)
        dialog.exec()

    def close_app(self):
        self.manager.stop_game()
        self.animator.engine.close()
        QApplication.quit()

    # Enable window dragging for "freedom"
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    console = RetroConsole()
    console.show()
    sys.exit(app.exec())
