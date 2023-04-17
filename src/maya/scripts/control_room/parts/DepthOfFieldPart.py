import ControlRoom as cr
from ControlRoom import *
from ControlRoomPart import *
import pymel.core as pm


class DepthOfFieldPart(ControlRoomPart):
    def __init__(self, control_room, part_name):
        super(DepthOfFieldPart, self).__init__(control_room, "Depth of Field", part_name)
        self.__no_refresh = False
        self.__cam = None
        for cam in pm.ls(type="camera"):
            if cam.renderable.get():
                self.__cam = cam
                break
        self.__ui_dof_cb = None
        self.__ui_lbl_fstop = None
        self.__ui_line_edit_fstop = None
        self.__camera_dof_callback = None
        self.__camera_fstop_callback = None
        if self.__cam is not None : self.add_dynamic_callbacks()

    def populate(self):
        content = QHBoxLayout()
        content.setContentsMargins(4, 4, 1, 4)

        self.__ui_dof_cb = QCheckBox("Depth of field")
        self.__ui_dof_cb.stateChanged.connect(self.__on_dof_changed)
        content.addWidget(self.__ui_dof_cb, 1, Qt.AlignLeft)

        form_layout = QFormLayout()
        content.addLayout(form_layout, 2)

        self.__ui_lbl_fstop = QLabel("FStop")
        self.__ui_line_edit_fstop = QLineEdit()
        validator = QDoubleValidator(bottom=1, top=64, decimals=3)
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        validator.setLocale(locale)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.__ui_line_edit_fstop.setValidator(validator)
        self.__ui_line_edit_fstop.editingFinished.connect(self.__on_fstop_changed)
        form_layout.addRow(self.__ui_lbl_fstop, self.__ui_line_edit_fstop)
        return content

    def refresh_ui(self):
        try:
            dof_checked = False
            if self.__cam is not None and not self.__no_refresh:
                dof_checked = self.__cam.depthOfField.get()

                stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                    self._part_name, "depth_of_field", dof_checked)
                self.__ui_dof_cb.setStyleSheet("QCheckBox{" + stylesheet_lbl + "}")

                hovered_preset = self._control_room.get_hovered_preset()
                if hovered_preset and hovered_preset.contains(self._part_name, "depth_of_field"):
                    self._preset_hovered = True
                    self.__ui_dof_cb.setChecked(hovered_preset.get(self._part_name, "depth_of_field"))
                    self._preset_hovered = False
                else:
                    self.__ui_dof_cb.setChecked(dof_checked)

                f_stop = round(self.__cam.fStop.get(), 3)
                stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                    self._part_name, "f_stop", f_stop)
                self.__ui_lbl_fstop.setStyleSheet("QLabel{" + stylesheet_lbl + "}")
                self.__ui_line_edit_fstop.setEnabled(dof_checked)

                if hovered_preset and hovered_preset.contains(self._part_name, "f_stop"):
                    self._preset_hovered = True
                    self.__ui_line_edit_fstop.setText(str(hovered_preset.get(self._part_name, "f_stop")))
                    self._preset_hovered = False
                else:
                    self.__ui_line_edit_fstop.setText(str(f_stop))
            self.__ui_dof_cb.setEnabled(self.__cam is not None and not self.__cam.depthOfField.isLocked())
            self.__ui_line_edit_fstop.setEnabled(self.__cam is not None and dof_checked and not self.__cam.fStop.isLocked())
        except:
            pass

    # On checkbox Depth of Field changed
    def __on_dof_changed(self, state):
        if self.__cam is not None and not self._preset_hovered:
            self.__no_refresh = True
            self.__cam.depthOfField.set(state == 2)
            self.__no_refresh = False

    # On FStop line edit changed
    def __on_fstop_changed(self):
        if self.__cam is not None and not self._preset_hovered:
            self.__no_refresh = True
            self.__cam.fStop.set(float(self.__ui_line_edit_fstop.text()))
            self.__no_refresh = False

    def add_callbacks(self):
        # Nothing
        pass

    # Add callbacks to the current camera
    def add_dynamic_callbacks(self):
        if self.__cam is not None:
            self.__camera_dof_callback = pm.scriptJob(
                attributeChange=[self.__cam + '.depthOfField', self.refresh_ui])
            self.__camera_fstop_callback = pm.scriptJob(
                attributeChange=[self.__cam + '.fStop', self.refresh_ui])

    # Remove the callbacks from the current camera
    def remove_callbacks(self):
        if self.__camera_dof_callback is not None:
            pm.scriptJob(kill=self.__camera_dof_callback)
            self.__camera_dof_callback = None
        if self.__camera_fstop_callback is not None:
            pm.scriptJob(kill=self.__camera_fstop_callback)
            self.__camera_fstop_callback = None

    def add_to_preset(self, preset):
        if self.__cam is not None:
            preset.set(self._part_name, "depth_of_field", self.__cam.depthOfField.get())
            preset.set(self._part_name, "f_stop", self.__cam.fStop.get())

    def apply(self, preset):
        if self.__cam is not None:
            if preset.contains(self._part_name, "depth_of_field"):
                self.__cam.depthOfField.set(preset.get(self._part_name, "depth_of_field"))
            if preset.contains(self._part_name, "f_stop"):
                self.__cam.fStop.set(preset.get(self._part_name, "f_stop"))
