"""Program user interface"""
#pylint: disable=(E0611, E0401, C0103, W0613, R0903, R0902, R0913, R0917, R0914)
#pylint: disable=(R0915, )
import math
from typing import Callable, Union

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import (QCheckBox, QDoubleSpinBox, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPushButton, QSpinBox,
                             QVBoxLayout, QWidget)

from modules.asteroids import Asteroid, AsteroidManager
from modules.consts import MAX_LEFT_GRID as MLG
from modules.consts import SPEED
from modules.consts import ButtonNames as BN
from modules.consts import SettingsParams as SP
from modules.consts import base_settings


class AsteroidPainter(QWidget):
    """Widget that render asteroids on plot"""
    def __init__(self, asteroid_manager: AsteroidManager = None, parent=None):
        """Initialization a class"""
        super().__init__(parent)
        self.manager = asteroid_manager
        self.tree = None

    def paintEvent(self, event):
        """Func that paint asteroids and trees on plot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        if self.manager is None:
            painter.end()
            return

        w, h = self.manager.width, self.manager.height
        scale = min(self.width() / w, self.height() / h)
        ox = (self.width()  - w * scale) / 2
        oy = (self.height() - h * scale) / 2

        painter.save()
        painter.translate(ox, oy)
        painter.scale(scale, scale)

        painter.setPen(QPen(QColor(80, 80, 120), 2 / scale))
        painter.drawRect(QRectF(0, 0, w, h))

        if self.tree is not None:
            self._draw_tree(painter, self.tree, scale)

        painter.setPen(Qt.PenStyle.NoPen)
        for ast in self.manager.asteroids:
            painter.setBrush(QBrush(QColor(*ast.color)))
            painter.drawEllipse(QPointF(ast.x, ast.y), ast.radius, ast.radius)

        painter.restore()
        painter.end()

    def _draw_tree(self, painter, node, scale, depth=0):
        """Func that paint trees on plot"""
        x0, x1, y0, y1 = node.min_x, node.max_x, node.min_y, node.max_y
        alpha = max(30, 160 - depth * 25)
        painter.setPen(QPen(QColor(0, 200, 100, alpha), 1 / scale))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(x0, y0, x1 - x0, y1 - y0))
        if node.nodes and not isinstance(node.nodes[0], Asteroid):
            for child in node.nodes:
                self._draw_tree(painter, child, scale, depth + 1)


class UI(QMainWindow):
    """Program main window class"""
    DSB_STEP = 10 ** (-MLG)

    def __init__(self, asteroid_manager: AsteroidManager):
        """Initialization a class"""
        super().__init__()
        self.asteroid_manager: AsteroidManager = asteroid_manager
        self._is_running: bool = False
        self._is_first_time: bool = True
        self._create_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(round(1000 / SPEED))

    def _create_ui(self):
        """Func that create main program user interface"""
        self.setWindowTitle("Asteroids")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(20)

        form_layout.addWidget(QLabel("Enter params: "))

        self.inputs = {}

        label1 = QLabel("Enter num of asteroids:")
        count = QSpinBox()
        count.setRange(2, 1000)
        count.setValue(base_settings.get(SP.COUNT.value))
        layout1 = QHBoxLayout()
        layout1.addWidget(label1)
        layout1.addWidget(count)
        form_layout.addLayout(layout1)
        self.inputs[SP.COUNT.value] = count

        def _make_pair(parent_layout: QVBoxLayout, title: str,
                       left_label: str, left_range: tuple,
                       left_step: Union[int, float],
                       left_key: Union[int, float], right_label: str,
                       right_range: tuple,
                       right_step: Union[int, float],
                       right_key: Union[int, float],
                       defaults: tuple[float], spin_box: Union[QDoubleSpinBox, QSpinBox]):
            """Create row (QHBoxLayout): [title] [label1][spin1] [label2][spin2]."""
            if title:
                parent_layout.addWidget(QLabel(title))
            row = QHBoxLayout()

            for label_text, rng, step, key, deft in (
                (left_label,  left_range,  left_step,  left_key, defaults[0]),
                (right_label, right_range, right_step, right_key, defaults[1]),
            ):
                row.addWidget(QLabel(label_text + ":"))
                spin = spin_box()
                spin.setRange(*rng)
                spin.setSingleStep(step)

                if isinstance(spin, QDoubleSpinBox):
                    spin.setDecimals(abs(round(math.log10(step))))

                row.addWidget(spin)
                spin.setValue(deft)
                self.inputs[key] = spin

            parent_layout.addLayout(row)

        _make_pair(
            form_layout,
            "Enter asteroids size limits (radius):",
            "Min value", (1, 50), self.DSB_STEP, SP.MIN_VALUE.value,
            "Max value", (2, 100),  self.DSB_STEP, SP.MAX_VALUE.value,
            (base_settings.get(SP.MIN_VALUE.value),
             base_settings.get(SP.MAX_VALUE.value)),
            QDoubleSpinBox
        )

        _make_pair(
            form_layout,
            "Area size:",
            "Height", (200, 1500), 10, SP.HEIGHT.value,
            "Width",  (200, 3000), 5, SP.WIDTH.value,
            (base_settings.get(SP.HEIGHT.value),
             base_settings.get(SP.WIDTH.value)),
            QSpinBox
        )

        _make_pair(
            form_layout,
            "Speed limits",
            "Min speed", (1, 300), 10, SP.MIN_SPEED.value,
            "Max max", (1, 300), 1, SP.MAX_SPEED.value,
            (base_settings.get(SP.MIN_SPEED.value),
             base_settings.get(SP.MAX_SPEED.value)),
            QSpinBox
        )

        self.use_color = QCheckBox("Use color on asteroids?")
        self.use_color.setChecked(base_settings.get(SP.USE_COLOR.value))
        form_layout.addWidget(self.use_color)

        def _create_btn(name: str, func: Callable) -> QPushButton:
            """Create buttons by pattern"""
            btn = QPushButton(name)
            btn.clicked.connect(func)
            return btn

        btns = (
            (BN.START.value, self.start),
            (BN.STOP.value, self.stop),
            (BN.RESTART.value, self.restart)
        )
        self._btns = {}
        btns_layout = QHBoxLayout()

        for name, func in btns:
            btn = _create_btn(name, func)
            btns_layout.addWidget(btn)
            self._btns[name] = btn

        self._switch_btns()
        self._btns[BN.RESTART.value].setDisabled(True)
        form_layout.addStretch()
        form_layout.addLayout(btns_layout)

        root.addWidget(form, 0)
        self.view = AsteroidPainter()
        root.addWidget(self.view, 1)

    def _update_view(self):
        """Update plot with asteroids"""
        self.view.update()

    def _tick(self):
        """Next tick in plot and asteroid manager"""
        if not self._is_running:
            return

        self.asteroid_manager.next_step()
        self.view.tree = self.asteroid_manager.tree
        self._update_view()

    def start(self):
        """Func that starts rendering flying asteroids on plot"""
        if self._is_first_time:
            if not self._new_asteroids():
                return

            self._is_first_time = False
            self._btns[BN.RESTART.value].setDisabled(False)


        self._is_running = True
        self._switch_btns()


    def _switch_btns(self):
        """Switch buttons state by _is_running value"""
        self._btns.get(BN.START.value).setDisabled(self._is_running)
        self._btns.get(BN.STOP.value).setDisabled(not self._is_running)

    def _get_value(self, key):
        """Wrapper on self.inputs.get(key).value"""
        return self.inputs.get(key).value()

    def _error(self, text: str = ""):
        """
        Reusable error message
        """
        QMessageBox.critical(self, "Error", text)

    def stop(self):
        """Func that stops rendering flying asteroids on plot"""
        self._is_running = False
        self._switch_btns()

    def restart(self):
        """Create new plot with new asteroids"""
        if self._new_asteroids():
            self._is_running = False
            self._switch_btns()

    def _new_asteroids(self) -> bool:
        """Generate new plot and new asteroids"""
        for ky in self.inputs:
            if not self.inputs.get(ky):
                self._error(f"The value of {ky} is 0")
                return False

        values = {key: item.value() for key, item in self.inputs.items()}

        min_value = values.get(SP.MIN_VALUE.value)
        max_value = values.get(SP.MAX_VALUE.value)

        if min_value > max_value:
            self._error("min radius > max radius")
            return False

        if values.get(SP.MIN_SPEED.value) > values.get(SP.MAX_SPEED.value):
            self._error("min speed > max speed")
            return False

        w = values.get(SP.WIDTH.value)
        h = values.get(SP.HEIGHT.value)
        n = int(values.get(SP.COUNT.value))

        r_avg = (min_value + max_value) / 2
        fill = n * math.pi * r_avg**2 / (w * h)

        if fill > 0.30:
            self._error(f"too dense: fill = {fill:.2f} > 0.30")
            return False

        self.asteroid_manager.restart(**values, use_color=self.use_color.isChecked())
        self.view.manager = self.asteroid_manager
        self._update_view()
        return True
