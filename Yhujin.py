import sys, os, json, zipfile, io, requests, psutil, winreg, subprocess, time, shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, 
                             QProgressBar, QLabel, QListWidget, QListWidgetItem, QGroupBox, QGridLayout, 
                             QSpinBox, QCheckBox, QFrame, QStatusBar, QSizePolicy, QComboBox, QAbstractItemView,
                             QStackedWidget, QScrollArea, QTabBar, QDialog, QToolButton, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QMutex, QMutexLocker, QRect, QPoint, QSize, QUrl
from PyQt6.QtGui import QFont, QColor, QPainter, QMouseEvent, QDesktopServices, QPixmap, QLinearGradient

BG_DARK = "#0a0a0a"
BG_MEDIUM = "#111111"
BG_LIGHT = "#1a1a1a"
BORDER = "#333333"
BORDER_HOVER = "#555555"
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#888888"
TEXT_MUTED = "#666666"
ACCENT = "#ffffff"
ACCENT_HOVER = "#cccccc"
BTN_BG = "#222222"
BTN_HOVER = "#333333"
BTN_DISABLED = "#1a1a1a"
RED = "#ff4444"
RED_HOVER = "#ff6666"
GREEN = "#44ff44"
INPUT_BG = "#151515"
INPUT_BORDER = "#333333"
INPUT_FOCUS = "#555555"
CARD_BG = "#151515"
CARD_HOVER = "#1f1f1f"
SIDEBAR_BG = "#0d0d0d"
TOPBAR_BG = "#0d0d0d"
PROGRESS_BG = "#222222"
PROGRESS_CHUNK = "#ffffff"

class DiscordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YHUJIN CLIENT")
        self.setFixedSize(350, 200)
        self.setStyleSheet(f"""
            QDialog {{
                background: {BG_DARK};
                border: 1px solid {BORDER};
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
            }}
            QLabel#small {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Welcome to YHUJIN CLIENT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {TEXT_PRIMARY};")
        layout.addWidget(title)
        
        desc = QLabel("Visit our website for more information:")
        desc.setObjectName("small")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        link = QLabel("yhujinism.vercel.app")
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background: {BG_LIGHT};
                border: 1px solid {BORDER};
                border-radius: 4px;
            }}
            QLabel:hover {{
                background: {BG_MEDIUM};
                border-color: {TEXT_PRIMARY};
            }}
        """)
        link.setCursor(Qt.CursorShape.PointingHandCursor)
        link.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl("https://yhujinism.vercel.app/"))
        layout.addWidget(link)
        
        button_layout = QHBoxLayout()
        
        visit_btn = QPushButton("Visit Now")
        visit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {TEXT_PRIMARY};
                border: none;
                color: {BG_DARK};
                font-size: 12px;
                font-weight: 600;
                padding: 8px 20px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {ACCENT_HOVER};
            }}
        """)
        visit_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://yhujinism.vercel.app/")))
        button_layout.addWidget(visit_btn)
        
        later_btn = QPushButton("Later")
        later_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {BORDER};
                color: {TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
                padding: 8px 20px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {BG_LIGHT};
                border-color: {BORDER_HOVER};
                color: {TEXT_PRIMARY};
            }}
        """)
        later_btn.clicked.connect(self.accept)
        button_layout.addWidget(later_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

class ActionButton(QPushButton):
    def __init__(self, text="", parent=None, primary=False):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(28)
        if primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {TEXT_PRIMARY};
                    border: none;
                    color: {BG_DARK};
                    font-size: 11px;
                    font-weight: 600;
                    padding: 0 12px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background: {ACCENT_HOVER};
                }}
                QPushButton:pressed {{
                    background: #999999;
                }}
                QPushButton:disabled {{ background: {BTN_DISABLED}; color: {TEXT_MUTED}; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {BORDER};
                    color: {TEXT_SECONDARY};
                    font-size: 11px;
                    font-weight: 500;
                    padding: 0 12px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{ background: {BTN_HOVER}; border-color: {BORDER_HOVER}; color: {TEXT_PRIMARY}; }}
                QPushButton:pressed {{ background: {BG_LIGHT}; }}
                QPushButton:disabled {{ background: {BTN_DISABLED}; color: {TEXT_MUTED}; border-color: #222; }}
            """)

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 0 16px;
                background: transparent;
                border: none;
                color: {TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {BG_LIGHT};
                color: {TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                background: {BG_LIGHT};
                color: {TEXT_PRIMARY};
                border-left: 3px solid {TEXT_PRIMARY};
                font-weight: 600;
            }}
        """)

class ThumbnailLoader(QThread):
    thumbnail_loaded = pyqtSignal(str, QPixmap)
    thumbnail_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.queue = []
        self.running = True
        self.cache = {}
        self.active_requests = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def add_to_queue(self, appid):
        if appid not in self.cache and appid not in self.active_requests:
            self.queue.append(appid)
            self.active_requests[appid] = True
            return True
        return False
    
    def get_cached(self, appid):
        return self.cache.get(appid)
    
    def download_thumbnail(self, appid):
        try:
            url = f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}/header.jpg"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                if not pixmap.isNull():
                    return pixmap.scaled(200, 93, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            return None
        except:
            return None
    
    def run(self):
        while self.running:
            if self.queue:
                appid = self.queue.pop(0)
                try:
                    pixmap = self.download_thumbnail(appid)
                    if pixmap:
                        self.cache[appid] = pixmap
                        self.thumbnail_loaded.emit(appid, pixmap)
                    else:
                        self.thumbnail_failed.emit(appid)
                except Exception as e:
                    self.thumbnail_failed.emit(appid)
                finally:
                    if appid in self.active_requests:
                        del self.active_requests[appid]
            self.msleep(50)

class GameCard(QFrame):
    clicked = pyqtSignal(dict)
    
    def __init__(self, game_data, thumbnail_loader, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.appid = str(game_data.get('appid', ''))
        self.thumbnail_loader = thumbnail_loader
        self.thumbnail_set = False
        self.setFixedSize(200, 235)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            GameCard {{
                background: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}
            GameCard:hover {{
                background: {CARD_HOVER};
                border: 1px solid {BORDER_HOVER};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.image_frame = QFrame()
        self.image_frame.setFixedHeight(93)
        self.image_frame.setStyleSheet(f"""
            QFrame {{
                background: {BG_LIGHT};
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
        """)
        image_layout = QVBoxLayout(self.image_frame)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(200, 93)
        self.image_label.setStyleSheet(f"QLabel {{ color: {TEXT_SECONDARY}; font-size: 10px; background: {BG_LIGHT}; border-top-left-radius: 6px; border-top-right-radius: 6px; }}")
        
        cached = self.thumbnail_loader.get_cached(self.appid)
        if cached:
            self.image_label.setPixmap(cached)
            self.thumbnail_set = True
        else:
            self.image_label.setText("LOADING...")
            if self.appid and self.appid.isdigit():
                QTimer.singleShot(100, lambda: self.request_thumbnail())
        
        type_badge = QLabel(game_data.get('type', 'game').upper())
        type_badge.setStyleSheet(f"""
            QLabel {{
                background: rgba(0, 0, 0, 0.9);
                color: {TEXT_SECONDARY};
                font-size: 9px;
                font-weight: 600;
                padding: 2px 6px;
                border-radius: 2px;
                margin: 4px;
            }}
        """)
        type_badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(type_badge)
        image_layout.setAlignment(type_badge, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(self.image_frame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 8, 10, 8)
        content_layout.setSpacing(4)
        
        title = QLabel(game_data.get('name', 'Unknown Game'))
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: 600;")
        content_layout.addWidget(title)
        
        tags = game_data.get('tags', [])
        if tags:
            tag_text = ', '.join(tags[:2])
            if len(tags) > 2:
                tag_text += f" +{len(tags)-2}"
            tag_label = QLabel(tag_text)
            tag_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px;")
            tag_label.setWordWrap(True)
            content_layout.addWidget(tag_label)
        
        badge_layout = QHBoxLayout()
        badge_layout.setSpacing(4)
        
        if game_data.get('nsfw'):
            badge = QLabel("18+")
            badge.setStyleSheet(f"""
                QLabel {{
                    background: #333;
                    color: {TEXT_PRIMARY};
                    font-size: 9px;
                    font-weight: 600;
                    padding: 2px 4px;
                    border-radius: 2px;
                    border: 1px solid {TEXT_PRIMARY};
                }}
            """)
            badge_layout.addWidget(badge)
        
        if game_data.get('drm'):
            badge = QLabel("DRM FREE")
            badge.setStyleSheet(f"""
                QLabel {{
                    background: #222;
                    color: {TEXT_PRIMARY};
                    font-size: 9px;
                    font-weight: 600;
                    padding: 2px 4px;
                    border-radius: 2px;
                    border: 1px solid {TEXT_SECONDARY};
                }}
            """)
            badge_layout.addWidget(badge)
        
        badge_layout.addStretch()
        content_layout.addLayout(badge_layout)
        
        self.install_btn = ActionButton("INSTALL", primary=True)
        self.install_btn.setFixedHeight(24)
        content_layout.addWidget(self.install_btn)
        
        layout.addWidget(content)
        self.setLayout(layout)
        
        self.install_btn.clicked.connect(lambda: self.clicked.emit(self.game_data))
    
    def request_thumbnail(self):
        if not self.thumbnail_set and self.thumbnail_loader.add_to_queue(self.appid):
            pass
    
    def set_thumbnail(self, appid, pixmap):
        if appid == self.appid and not self.thumbnail_set:
            self.image_label.setPixmap(pixmap)
            self.thumbnail_set = True
    
    def set_thumbnail_failed(self, appid):
        if appid == self.appid and not self.thumbnail_set:
            self.image_label.setText("NO IMAGE")
            self.thumbnail_set = True
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.install_btn.underMouse():
            self.clicked.emit(self.game_data)

class TopBar(QFrame):
    def __init__(self, steam_path, parent=None):
        super().__init__(parent)
        self.steam_path = steam_path
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            QFrame {{
                background: {TOPBAR_BG};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(20)
        
        logo = QLabel("YHUJIN CLIENT")
        logo.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 0.5px;
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(logo)
        
        self.status_icon = QLabel("\u25cf")
        self.status_icon.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; background: transparent; border: none;")
        layout.addWidget(self.status_icon)
        
        self.status_text = QLabel("Steam: ?")
        self.status_text.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 500; background: transparent; border: none;")
        layout.addWidget(self.status_text)
        
        self.restart_btn = QPushButton("Restart")
        self.restart_btn.setFixedSize(60, 24)
        self.restart_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {BTN_BG}; 
                border: 1px solid {BORDER}; 
                color: {TEXT_SECONDARY}; 
                font-size: 11px; 
                font-weight: 600;
                border-radius: 3px;
                padding: 2px 0;
            }}
            QPushButton:hover {{ background: {BTN_HOVER}; border-color: {BORDER_HOVER}; color: {TEXT_PRIMARY}; }}
            QPushButton:disabled {{ background: {BTN_DISABLED}; color: {TEXT_MUTED}; border-color: #222; }}
        """)
        self.restart_btn.clicked.connect(self.restart_steam)
        layout.addWidget(self.restart_btn)
        
        self.xinput_btn = QPushButton("XInput")
        self.xinput_btn.setFixedSize(60, 24)
        self.xinput_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: {BTN_BG}; 
                border: 1px solid {BORDER}; 
                color: {TEXT_SECONDARY}; 
                font-size: 11px; 
                font-weight: 600;
                border-radius: 3px;
                padding: 2px 0;
            }}
            QPushButton:hover {{ background: {BTN_HOVER}; border-color: {BORDER_HOVER}; color: {TEXT_PRIMARY}; }}
            QPushButton:disabled {{ background: {BTN_DISABLED}; color: {TEXT_MUTED}; border-color: #222; }}
        """)
        self.xinput_btn.clicked.connect(self.install_xinput)
        layout.addWidget(self.xinput_btn)
        
        self.xinput_status = QLabel("")
        self.xinput_status.setFixedWidth(30)
        self.xinput_status.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self.xinput_status)
        
        layout.addStretch()
        
        self.steam_path_label = QLabel("")
        self.steam_path_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self.steam_path_label)
        
        self.setLayout(layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_status)
        self.timer.start(2000)
        
        self.check_status()
        self.check_xinput()
    
    def check_status(self):
        if not self.steam_path:
            self.status_icon.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; background: transparent; border: none;")
            self.status_text.setText("Steam: ?")
            self.restart_btn.setEnabled(False)
            self.steam_path_label.setText("")
            return
        running = False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'steam.exe' in proc.info['name'].lower():
                    running = True; break
            except: continue
        if running:
            self.status_icon.setStyleSheet(f"font-size: 10px; color: {GREEN}; background: transparent; border: none;")
            self.status_text.setText("Steam: Running")
            self.restart_btn.setEnabled(True)
        else:
            self.status_icon.setStyleSheet(f"font-size: 10px; color: {RED}; background: transparent; border: none;")
            self.status_text.setText("Steam: Stopped")
            self.restart_btn.setEnabled(True)
        
        short = self.steam_path if len(self.steam_path) <= 45 else "..." + self.steam_path[-42:]
        self.steam_path_label.setText(short)
    
    def check_xinput(self):
        if self.steam_path:
            dll = os.path.join(self.steam_path, "xinput1_4.dll")
            if os.path.exists(dll):
                self.xinput_status.setText("\u2713")
                self.xinput_status.setStyleSheet(f"color: {GREEN}; font-size: 11px; background: transparent; border: none;")
                self.xinput_btn.setEnabled(False)
            else:
                self.xinput_status.setText("\u2717")
                self.xinput_status.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; background: transparent; border: none;")
                self.xinput_btn.setEnabled(True)
    
    def restart_steam(self):
        if not self.steam_path: return
        if QMessageBox.question(self, "Restart Steam", "Restart Steam now?") == QMessageBox.StandardButton.Yes:
            success, message = SteamLocator.restart_steam(self.steam_path)
            QMessageBox.information(self, "Success" if success else "Failed", message)
    
    def install_xinput(self):
        if not self.steam_path: return
        success, message = SteamLocator.check_and_install_xinput_dll(self.steam_path)
        QMessageBox.information(self, "Success" if success else "Failed", message)
        self.check_xinput()

class GameListTab(QWidget):
    install_requested = pyqtSignal(str, str)
    
    def __init__(self, steam_path):
        super().__init__()
        self.steam_path = steam_path
        self.all_games = []
        self.filtered_games = []
        self.loader = None
        self.thumbnail_loader = ThumbnailLoader()
        self.thumbnail_loader.start()
        self.cards = []
        self.current_cols = 0
        self.tags = ["All Tags", "Indie", "Adventure", "Action", "Casual", "Simulation", "RPG", "Strategy", 
                     "Sports", "Racing", "Utilities", "Education", "Violent", "Gore", "Sexual Content", "Nudity"]
        self.initUI()
        QTimer.singleShot(100, self.load_games)
    
    def initUI(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {BG_DARK};
            }}
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 500;
            }}
            QComboBox {{
                background: {INPUT_BG};
                border: 1px solid {INPUT_BORDER};
                color: {TEXT_PRIMARY};
                font-size: 11px;
                font-weight: 500;
                padding: 4px 6px;
                border-radius: 3px;
                height: 20px;
            }}
            QComboBox:hover {{
                border: 1px solid {INPUT_FOCUS};
                background: {BG_LIGHT};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {TEXT_SECONDARY};
                margin-right: 4px;
            }}
            QComboBox QAbstractItemView {{
                background: {INPUT_BG};
                border: 1px solid {INPUT_BORDER};
                color: {TEXT_PRIMARY};
                selection-background-color: {BG_LIGHT};
            }}
            QLineEdit {{
                background: {INPUT_BG};
                border: 1px solid {INPUT_BORDER};
                color: {TEXT_PRIMARY};
                font-size: 11px;
                padding: 4px 6px;
                border-radius: 3px;
                height: 20px;
            }}
            QLineEdit:focus {{
                border: 1px solid {INPUT_FOCUS};
                background: {BG_LIGHT};
            }}
            QCheckBox {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
                font-weight: 500;
                spacing: 4px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                background: {INPUT_BG};
                border: 1px solid {INPUT_BORDER};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background: {TEXT_PRIMARY};
                border: 1px solid {TEXT_PRIMARY};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {INPUT_FOCUS};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 10, 12, 8)
        main_layout.setSpacing(8)
        
        header = QLabel("GAME LIST")
        header.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: 0.5px; margin-bottom: 0px;")
        main_layout.addWidget(header)
        
        filter_bar = QFrame()
        filter_bar.setStyleSheet(f"QFrame {{ background: {BG_MEDIUM}; border-radius: 6px; }}")
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(8, 6, 8, 6)
        filter_layout.setSpacing(6)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search games...")
        self.search_input.setFixedHeight(24)
        self.search_input.textChanged.connect(lambda: QTimer.singleShot(300, self.apply_filters))
        filter_layout.addWidget(self.search_input, 2)
        
        self.tag_combo = QComboBox()
        self.tag_combo.addItems(self.tags)
        self.tag_combo.setFixedWidth(110)
        self.tag_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.tag_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Types", "game", "demo", "music"])
        self.type_combo.setFixedWidth(80)
        self.type_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_combo)
        
        self.nsfw_check = QCheckBox("18+")
        self.nsfw_check.stateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.nsfw_check)
        
        self.drm_check = QCheckBox("DRM Free")
        self.drm_check.stateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.drm_check)
        
        reset_btn = ActionButton("Reset")
        reset_btn.setFixedSize(55, 24)
        reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_btn)
        
        main_layout.addWidget(filter_bar)
        
        stats_bar = QFrame()
        stats_bar.setStyleSheet("QFrame { background: transparent; }")
        stats_layout = QHBoxLayout(stats_bar)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.total_label = QLabel("Loading games...")
        self.total_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 500;")
        stats_layout.addWidget(self.total_label)
        
        stats_layout.addStretch()
        
        per_page_label = QLabel("Show:")
        per_page_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        stats_layout.addWidget(per_page_label)
        
        self.per_page_combo = QComboBox()
        self.per_page_combo.addItems(["12", "24", "48", "96"])
        self.per_page_combo.setCurrentText("24")
        self.per_page_combo.setFixedWidth(50)
        self.per_page_combo.currentTextChanged.connect(self.change_per_page)
        stats_layout.addWidget(self.per_page_combo)
        
        main_layout.addWidget(stats_bar)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)
        
        pagination_bar = QFrame()
        pagination_bar.setStyleSheet("QFrame { background: transparent; }")
        pagination_layout = QHBoxLayout(pagination_bar)
        pagination_layout.setContentsMargins(0, 2, 0, 0)
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 500; margin: 0 8px;")
        
        self.prev_btn = ActionButton("Prev")
        self.prev_btn.setFixedSize(50, 22)
        self.prev_btn.clicked.connect(self.prev_page)
        
        self.next_btn = ActionButton("Next")
        self.next_btn.setFixedSize(50, 22)
        self.next_btn.clicked.connect(self.next_page)
        
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)
        
        main_layout.addWidget(pagination_bar)
        
        self.setLayout(main_layout)
        
        self.current_page = 1
        self.items_per_page = 24
        self.total_pages = 1
        self.update_pagination()
    
    def load_games(self):
        if self.loader and self.loader.isRunning():
            return
        
        self.total_label.setText("Loading games...")
        
        try:
            response = requests.get("https://raw.githubusercontent.com/SteamTools-Team/GameList/refs/heads/main/games.json", timeout=10)
            if response.status_code == 200:
                self.all_games = response.json()
                self.apply_filters()
                self.total_label.setText(f"Total: {len(self.all_games)} games")
            else:
                self.total_label.setText("Failed to load games")
        except Exception as e:
            self.total_label.setText(f"Error: {str(e)}")
    
    def apply_filters(self):
        if not self.all_games:
            return
        
        search_text = self.search_input.text().lower().strip()
        selected_tag = self.tag_combo.currentText()
        selected_type = self.type_combo.currentText()
        show_nsfw = self.nsfw_check.isChecked()
        show_drm = self.drm_check.isChecked()
        
        self.filtered_games = []
        
        for game in self.all_games:
            if search_text and search_text not in game.get('name', '').lower():
                continue
            
            if selected_tag != "All Tags" and selected_tag not in game.get('tags', []):
                continue
            
            if selected_type != "All Types" and game.get('type', '') != selected_type:
                continue
            
            if show_nsfw and not game.get('nsfw'):
                continue
            
            if show_drm and not game.get('drm'):
                continue
            
            self.filtered_games.append(game)
        
        self.total_pages = max(1, (len(self.filtered_games) + self.items_per_page - 1) // self.items_per_page)
        self.current_page = min(self.current_page, self.total_pages)
        
        self.update_pagination()
        self.display_current_page()
    
    def display_current_page(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.filtered_games:
            empty_label = QLabel("No games found")
            empty_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px; padding: 30px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, 4)
            return
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.filtered_games))
        
        cols = max(2, self.width() // 215)
        
        row = 0
        col = 0
        
        for i in range(start_idx, end_idx):
            game = self.filtered_games[i]
            card = GameCard(game, self.thumbnail_loader)
            card.clicked.connect(self.on_game_clicked)
            self.thumbnail_loader.thumbnail_loaded.connect(card.set_thumbnail)
            self.thumbnail_loader.thumbnail_failed.connect(card.set_thumbnail_failed)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= cols:
                col = 0
                row += 1
    
    def on_game_clicked(self, game_data):
        appid = game_data.get('appid', '')
        name = game_data.get('name', 'Unknown')
        self.install_requested.emit(str(appid), name)
    
    def update_pagination(self):
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
    
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination()
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()
            self.update_pagination()
    
    def change_per_page(self, value):
        self.items_per_page = int(value)
        self.total_pages = max(1, (len(self.filtered_games) + self.items_per_page - 1) // self.items_per_page)
        self.current_page = min(self.current_page, self.total_pages)
        self.display_current_page()
        self.update_pagination()
    
    def reset_filters(self):
        self.search_input.clear()
        self.tag_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.nsfw_check.setChecked(False)
        self.drm_check.setChecked(False)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.filtered_games:
            new_cols = max(2, self.width() // 215)
            if new_cols != self.current_cols:
                self.current_cols = new_cols
                self.display_current_page()

class ThreadManager:
    threads = []
    @classmethod
    def add(cls, t): cls.threads.append(t)
    @classmethod
    def remove(cls, t): 
        if t in cls.threads: cls.threads.remove(t)
    @classmethod
    def stop_all(cls):
        for t in cls.threads:
            if t.isRunning(): t.stop(); t.wait()
        cls.threads.clear()

class BaseWorker(QThread):
    finished = pyqtSignal(); error = pyqtSignal(str)
    def __init__(self): 
        super().__init__(); self._running = True; self._mutex = QMutex()
    def stop(self): 
        with QMutexLocker(self._mutex): self._running = False
    def is_running(self): 
        with QMutexLocker(self._mutex): return self._running

class SteamLocator:
    @staticmethod
    def find_steam_from_process():
        try:
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    if proc.info['name'] and 'steam.exe' in proc.info['name'].lower():
                        exe_path = proc.info['exe']
                        if exe_path and os.path.exists(exe_path):
                            return os.path.dirname(exe_path)
                except: continue
        except: pass
        return None
    
    @staticmethod
    def find_steam_from_registry():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            winreg.CloseKey(key)
            return path if path and os.path.exists(path) else None
        except: return None
    
    @staticmethod
    def find_steam():
        path = SteamLocator.find_steam_from_process()
        return path if path else SteamLocator.find_steam_from_registry()
    
    @staticmethod
    def ensure_steam_folders(steam_path):
        if not steam_path: return False
        for folder in [os.path.join(steam_path, "config", "depotcache"), os.path.join(steam_path, "config", "stplug-in")]:
            if not os.path.exists(folder): os.makedirs(folder)
        return True
    
    @staticmethod
    def check_and_install_xinput_dll(steam_path):
        if not steam_path: return False, "Steam path not found"
        dll_path = os.path.join(steam_path, "xinput1_4.dll")
        if os.path.exists(dll_path): return True, "DLL already exists"
        try:
            r = requests.get("https://github.com/SevelXX/dll/raw/refs/heads/main/xinput1_4.dll", timeout=30)
            if r.status_code == 200:
                with open(dll_path, 'wb') as f: f.write(r.content)
                return True, "DLL installed"
            return False, f"HTTP {r.status_code}"
        except Exception as e: return False, str(e)
    
    @staticmethod
    def restart_steam(steam_path):
        if not steam_path: return False, "Steam path not found"
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if proc.info['name'] and 'steam.exe' in proc.info['name'].lower(): proc.kill()
                except: continue
            time.sleep(2)
            subprocess.Popen([os.path.join(steam_path, "steam.exe")])
            return True, "Steam restarted"
        except Exception as e: return False, str(e)

class DownloadThread(BaseWorker):
    progress = pyqtSignal(int); download_finished = pyqtSignal(bool, str)
    def __init__(self, appid, name, steam_path):
        super().__init__(); self.appid = appid; self.name = name; self.steam_path = steam_path
    def run(self):
        try:
            depot = os.path.join(self.steam_path, "config", "depotcache")
            plugin = os.path.join(self.steam_path, "config", "stplug-in")
            os.makedirs(depot, exist_ok=True); os.makedirs(plugin, exist_ok=True)
            self.progress.emit(10)
            
            download_url = None
            
            try:
                api_url = f"https://luagen.pages.dev/api/check-lua?id={self.appid}"
                r = requests.get(api_url, timeout=30)
                if not self.is_running(): return
                if r.status_code == 200:
                    api_data = r.json()
                    if api_data.get('success'):
                        download_url = api_data.get('primary')
            except:
                pass
            
            if not download_url:
                backup_url = f"https://pub-5b6d3b7c03fd4ac1afb5bd3017850e20.r2.dev/{self.appid}.zip"
                try:
                    r = requests.head(backup_url, timeout=10)
                    if r.status_code == 200:
                        download_url = backup_url
                except:
                    pass
            
            if not download_url:
                self.download_finished.emit(False, "No download URL found from any source"); return
            
            self.progress.emit(30)
            
            r = requests.get(download_url, stream=True, timeout=60)
            if not self.is_running(): return
            if r.status_code != 200:
                self.download_finished.emit(False, f"Download Error: HTTP {r.status_code}"); return
            
            content = io.BytesIO(); total = int(r.headers.get('content-length', 0)); downloaded = 0
            for chunk in r.iter_content(8192):
                if not self.is_running(): return
                content.write(chunk); downloaded += len(chunk)
                if total > 0: self.progress.emit(30 + int((downloaded / total) * 70))
            content.seek(0); m, l = 0, 0
            with zipfile.ZipFile(content) as z:
                for f in z.infolist():
                    name = os.path.basename(f.filename)
                    if name.endswith('.manifest'):
                        with open(os.path.join(depot, name), 'wb') as out: out.write(z.open(f).read()); m += 1
                    elif name.endswith('.lua'):
                        with open(os.path.join(plugin, name), 'wb') as out: out.write(z.open(f).read()); l += 1
            if self.is_running(): self.download_finished.emit(True, f"Installed {self.name} ({m} manifest, {l} lua)")
        except Exception as e: self.download_finished.emit(False, str(e))
        finally: self.finished.emit()

class LuaScanner(BaseWorker):
    game_found = pyqtSignal(str, str); scan_finished = pyqtSignal(int)
    def __init__(self, steam_path): super().__init__(); self.steam_path = steam_path
    def run(self):
        try:
            lua_path = os.path.join(self.steam_path, "config", "stplug-in"); appids = set()
            if os.path.exists(lua_path):
                for f in os.listdir(lua_path):
                    if not self.is_running(): return
                    if f.endswith('.lua'):
                        appid = f.replace('.lua', '')
                        if appid.isdigit(): appids.add(appid)
            appids = list(appids); total = len(appids)
            if total == 0: self.scan_finished.emit(0); return
            for appid in appids:
                if not self.is_running(): return
                try:
                    r = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}", timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        if data.get(appid, {}).get('success'):
                            self.game_found.emit(appid, data[appid]['data']['name'])
                        else: self.game_found.emit(appid, "Unknown")
                    else: self.game_found.emit(appid, "Unknown")
                    time.sleep(0.5)
                except: self.game_found.emit(appid, "Unknown")
            self.scan_finished.emit(total)
        except Exception as e: self.error.emit(str(e))
        finally: self.finished.emit()

class UninstallThread(BaseWorker):
    progress = pyqtSignal(int, str); uninstall_finished = pyqtSignal(bool, str)
    def __init__(self, steam_path, games_to_uninstall):
        super().__init__(); self.steam_path = steam_path; self.games_to_uninstall = games_to_uninstall
    def run(self):
        try:
            lua_path = os.path.join(self.steam_path, "config", "stplug-in")
            depotcache_path = os.path.join(self.steam_path, "config", "depotcache")
            steamapps_path = os.path.join(self.steam_path, "steamapps")
            total = len(self.games_to_uninstall); uninstalled = 0; failed = []
            for i, (appid, name) in enumerate(self.games_to_uninstall):
                if not self.is_running(): return
                try:
                    lua_deleted = 0; manifest_deleted = 0
                    if os.path.exists(lua_path):
                        f = os.path.join(lua_path, f"{appid}.lua")
                        if os.path.exists(f): os.remove(f); lua_deleted += 1
                    if os.path.exists(depotcache_path):
                        for file in os.listdir(depotcache_path):
                            if file.startswith(f"{appid}_") and file.endswith(".manifest"):
                                os.remove(os.path.join(depotcache_path, file)); manifest_deleted += 1
                    acf_file = os.path.join(steamapps_path, f"appmanifest_{appid}.acf")
                    if os.path.exists(acf_file): os.remove(acf_file)
                    if lua_deleted > 0 or manifest_deleted > 0:
                        uninstalled += 1
                        self.progress.emit(int((i + 1) / total * 100), f"Uninstalled: {name} ({lua_deleted} lua, {manifest_deleted} manifest)")
                    else: failed.append(f"{name} (no files found)")
                except Exception as e: failed.append(f"{name} ({str(e)})")
            if failed: self.uninstall_finished.emit(False, f"Uninstalled {uninstalled} games.\nFailed: {', '.join(failed)}")
            else: self.uninstall_finished.emit(True, f"Successfully uninstalled {uninstalled} games")
        except Exception as e: self.uninstall_finished.emit(False, f"Error: {str(e)}")
        finally: self.finished.emit()

class InstallTab(QWidget):
    install_requested = pyqtSignal(str, str)
    def __init__(self, steam_path):
        super().__init__(); self.steam_path = steam_path; self.manifest = []; self.lua = []; self.setAcceptDrops(True); self.initUI()
    def initUI(self):
        self.setStyleSheet(f"QWidget {{ background: {BG_DARK}; }}")
        l = QVBoxLayout(); l.setContentsMargins(16, 14, 16, 14); l.setSpacing(14)
        
        header = QLabel("INSTALL GAME")
        header.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: 0.5px; margin-bottom: 2px;"); l.addWidget(header)
        
        f1 = QFrame(); f1.setStyleSheet(f"QFrame {{ background: {BG_MEDIUM}; border: 1px solid {BORDER}; border-radius: 6px; }}")
        h1 = QHBoxLayout(); h1.setContentsMargins(14, 10, 14, 10); h1.setSpacing(8)
        h1.addWidget(QLabel("App ID:"))
        self.app_input = QLineEdit(); self.app_input.setPlaceholderText("Enter Steam App ID"); self.app_input.setFixedHeight(30)
        self.app_input.setStyleSheet(f"QLineEdit {{ background: {INPUT_BG}; border: 1px solid {INPUT_BORDER}; padding: 5px 8px; color: {TEXT_PRIMARY}; font-size: 12px; border-radius: 4px; }}")
        self.install_btn = QPushButton("Install Now"); self.install_btn.setFixedSize(85, 30)
        self.install_btn.setStyleSheet(f"QPushButton {{ background: {TEXT_PRIMARY}; border: none; color: {BG_DARK}; font-size: 12px; font-weight: 600; border-radius: 4px; }} QPushButton:hover {{ background: {ACCENT_HOVER}; }}")
        self.install_btn.clicked.connect(self.install_via_appid)
        h1.addWidget(self.app_input, 1); h1.addWidget(self.install_btn); f1.setLayout(h1); l.addWidget(f1)
        
        f2 = QFrame(); f2.setStyleSheet(f"QFrame {{ background: {BG_MEDIUM}; border: 1px solid {BORDER}; border-radius: 6px; }}")
        v1 = QVBoxLayout(); v1.setContentsMargins(14, 14, 14, 14); v1.setSpacing(8)
        
        drop_label = QLabel("DRAG & DROP FILES")
        drop_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600; letter-spacing: 0.5px;")
        v1.addWidget(drop_label)
        
        self.drop = QLabel("Drop .manifest and .lua files here"); self.drop.setAlignment(Qt.AlignmentFlag.AlignCenter); self.drop.setFixedHeight(55)
        self.drop.setStyleSheet(f"QLabel {{ border: 2px dashed {BORDER}; background: {INPUT_BG}; color: {TEXT_MUTED}; font-size: 11px; border-radius: 5px; }}")
        self.file_list = QListWidget(); self.file_list.setMaximumHeight(65)
        self.file_list.setStyleSheet(f"QListWidget {{ background: {INPUT_BG}; border: 1px solid {INPUT_BORDER}; color: {TEXT_PRIMARY}; font-size: 11px; border-radius: 4px; }}")
        h2 = QHBoxLayout()
        self.install_files = QPushButton("Install Files"); self.install_files.setFixedHeight(30); self.install_files.setEnabled(False)
        self.install_files.setStyleSheet(f"QPushButton {{ background: {TEXT_PRIMARY}; border: none; color: {BG_DARK}; font-size: 11px; font-weight: 600; padding: 0 18px; border-radius: 4px; }} QPushButton:disabled {{ background: {BTN_DISABLED}; color: {TEXT_MUTED}; }}")
        self.install_files.clicked.connect(self.install_dropped)
        self.clear_btn = QPushButton("Clear"); self.clear_btn.setFixedHeight(30); self.clear_btn.setEnabled(False)
        self.clear_btn.setStyleSheet(f"QPushButton {{ background: {BTN_BG}; border: 1px solid {BORDER}; color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 500; padding: 0 18px; border-radius: 4px; }} QPushButton:hover {{ background: {BTN_HOVER}; }}")
        self.clear_btn.clicked.connect(self.clear_files)
        h2.addStretch(); h2.addWidget(self.install_files); h2.addWidget(self.clear_btn)
        v1.addWidget(self.drop); v1.addWidget(self.file_list); v1.addLayout(h2); f2.setLayout(v1); l.addWidget(f2)
        
        f3 = QFrame(); f3.setStyleSheet(f"QFrame {{ background: {BG_MEDIUM}; border: 1px solid {BORDER}; border-radius: 6px; }}")
        v2 = QVBoxLayout(); v2.setContentsMargins(14, 10, 14, 10); v2.setSpacing(5)
        if self.steam_path:
            v2.addWidget(QLabel("INSTALLATION PATHS:"))
            v2.addWidget(QLabel(f"Depot: {os.path.join(self.steam_path, 'config', 'depotcache')}"))
            v2.addWidget(QLabel(f"Plugin: {os.path.join(self.steam_path, 'config', 'stplug-in')}"))
        else: v2.addWidget(QLabel("Steam path not found"))
        for i in range(v2.count()): 
            w = v2.itemAt(i).widget()
            if w: w.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 2px 0;")
        f3.setLayout(v2); l.addWidget(f3); l.addStretch(); self.setLayout(l)
    
    def dragEnterEvent(self, e): 
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dropEvent(self, e):
        files = []
        for url in e.mimeData().urls():
            p = url.toLocalFile()
            if p.endswith(('.manifest', '.lua')): files.append(p)
        if files: self.add_files(files)
    def add_files(self, files):
        for f in files:
            n = os.path.basename(f)
            if f.endswith('.manifest') and f not in self.manifest:
                self.manifest.append(f); self.file_list.addItem(f"[M] {n}")
            elif f.endswith('.lua') and f not in self.lua:
                self.lua.append(f); self.file_list.addItem(f"[L] {n}")
        self.update_buttons()
    def update_buttons(self):
        has = bool(self.manifest or self.lua)
        self.install_files.setEnabled(has); self.clear_btn.setEnabled(has)
        if has: self.drop.setText(f"{len(self.manifest)} manifest, {len(self.lua)} lua files ready")
        else: self.drop.setText("Drop .manifest and .lua files here")
    def clear_files(self): self.manifest.clear(); self.lua.clear(); self.file_list.clear(); self.update_buttons()
    def install_via_appid(self):
        appid = self.app_input.text().strip()
        if not appid or not appid.isdigit(): QMessageBox.warning(self, "Error", "Enter valid App ID"); return
        self.install_requested.emit(appid, f"AppID {appid}")
    def install_dropped(self):
        if not self.steam_path: QMessageBox.warning(self, "Error", "Steam not found"); return
        depot = os.path.join(self.steam_path, "config", "depotcache")
        plugin = os.path.join(self.steam_path, "config", "stplug-in"); m, l = 0, 0
        try:
            for f in self.manifest: shutil.copy2(f, depot); m += 1
            for f in self.lua: shutil.copy2(f, plugin); l += 1
            QMessageBox.information(self, "Success", f"Installed {m} manifest, {l} lua files")
            self.clear_files()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

class UninstallTab(QWidget):
    def __init__(self, steam_path):
        super().__init__(); self.steam_path = steam_path; self.games = []; self.scanner = None; self.uninstaller = None; self.initUI()
    def initUI(self):
        self.setStyleSheet(f"QWidget {{ background: {BG_DARK}; }}")
        l = QVBoxLayout(); l.setContentsMargins(16, 14, 16, 14); l.setSpacing(14)
        
        header = QLabel("UNINSTALL GAME")
        header.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY}; letter-spacing: 0.5px; margin-bottom: 2px;"); l.addWidget(header)
        
        f1 = QFrame(); f1.setStyleSheet(f"QFrame {{ background: {BG_MEDIUM}; border: 1px solid {BORDER}; border-radius: 6px; }}")
        h1 = QHBoxLayout(); h1.setContentsMargins(14, 10, 14, 10)
        self.scan = QPushButton("Scan Installed"); self.scan.setFixedHeight(30)
        self.scan.setStyleSheet(f"QPushButton {{ background: {BTN_BG}; border: 1px solid {BORDER}; color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600; padding: 0 16px; border-radius: 4px; }} QPushButton:hover {{ background: {BTN_HOVER}; }}")
        self.scan.clicked.connect(self.scan_files); h1.addWidget(self.scan)
        self.select = QPushButton("Select All"); self.select.setFixedHeight(30)
        self.select.setStyleSheet(f"QPushButton {{ background: {BTN_BG}; border: 1px solid {BORDER}; color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 500; padding: 0 16px; border-radius: 4px; }} QPushButton:hover {{ background: {BTN_HOVER}; }}")
        self.select.clicked.connect(lambda: self.list.selectAll()); h1.addWidget(self.select)
        self.unselect = QPushButton("Unselect"); self.unselect.setFixedHeight(30)
        self.unselect.setStyleSheet(f"QPushButton {{ background: {BTN_BG}; border: 1px solid {BORDER}; color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 500; padding: 0 16px; border-radius: 4px; }} QPushButton:hover {{ background: {BTN_HOVER}; }}")
        self.unselect.clicked.connect(lambda: self.list.clearSelection()); h1.addWidget(self.unselect)
        h1.addStretch()
        self.uninstall_btn = QPushButton("Uninstall Selected"); self.uninstall_btn.setFixedHeight(30); self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.setStyleSheet(f"QPushButton {{ background: {RED}; border: none; color: {BG_DARK}; font-size: 11px; font-weight: 600; padding: 0 16px; border-radius: 4px; }} QPushButton:hover {{ background: {RED_HOVER}; }} QPushButton:disabled {{ background: {BTN_DISABLED}; color: {TEXT_MUTED}; }}")
        self.uninstall_btn.clicked.connect(self.uninstall); h1.addWidget(self.uninstall_btn)
        f1.setLayout(h1); l.addWidget(f1)
        
        self.info = QLabel("Ready"); self.info.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 4px;"); l.addWidget(self.info)
        self.progress = QProgressBar(); self.progress.setVisible(False); self.progress.setFixedHeight(4); self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"QProgressBar {{ border: none; background: {PROGRESS_BG}; border-radius: 2px; }} QProgressBar::chunk {{ background: {PROGRESS_CHUNK}; border-radius: 2px; }}")
        l.addWidget(self.progress)
        
        self.list = QListWidget(); self.list.setSelectionMode(QListWidget.SelectionMode.MultiSelection); self.list.setAlternatingRowColors(True)
        self.list.setStyleSheet(f"""
            QListWidget {{ background: {BG_MEDIUM}; border: 1px solid {BORDER}; color: {TEXT_PRIMARY}; font-size: 11px; border-radius: 5px; }}
            QListWidget::item {{ padding: 7px; border-bottom: 1px solid #222; }}
            QListWidget::item:selected {{ background-color: {BG_LIGHT}; color: {TEXT_PRIMARY}; }}
            QListWidget::item:hover {{ background-color: #1a1a1a; }}
        """)
        l.addWidget(self.list); self.setLayout(l)
    
    def scan_files(self):
        if self.scanner and self.scanner.isRunning(): self.scanner.stop(); self.scanner.wait()
        self.list.clear(); self.games.clear(); self.info.setText("Scanning..."); self.scan.setEnabled(False); self.uninstall_btn.setEnabled(False)
        self.progress.setVisible(True); self.progress.setRange(0, 0)
        self.scanner = LuaScanner(self.steam_path)
        self.scanner.game_found.connect(lambda a,n: [self.games.append((a,n)), self.list.addItem(QListWidgetItem(f"[{a}] {n}"))])
        self.scanner.scan_finished.connect(lambda t: [self.progress.setVisible(False), self.info.setText(f"Found {t} games"), self.scan.setEnabled(True), self.uninstall_btn.setEnabled(self.list.count() > 0)])
        self.scanner.error.connect(lambda e: [self.progress.setVisible(False), QMessageBox.warning(self, "Error", e), self.scan.setEnabled(True)])
        ThreadManager.add(self.scanner); self.scanner.start()
    
    def uninstall(self):
        items = self.list.selectedItems()
        if not items: return
        games = [(i.text().split(']')[0].replace('[',''), i.text().split('] ')[1] if '] ' in i.text() else i.text()) for i in items]
        names = "\n".join([f"\u2022 {n} [{a}]" for a,n in games])
        if QMessageBox.question(self, "Confirm", f"Uninstall these games?\n\n{names}") != QMessageBox.StandardButton.Yes: return
        self.progress.setVisible(True); self.progress.setRange(0, 100); self.progress.setValue(0)
        self.scan.setEnabled(False); self.select.setEnabled(False); self.unselect.setEnabled(False); self.uninstall_btn.setEnabled(False); self.list.setEnabled(False)
        self.uninstaller = UninstallThread(self.steam_path, games)
        self.uninstaller.progress.connect(lambda v,m: [self.progress.setValue(v), self.info.setText(m)])
        self.uninstaller.uninstall_finished.connect(lambda s,m: [self.progress.setVisible(False), self.scan.setEnabled(True), self.select.setEnabled(True), self.unselect.setEnabled(True), self.list.setEnabled(True), QMessageBox.information(self, "Success" if s else "Error", m), self.scan_files() if s else None])
        ThreadManager.add(self.uninstaller); self.uninstaller.start()

