"""
Global stylesheet and theme constants for the application.
"""

DARK_NAVY = "#0A0E1A"
PANEL_BG = "#0F1629"
CARD_BG = "#12182E"
BORDER_COLOR = "#1A2A4A"
ACCENT = "#00D4FF"
ACCENT2 = "#7B2FFF"
ACCENT3 = "#00FF88"
TEXT_PRIMARY = "#E8F0FF"
TEXT_SECONDARY = "#8090B0"
TEXT_MUTED = "#4A5680"
WARNING = "#FFB800"
DANGER = "#FF4560"
SUCCESS = "#00FF88"

MAIN_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #0A0E1A;
    color: #E8F0FF;
}

QWidget {
    background-color: #0A0E1A;
    color: #E8F0FF;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 11px;
}

QTabWidget::pane {
    border: 1px solid #1A2A4A;
    background-color: #0F1629;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #0A0E1A;
    color: #8090B0;
    padding: 10px 18px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    min-width: 100px;
}

QTabBar::tab:selected {
    color: #00D4FF;
    border-bottom: 2px solid #00D4FF;
    background-color: #0F1629;
}

QTabBar::tab:hover:!selected {
    color: #C8D6F0;
    background-color: #0D1220;
}

QPushButton {
    background-color: #1A2A4A;
    color: #E8F0FF;
    border: 1px solid #2A3A5A;
    border-radius: 5px;
    padding: 7px 16px;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.3px;
}

QPushButton:hover {
    background-color: #1E3060;
    border-color: #00D4FF;
    color: #00D4FF;
}

QPushButton:pressed {
    background-color: #0D1A30;
    border-color: #00D4FF;
}

QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0080AA, stop:1 #00D4FF);
    color: #000814;
    border: none;
    font-weight: 700;
}

QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00AADD, stop:1 #00EEFF);
    color: #000814;
}

QPushButton#danger {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8B0000, stop:1 #FF4560);
    color: white;
    border: none;
}

QPushButton#success {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #006644, stop:1 #00FF88);
    color: #000814;
    border: none;
    font-weight: 700;
}

QLabel {
    color: #E8F0FF;
    background: transparent;
}

QLabel#muted {
    color: #8090B0;
}

QLabel#accent {
    color: #00D4FF;
}

QLabel#section_title {
    color: #00D4FF;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #0F1629;
    color: #E8F0FF;
    border: 1px solid #1A2A4A;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 11px;
    selection-background-color: #1A4080;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #00D4FF;
    background-color: #101828;
}

QComboBox {
    background-color: #0F1629;
    color: #E8F0FF;
    border: 1px solid #1A2A4A;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 11px;
    min-width: 120px;
}

QComboBox:focus {
    border-color: #00D4FF;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #0F1629;
    color: #E8F0FF;
    border: 1px solid #1A2A4A;
    selection-background-color: #1A3060;
    outline: none;
}

QSlider::groove:horizontal {
    height: 4px;
    background-color: #1A2A4A;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #00D4FF;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0080AA, stop:1 #00D4FF);
    border-radius: 2px;
}

QGroupBox {
    color: #8090B0;
    border: 1px solid #1A2A4A;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 8px 8px 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #00D4FF;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

QScrollBar:vertical {
    background-color: #0A0E1A;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #1A2A4A;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00D4FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QStatusBar {
    background-color: #060810;
    color: #8090B0;
    border-top: 1px solid #1A2A4A;
    font-size: 10px;
}

QProgressBar {
    background-color: #1A2A4A;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #E8F0FF;
    font-size: 10px;
    height: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0080AA, stop:1 #00D4FF);
    border-radius: 4px;
}

QListWidget {
    background-color: #0F1629;
    border: 1px solid #1A2A4A;
    border-radius: 5px;
    color: #E8F0FF;
    outline: none;
}

QListWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #1A2040;
}

QListWidget::item:selected {
    background-color: #1A3060;
    color: #00D4FF;
}

QListWidget::item:hover {
    background-color: #0D1830;
}

QCheckBox {
    spacing: 8px;
    color: #E8F0FF;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #2A3A5A;
    border-radius: 3px;
    background: #0F1629;
}

QCheckBox::indicator:checked {
    background: #00D4FF;
    border-color: #00D4FF;
}

QSplitter::handle {
    background-color: #1A2A4A;
    width: 2px;
}

QToolTip {
    background-color: #0F1629;
    color: #C8D6F0;
    border: 1px solid #00D4FF;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 10px;
}
"""


def card_style(extra=""):
    return f"""
        background-color: #12182E;
        border: 1px solid #1A2A4A;
        border-radius: 10px;
        padding: 14px;
        {extra}
    """
