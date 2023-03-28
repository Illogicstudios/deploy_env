import enum
import maya.OpenMaya as OpenMaya

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from utils import *

import ControlRoom as cr
from ControlRoom import *


class FormSliderType(Enum):
    IntSlider = 0
    FloatSlider = 1


class FormSlider:
    def __init__(self, control_room,  type, name, part_name, field_name, key_preset, min, max, mmax=None):
        self.__control_room = control_room
        self.__type = type
        self.__name = name
        self.__part_name = part_name
        self.__field_name = field_name
        self.__key_preset = key_preset
        self.__min = min
        self.__max = max
        self.__mmax = mmax if mmax is not None else max
        self.__mult = 1000 if self.__type == FormSliderType.FloatSlider else 1
        self.__callback = None
        self.__layer_callback = None
        self.__override = None
        self.__action_add_override = QAction(text="Add Override")
        self.__action_add_override.triggered.connect(self.__create_override)
        self.__action_remove_override = QAction(text="Remove Override")
        self.__action_remove_override.triggered.connect(self.__remove_override)

        self.__ui_value_line_edit = None
        self.__ui_slider = None
        self.__ui_lbl_widget = None
        self.__ui_background_widget = None

        self.__retrieve_override()

    # Create an override for the field of the slider
    def __create_override(self):
        obj_attr = self.__field_name.split(".")
        self.__override = cr.ControlRoom.create_override(obj_attr[0], obj_attr[1])

    # Remove the override
    def __remove_override(self):
        cr.ControlRoom.remove_override(self.__override)
        self.__override = None

    # retrieve an override corresponding to the slider
    def __retrieve_override(self):
        obj_attr = self.__field_name.split(".")
        self.__override = cr.ControlRoom.retrieve_override(obj_attr[0], obj_attr[1])

    # On value of slider changed
    def __on_slider_value_changed(self, value):
        if self.__type is FormSliderType.IntSlider:
            value = int(value)
        else:
            value = value / self.__mult
        self.__ui_value_line_edit.setText(str(value))
        setAttr(self.__field_name, value)

    # On value of line edit changed
    def __on_edit_value_changed(self):
        str_value = self.__ui_value_line_edit.text()
        value = float(str_value)
        self.__ui_slider.setValue(value)
        setAttr(self.__field_name, value)

    # Generate the UI for the slider
    def generate_ui(self):
        # Label
        self.__ui_lbl_widget = QLabel(self.__name)
        self.__ui_lbl_widget.setAlignment(Qt.AlignCenter)
        self.__ui_lbl_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__ui_lbl_widget.addAction(self.__action_add_override)
        self.__ui_lbl_widget.addAction(self.__action_remove_override)
        # Background
        self.__ui_background_widget = QWidget()
        self.__ui_background_widget.setObjectName("widget_form_slider")
        lyt = QHBoxLayout(self.__ui_background_widget)
        lyt.setContentsMargins(0, 0, 0, 0)
        # Line Edit
        self.__ui_value_line_edit = QLineEdit()
        if self.__type is FormSliderType.IntSlider:
            validator = QIntValidator(bottom=self.__min, top=self.__mmax)
        else:
            validator = QDoubleValidator(bottom=self.__min, top=self.__mmax, decimals=3)
            locale = QLocale(QLocale.English, QLocale.UnitedStates)
            validator.setLocale(locale)
            validator.setNotation(QDoubleValidator.StandardNotation)
        self.__ui_value_line_edit.setValidator(validator)
        self.__ui_value_line_edit.editingFinished.connect(self.__on_edit_value_changed)
        self.__ui_value_line_edit.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__ui_value_line_edit.addAction(self.__action_add_override)
        self.__ui_value_line_edit.addAction(self.__action_remove_override)
        # Slider
        self.__ui_slider = QSlider(Qt.Horizontal)
        self.__ui_slider.setMaximum(self.__max * self.__mult)
        self.__ui_slider.setMinimum(self.__min * self.__mult)
        self.__ui_slider.valueChanged.connect(self.__on_slider_value_changed)
        self.__ui_slider.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__ui_slider.addAction(self.__action_add_override)
        self.__ui_slider.addAction(self.__action_remove_override)

        lyt.addWidget(self.__ui_value_line_edit, 1)
        lyt.addWidget(self.__ui_slider, 3)
        return self.__ui_lbl_widget, self.__ui_background_widget

    # Refresh the UI
    def refresh_ui(self):
        val = getAttr(self.__field_name)
        if val >= self.__max:
            self.__ui_slider.setMaximum(val * self.__mult)
        self.__ui_slider.setValue(val * self.__mult)
        self.__ui_value_line_edit.setText(str(round(val, 3)))

        visible_layer = render_setup.instance().getVisibleRenderLayer()
        is_default_layer = visible_layer.name() == "defaultRenderLayer"
        self.__action_add_override.setEnabled(not is_default_layer and self.__override is None)
        self.__action_remove_override.setEnabled(not is_default_layer and self.__override is not None)

        stylesheet_bg = "background-color:" + cr.OVERRIDE_BG_COLOR if self.__override is not None else ""
        stylesheet_lbl = self.__control_room.get_stylesheet_color_for_field(
            self.__part_name, self.__key_preset, val, self.__override)
        self.__ui_background_widget.setStyleSheet("QWidget#widget_form_slider{" + stylesheet_bg + "}")
        self.__ui_lbl_widget.setStyleSheet("QLabel{" + stylesheet_lbl + "}")
        self.__retrieve_override()

    # Add callbacks
    def add_callbacks(self):
        self.__callback = scriptJob(attributeChange=[self.__field_name, self.refresh_ui])
        self.__layer_callback = scriptJob(event=["renderLayerManagerChange", self.refresh_ui])

    # remove callbacks
    def remove_callbacks(self):
        scriptJob(kill=self.__callback)
        scriptJob(kill=self.__layer_callback)

    # Getter of the key preset and the field name
    def get_key_preset_and_field(self):
        return self.__key_preset, self.__field_name
