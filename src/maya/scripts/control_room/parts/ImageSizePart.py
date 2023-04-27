import enum
from ..ControlRoomPart import *
from ..FormSlider import *
import pymel.core as pm
from functools import partial

# Aspect Ratio datas
_AspectRatios = {
    "1:1": {"ratio": 1.0, "HD": 1920, "SD": 720},
    "16:9": {"ratio": 1.77777777778, "HD": 1920, "SD": 1280},
    "9:16": {"ratio": 0.5625, "HD": 1080, "SD": 720},
    "4:5": {"ratio": 0.8, "HD": 1536, "SD": 720},
    "Scope": {"ratio": 2.38694638695, "HD": 2048, "SD": 1024},
}


class ImageSizePart(ControlRoomPart):
    def __init__(self, control_room, part_name):
        super(ImageSizePart, self).__init__(control_room, "Image Size", part_name)
        self.__cam = None
        for cam in pm.ls(type="camera"):
            if cam.renderable.get():
                self.__cam = cam
                break
        self.__width_callback = None
        self.__height_callback = None
        self.__aspect_ratio_callback = None
        self.__overscan_callback = None
        self.__ratio_selected = None
        self.__is_gate_opaque = False
        self.__is_gate_enabled = False

        self.__ui_lbl_width = None
        self.__ui_lbl_height = None
        self.__ui_width_edit = None
        self.__ui_height_edit = None
        self.__ui_ratio_btns = {}
        self.__ui_sd_format_btn = None
        self.__ui_hd_format_btn = None
        self.__ui_lbl_overscan = None
        self.__ui_overscan_line_edit = None
        self.__ui_overscan_slider = None
        self.__ui_opaque_gate_cb = None
        self.__ui_enable_gate_cb = None

        self.__retrieve_aspect_ratio()
        if self.__cam is not None : self.add_dynamic_callbacks()

    def populate(self):
        content = QVBoxLayout()
        content.setContentsMargins(4, 4, 2, 0)
        # Width and Height
        size_lyt = QHBoxLayout()
        self.__ui_lbl_width = QLabel("Width")
        size_lyt.addWidget(self.__ui_lbl_width)
        self.__ui_width_edit = QLineEdit()
        self.__ui_width_edit.editingFinished.connect(self.__on_width_changed)
        self.__ui_width_edit.setContentsMargins(0, 0, 10, 0)
        size_lyt.addWidget(self.__ui_width_edit)
        self.__ui_lbl_height = QLabel("Height")
        size_lyt.addWidget(self.__ui_lbl_height)
        self.__ui_height_edit = QLineEdit()
        self.__ui_height_edit.editingFinished.connect(self.__on_height_changed)
        size_lyt.addWidget(self.__ui_height_edit)

        # Aspect Ratios
        ratios_lyt = QHBoxLayout()
        ratios_lyt.setContentsMargins(0, 4, 0, 0)
        for name in _AspectRatios.keys():
            self.__ui_ratio_btns[name] = QPushButton(name)
            self.__ui_ratio_btns[name].clicked.connect(partial(self.__on_click_ratio_btn, name))
            ratios_lyt.addWidget(self.__ui_ratio_btns[name])

        # SD and HD
        format_lyt = QHBoxLayout()
        format_lyt.setContentsMargins(0, 4, 0, 0)
        self.__ui_sd_format_btn = QPushButton("SD")
        self.__ui_sd_format_btn.clicked.connect(partial(self.__on_click_format_btn, "SD"))
        self.__ui_hd_format_btn = QPushButton("HD")
        self.__ui_hd_format_btn.clicked.connect(partial(self.__on_click_format_btn, "HD"))
        format_lyt.addWidget(self.__ui_sd_format_btn)
        format_lyt.addWidget(self.__ui_hd_format_btn)

        # Overscan
        form_lyt = QFormLayout()
        self.__ui_lbl_overscan = QLabel("Overscan")
        lyt = QHBoxLayout()
        self.__ui_overscan_line_edit = QLineEdit()
        min = 0
        max = 10
        validator = QDoubleValidator(bottom=min, top=max, decimals=3)
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        validator.setLocale(locale)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.__ui_overscan_line_edit.setValidator(validator)
        self.__ui_overscan_line_edit.editingFinished.connect(self.__on_overscan_changed)
        self.__ui_overscan_slider = QSlider(Qt.Horizontal)
        self.__ui_overscan_slider.setMaximum(max * 1000)
        self.__ui_overscan_slider.setMinimum(min * 1000)
        self.__ui_overscan_slider.valueChanged.connect(self.__on_slider_overscan_changed)
        lyt.addWidget(self.__ui_overscan_line_edit, 1)
        lyt.addWidget(self.__ui_overscan_slider, 3)
        form_lyt.addRow(self.__ui_lbl_overscan, lyt)

        # Gate
        camera_gate_lyt = QHBoxLayout()
        self.__ui_enable_gate_cb = QCheckBox("Enable Gate")
        self.__ui_enable_gate_cb.stateChanged.connect(self.__on_gate_enable_changed)
        self.__ui_opaque_gate_cb = QCheckBox("Opaque Gate")
        self.__ui_opaque_gate_cb.stateChanged.connect(self.__on_gate_opacity_changed)
        camera_gate_lyt.addWidget(self.__ui_enable_gate_cb, 1)
        camera_gate_lyt.addWidget(self.__ui_opaque_gate_cb, 1)

        content.addLayout(size_lyt)
        content.addLayout(ratios_lyt)
        content.addLayout(format_lyt)
        content.addLayout(form_lyt)
        content.addLayout(camera_gate_lyt)
        return content

    # On line edit Overscan changed
    def __on_overscan_changed(self):
        if self.__cam is not None and not self._preset_hovered:
            self.__cam.overscan.set(float(self.__ui_overscan_line_edit.text()))

    # On slider Overscan changed
    def __on_slider_overscan_changed(self, value):
        if self.__cam is not None and not self.__cam.overscan.isLocked() and not self.__cam.overscan.isConnected():
            value = value / 1000
            if value > 0:
                self.__ui_overscan_line_edit.setText(str(value))
                if not self._preset_hovered:
                    self.__cam.overscan.set(value)

    # On click on an aspect ratio button
    def __on_click_ratio_btn(self, ratio):
        if self.__ratio_selected == ratio:
            self.__ratio_selected = None
        else:
            self.__ratio_selected = ratio
            pm.setAttr("defaultResolution.deviceAspectRatio", _AspectRatios[self.__ratio_selected]["ratio"])
            self.__update_height()
            self.__retrieve_aspect_ratio()
        self.refresh_ui()

    # On click on a format button (SD and HD)
    def __on_click_format_btn(self, format):
        width = _AspectRatios[self.__ratio_selected][format]
        pm.setAttr("defaultResolution.width", width)
        self.__update_height()
        self.__retrieve_aspect_ratio()
        self.refresh_ui()

    # Update the height
    def __update_height(self):
        if self.__ratio_selected is not None:
            pm.setAttr("defaultResolution.height",
                    pm.getAttr("defaultResolution.width") / _AspectRatios[self.__ratio_selected]["ratio"])

    # Update the width
    def __update_width(self):
        if self.__ratio_selected is not None:
            pm.setAttr("defaultResolution.width",
                    pm.getAttr("defaultResolution.height") * _AspectRatios[self.__ratio_selected]["ratio"])

    # Retrieve the aspect ratio
    def __retrieve_aspect_ratio(self):
        self.__ratio_selected = None
        aspect_ratio = pm.getAttr("defaultResolution.deviceAspectRatio")
        for name, aspect_ratio_datas in _AspectRatios.items():
            if abs(aspect_ratio - aspect_ratio_datas["ratio"]) < 0.001:
                self.__ratio_selected = name
                break

    # Update the gate attributes
    def __update_gate_attr(self):
        if self.__cam is not None:
            self.__cam.displayGateMaskOpacity.set(1.0 if self.__is_gate_opaque else 0.7)
            self.__cam.displayGateMaskColor.set((0, 0, 0) if self.__is_gate_opaque else (0.5, 0.5, 0.5))
            self.__cam.displayResolution.set(self.__is_gate_enabled)

    def refresh_ui(self):
        try:
            width_retrieved = pm.getAttr("defaultResolution.width")
            stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                self._part_name, "width", width_retrieved)

            self.__ui_lbl_width.setStyleSheet("QLabel{"+stylesheet_lbl+"}")

            hovered_preset = self._control_room.get_hovered_preset()
            if hovered_preset and hovered_preset.contains(self._part_name, "width"):
                self._preset_hovered = True
                width_displayed = hovered_preset.get(self._part_name, "width")
                self.__ui_width_edit.setText(str(width_displayed))
                self._preset_hovered = False
            else:
                width_displayed = width_retrieved
                self.__ui_width_edit.setText(str(width_retrieved))

            height_retrieved = pm.getAttr("defaultResolution.height")
            stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                self._part_name, "height", height_retrieved)
            self.__ui_lbl_height.setStyleSheet("QLabel{"+stylesheet_lbl+"}")
            if hovered_preset and hovered_preset.contains(self._part_name, "height"):
                self._preset_hovered = True
                height_displayed = hovered_preset.get(self._part_name, "height")
                self.__ui_height_edit.setText(str(height_displayed))
                self._preset_hovered = False
            else:
                height_displayed = height_retrieved
                self.__ui_height_edit.setText(str(height_retrieved))

            aspect_ratio_displayed = width_displayed / height_displayed

            stylesheet_selected = "background-color:#2C2C2C"

            for name, btn in self.__ui_ratio_btns.items():
                if hovered_preset:
                    is_ratio_selected = abs(_AspectRatios[name]["ratio"] - aspect_ratio_displayed) < 0.001
                else:
                    is_ratio_selected = name == self.__ratio_selected
                btn.setStyleSheet(stylesheet_selected if is_ratio_selected else "")

            is_ratio_found = self.__ratio_selected is not None
            self.__ui_sd_format_btn.setEnabled(is_ratio_found)
            self.__ui_hd_format_btn.setEnabled(is_ratio_found)
            sd_selected = is_ratio_found and width_displayed == _AspectRatios[self.__ratio_selected]["SD"]
            hd_selected = is_ratio_found and width_displayed == _AspectRatios[self.__ratio_selected]["HD"]
            self.__ui_sd_format_btn.setStyleSheet(stylesheet_selected if sd_selected else "")
            self.__ui_hd_format_btn.setStyleSheet(stylesheet_selected if hd_selected else "")
            if self.__cam is not None:
                overscan = self.__cam.overscan.get()
                stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                    self._part_name, "overscan", overscan)
                self.__ui_lbl_overscan.setStyleSheet("QLabel{"+stylesheet_lbl+"}")

                if hovered_preset and hovered_preset.contains(self._part_name, "overscan"):
                    self._preset_hovered = True
                    overscan_displayed = hovered_preset.get(self._part_name, "overscan")
                    self.__ui_overscan_slider.setValue(overscan_displayed * 1000)
                    self._preset_hovered = False
                else:
                    self.__ui_overscan_slider.setValue(overscan * 1000)

            self.__ui_overscan_slider.setEnabled(self.__cam is not None and not self.__cam.overscan.isLocked()
                                                 and not self.__cam.overscan.isConnected())
            self.__ui_overscan_line_edit.setEnabled(self.__cam is not None and not self.__cam.overscan.isLocked()
                                                 and not self.__cam.overscan.isConnected())
            self.__ui_enable_gate_cb.setEnabled(self.__cam is not None and not self.__cam.displayResolution.isLocked()
                                                and not self.__cam.displayResolution.isConnected())
            self.__ui_opaque_gate_cb.setEnabled(
                self.__cam is not None and not self.__cam.displayGateMaskOpacity.isLocked()
                and not self.__cam.displayGateMaskOpacity.isConnected()
                and not self.__cam.displayGateMaskColor.isConnected())

            stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                self._part_name, "enable_gate", self.__is_gate_enabled)
            self.__ui_enable_gate_cb.setStyleSheet("QCheckBox{"+stylesheet_lbl+"}")
            if hovered_preset and hovered_preset.contains(self._part_name, "enable_gate"):
                self._preset_hovered = True
                self.__ui_enable_gate_cb.setChecked(hovered_preset.get(self._part_name, "enable_gate"))
                self._preset_hovered = False
            else:
                self.__ui_enable_gate_cb.setChecked(self.__is_gate_enabled)

            stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                self._part_name, "opaque_gate", self.__is_gate_opaque)
            self.__ui_opaque_gate_cb.setStyleSheet("QCheckBox{"+stylesheet_lbl+"}")
            if hovered_preset and hovered_preset.contains(self._part_name, "opaque_gate"):
                self._preset_hovered = True
                self.__ui_opaque_gate_cb.setChecked(hovered_preset.get(self._part_name, "opaque_gate"))
                self._preset_hovered = False
            else:
                self.__ui_opaque_gate_cb.setChecked(self.__is_gate_opaque)
        except:
            pass

    # On checkbox gate enable changed
    def __on_gate_enable_changed(self, state):
        if not self._preset_hovered:
            self.__is_gate_enabled = state == 2
            self.__update_gate_attr()

    # On checkbox gate opacity changed
    def __on_gate_opacity_changed(self, state):
        if not self._preset_hovered:
            self.__is_gate_opaque = state == 2
            self.__update_gate_attr()

    # On line edit width changed
    def __on_width_changed(self):
        if not self._preset_hovered:
            pm.setAttr("defaultResolution.width", int(self.__ui_width_edit.text()))
            self.__update_height()

    # On line edit height changed
    def __on_height_changed(self):
        if not self._preset_hovered:
            pm.setAttr("defaultResolution.height", int(self.__ui_height_edit.text()))
            self.__update_width()

    # Callback that retrieve data and refresh UI
    def __callback(self):
        self.__retrieve_aspect_ratio()
        self.refresh_ui()

    def add_callbacks(self):
        self.__width_callback = pm.scriptJob(
            attributeChange=["defaultResolution.width", self.__callback])
        self.__height_callback = pm.scriptJob(
            attributeChange=["defaultResolution.height", self.__callback])
        self.__aspect_ratio_callback = pm.scriptJob(
            attributeChange=["defaultResolution.deviceAspectRatio", self.__callback])

    # Add dynamic callback for the camera
    def add_dynamic_callbacks(self):
        if self.__cam is not None:
            self.__overscan_callback = pm.scriptJob(
                attributeChange=[self.__cam + '.overscan', self.__callback])

    def remove_callbacks(self):
        pm.scriptJob(kill=self.__width_callback)
        pm.scriptJob(kill=self.__height_callback)
        pm.scriptJob(kill=self.__aspect_ratio_callback)
        self.remove_dynamic_callbacks()

    # Remove dynamic callback for the camera
    def remove_dynamic_callbacks(self):
        if self.__overscan_callback is not None:
            pm.scriptJob(kill=self.__overscan_callback)
            self.__overscan_callback = None

    # retrieve the gate attributes
    def __retrieve_gate_attr(self):
        if self.__cam is not None:
            self.__is_gate_enabled = self.__cam.displayResolution.get()
            self.__is_gate_opaque = self.__cam.displayGateMaskOpacity.get() == 1.0

    def add_to_preset(self, preset):
        preset.set(self._part_name, "width", pm.getAttr("defaultResolution.width"))
        preset.set(self._part_name, "height", pm.getAttr("defaultResolution.height"))
        if self.__cam is not None:
            preset.set(self._part_name, "overscan", self.__cam.overscan.get())
            preset.set(self._part_name, "opaque_gate", self.__is_gate_opaque)
            preset.set(self._part_name, "enable_gate", self.__is_gate_enabled)

    def apply(self, preset):
        if preset.contains(self._part_name, "width"):
            width = preset.get(self._part_name, "width")
            pm.setAttr("defaultResolution.width", width)
        if preset.contains(self._part_name, "height"):
            height = preset.get(self._part_name, "height")
            pm.setAttr("defaultResolution.height", height)
        pm.setAttr("defaultResolution.deviceAspectRatio",
                   pm.getAttr("defaultResolution.width") / pm.getAttr("defaultResolution.height"))
        self.__retrieve_aspect_ratio()
        if self.__cam is not None:
            if preset.contains(self._part_name, "overscan"):
                self.__cam.overscan.set(preset.get(self._part_name, "overscan"))
            if preset.contains(self._part_name, "opaque_gate"):
                self.__is_gate_opaque = preset.get(self._part_name, "opaque_gate") == 1
            if preset.contains(self._part_name, "enable_gate"):
                self.__is_gate_enabled = preset.get(self._part_name, "enable_gate")
            self.__update_gate_attr()