class YHUJINSteamToolkit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.path = None
        self.downloads = []
        self.setWindowTitle("Yhujin Steam Toolkit")
        self.setGeometry(100, 100, 1035, 645)
        self.setStyleSheet(f"QMainWindow {{ background: {BG_DARK}; }}")
        
        discord_dialog = DiscordDialog(self)
        discord_dialog.exec()
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central.setLayout(main_layout)
        
        self.path = SteamLocator.find_steam()
        if self.path:
            SteamLocator.ensure_steam_folders(self.path)
        
        self.top_bar = TopBar(self.path)
        main_layout.addWidget(self.top_bar)
        
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        
        sidebar = QFrame()
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {SIDEBAR_BG};
                border-right: 1px solid {BORDER};
            }}
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 16, 0, 16)
        sidebar_layout.setSpacing(2)
        
        self.nav_library = SidebarButton("GAME LIST")
        self.nav_install = SidebarButton("MANUAL INSTALL")
        self.nav_uninstall = SidebarButton("UNINSTALL")
        
        self.nav_library.clicked.connect(lambda: self.switch_page(0))
        self.nav_install.clicked.connect(lambda: self.switch_page(1))
        self.nav_uninstall.clicked.connect(lambda: self.switch_page(2))
        
        sidebar_layout.addWidget(self.nav_library)
        sidebar_layout.addWidget(self.nav_install)
        sidebar_layout.addWidget(self.nav_uninstall)
        sidebar_layout.addStretch()
        
        sidebar.setLayout(sidebar_layout)
        content.addWidget(sidebar)
        
        self.main_content = QStackedWidget()
        self.main_content.setStyleSheet(f"QStackedWidget {{ background: {BG_DARK}; }}")
        content.addWidget(self.main_content, 1)
        
        main_layout.addLayout(content)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background: {PROGRESS_BG};
            }}
            QProgressBar::chunk {{
                background: {PROGRESS_CHUNK};
            }}
        """)
        main_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 2px; background: {BG_DARK};")
        main_layout.addWidget(self.progress_label)
    
    def switch_page(self, index):
        self.nav_library.setChecked(index == 0)
        self.nav_install.setChecked(index == 1)
        self.nav_uninstall.setChecked(index == 2)
        self.main_content.setCurrentIndex(index)
    
    def download(self, appid, name):
        if not self.path:
            QMessageBox.warning(self, "Error", "Steam not found!")
            return
        
        SteamLocator.ensure_steam_folders(self.path)
        
        thread = DownloadThread(appid, name, self.path)
        thread.progress.connect(lambda v: self.progress_bar.setValue(v))
        thread.download_finished.connect(self.on_download_finished)
        thread.finished.connect(lambda: [self.downloads.remove(thread) if thread in self.downloads else None, ThreadManager.remove(thread)])
        
        ThreadManager.add(thread)
        thread.start()
        self.downloads.append(thread)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"Downloading {name}...")
    
    def on_download_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        QMessageBox.information(self, "Success" if success else "Failed", message)
    
    def closeEvent(self, event):
        ThreadManager.stop_all()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setFont(QFont("Segoe UI", 9))
    app.setApplicationName("Yhujin Steam Toolkit")
    
    window = YHUJINSteamToolkit()
    window.show()

    window.library_tab = GameListTab(window.path)
    window.install_tab = InstallTab(window.path)
    window.uninstall_tab = UninstallTab(window.path)
    
    window.library_tab.install_requested.connect(window.download)
    window.install_tab.install_requested.connect(window.download)
    
    window.main_content.addWidget(window.library_tab)
    window.main_content.addWidget(window.install_tab)
    window.main_content.addWidget(window.uninstall_tab)
    
    window.nav_library.setChecked(True)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()