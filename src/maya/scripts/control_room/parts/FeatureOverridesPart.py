import ControlRoom as cr
from ControlRoom import *
from ControlRoomPart import *
from pymel.core import *


class IgnoreFields:
    def __init__(self, control_room, name, part_name, field_name, key_preset=None):
        self.__control_room = control_room
        self.__name = name
        self.__part_name = part_name
        self.__field_name = field_name
        self.__key_preset = key_preset
        self.__checkbox = None
        self.__callback = None
        self.__layer_callback = None
        self.__override = None
        self.__preset_hovered = False
        self.__action_add_override = QAction(text="Add Override")
        self.__action_add_override.triggered.connect(self.__create_override)
        self.__action_remove_override = QAction(text="Remove Override")
        self.__action_remove_override.triggered.connect(self.__remove_override)
        self.__retrieve_override()

    # Create an override for the field of the checkbox
    def __create_override(self):
        obj_attr = self.__field_name.split(".")
        self.__override = cr.ControlRoom.create_override(obj_attr[0], obj_attr[1])

    # Remove the override of the field of the checkbox
    def __remove_override(self):
        cr.ControlRoom.remove_override(self.__override)
        self.__override = None

    # Retrieve the override of the field of the checkbox
    def __retrieve_override(self):
        obj_attr = self.__field_name.split(".")
        self.__override = cr.ControlRoom.retrieve_override(obj_attr[0], obj_attr[1])

    # On checkbox changed
    def __on_state_changed(self, state):
        if not self.__preset_hovered:
            setAttr(self.__field_name, state == 2)

    # Getter of the key preset and the field
    def get_key_preset_and_field(self):
        return self.__key_preset, self.__field_name

    # Generate the checkbox
    def generate_checkbox(self):
        self.__checkbox = QCheckBox(self.__name)
        self.__checkbox.stateChanged.connect(self.__on_state_changed)
        self.__checkbox.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__checkbox.addAction(self.__action_add_override)
        self.__checkbox.addAction(self.__action_remove_override)
        return self.__checkbox

    # Refresh the checkbox
    def refresh_checkbox(self):
        try:
            visible_layer = render_setup.instance().getVisibleRenderLayer()
            is_default_layer = visible_layer.name() == "defaultRenderLayer"
            val = getAttr(self.__field_name)

            hovered_preset = self.__control_room.get_hovered_preset()
            if hovered_preset and hovered_preset.contains(self.__part_name, self.__key_preset):
                self.__preset_hovered = True
                self.__checkbox.setChecked(hovered_preset.get(self.__part_name, self.__key_preset))
                self.__preset_hovered = False
            else:
                self.__checkbox.setChecked(val)

            self.__action_add_override.setEnabled(not is_default_layer and self.__override is None)
            self.__action_remove_override.setEnabled(not is_default_layer and self.__override is not None)

            stylesheet_lbl = self.__control_room.get_stylesheet_color_for_field(self.__part_name, self.__key_preset, val, self.__override)
            self.__checkbox.setStyleSheet("QCheckBox{" + stylesheet_lbl + "}")

            self.__retrieve_override()
        except:
            pass

    def add_callback(self):
        self.__callback = scriptJob(attributeChange=[self.__field_name, self.refresh_checkbox])
        self.__layer_callback = scriptJob(event=["renderLayerManagerChange", self.refresh_checkbox])

    def remove_callback(self):
        scriptJob(kill=self.__callback)
        scriptJob(kill=self.__layer_callback)


class FeatureOverridesPart(ControlRoomPart):
    def __init__(self, control_room, part_name):
        super(FeatureOverridesPart, self).__init__(control_room, "Feature Overrides", part_name)
        self.__ignore_fields = [
            IgnoreFields(self._control_room, "Ignore Athmosphere", part_name,
                         "defaultArnoldRenderOptions.ignoreAtmosphere", "ignore_athmosphere"),
            IgnoreFields(self._control_room, "Ignore Subdivision", part_name,
                         "defaultArnoldRenderOptions.ignoreSubdivision", "ignore_subdivision"),
            IgnoreFields(self._control_room, "Ignore Displacement", part_name,
                         "defaultArnoldRenderOptions.ignoreDisplacement", "ignore_displacement"),
            IgnoreFields(self._control_room, "Ignore Motion", part_name,
                         "defaultArnoldRenderOptions.ignoreMotion", "ignore_motion"),
            IgnoreFields(self._control_room, "Ignore Depth of field", part_name,
                         "defaultArnoldRenderOptions.ignoreDof", "ignore_dof")
        ]
        self.__ignore_aovs = False

        self.__ui_ignore_aovs_cb = None
        self.__ui_output_denoising_aovs_cb = None

        self.__arnold_render_callback = None

    def populate(self):
        content = QHBoxLayout()
        content.setContentsMargins(5, 5, 5, 5)
        content.setSizeConstraint(QLayout.SetNoConstraint)
        left_content = QVBoxLayout()
        content.addLayout(left_content, 1)
        right_content = QVBoxLayout()
        content.addLayout(right_content, 1)

        # Ignore fields
        for ign_field in self.__ignore_fields:
            left_content.addWidget(ign_field.generate_checkbox())

        # Ignore AOVs
        self.__ui_ignore_aovs_cb = QCheckBox("AOVs Batch Only")
        self.__ignore_aovs = getAttr("defaultArnoldRenderOptions.aovMode") == 2
        self.__ui_ignore_aovs_cb.setChecked(self.__ignore_aovs)
        self.__ui_ignore_aovs_cb.stateChanged.connect(self.__on_state_changed_ignore_aovs)
        self.__ui_ignore_aovs_cb.setChecked(self.__ignore_aovs)
        right_content.addWidget(self.__ui_ignore_aovs_cb)

        # Output denoising
        self.__ui_output_denoising_aovs_cb = QCheckBox("Output Denoising AOVs")
        self.__ui_output_denoising_aovs_cb.stateChanged.connect(self.__on_state_changed_output_denoising_aovs)
        right_content.addWidget(self.__ui_output_denoising_aovs_cb)

        return content

    def refresh_ui(self):
        try:
            self.__refresh_ignore_fields()
            self.__refresh_ignore_aov()
            self.__refresh_output_denoising_aov()
        except:
            pass

    # Refresh all the ignore fields
    def __refresh_ignore_fields(self):
        for ign_field in self.__ignore_fields:
            ign_field.refresh_checkbox()

    # Refresh the ignore aovs field
    def __refresh_ignore_aov(self):
        stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
            self._part_name, "ignore_aovs", self.__ignore_aovs)
        self.__ui_ignore_aovs_cb.setStyleSheet("QCheckBox{" + stylesheet_lbl + "}")
        hovered_preset = self._control_room.get_hovered_preset()
        if hovered_preset and hovered_preset.contains(self._part_name, "ignore_aovs"):
            self._preset_hovered = True
            self.__ui_ignore_aovs_cb.setChecked(hovered_preset.get(self._part_name, "ignore_aovs"))
            self._preset_hovered = False
        else:
            self.__ui_ignore_aovs_cb.setChecked(self.__ignore_aovs)

    # Refresh the output denoising aov field
    def __refresh_output_denoising_aov(self):
        checked = ls("defaultArnoldRenderOptions")[0].outputVarianceAOVs.get()
        stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
            self._part_name, "output_denoising", checked)
        self.__ui_output_denoising_aovs_cb.setStyleSheet("QCheckBox{" + stylesheet_lbl + "}")

        hovered_preset = self._control_room.get_hovered_preset()
        if hovered_preset and hovered_preset.contains(self._part_name, "output_denoising"):
            self._preset_hovered = True
            self.__ui_output_denoising_aovs_cb.setChecked(hovered_preset.get(self._part_name, "output_denoising"))
            self._preset_hovered = False
        else:
            self.__ui_output_denoising_aovs_cb.setChecked(checked)

    # On ignore aov checkbox changed
    def __on_state_changed_ignore_aovs(self, state):
        if not self._preset_hovered:
            self.__ignore_aovs = state == 2
            setAttr("defaultArnoldRenderOptions.aovMode", 2 if self.__ignore_aovs else 1)
            self.__refresh_ignore_aov()

    # On output denoising aov checkbox changed
    def __on_state_changed_output_denoising_aovs(self, state):
        if not self._preset_hovered:
            enabled = state == 2
            ls("defaultArnoldRenderOptions")[0].outputVarianceAOVs.set(enabled)
            if objExists("defaultArnoldDriver"):
                multipart = True
                if enabled:
                    multipart = False
                else:
                    cameras = ls(type="camera")
                    for cam in cameras:
                        if cam.ai_translator.get() == "lentil_camera":
                            multipart = False
                            break
                half_driver = ls("defaultArnoldDriver", type="aiAOVDriver")[0]
                half_driver.multipart.set(multipart)

            self.__refresh_output_denoising_aov()

    def add_callbacks(self):
        self.__arnold_render_callback = scriptJob(
            attributeChange=['defaultArnoldRenderOptions.outputVarianceAOVs', self.__refresh_output_denoising_aov])
        for ign_field in self.__ignore_fields:
            ign_field.add_callback()

    def remove_callbacks(self):
        scriptJob(kill=self.__arnold_render_callback)

        for ign_field in self.__ignore_fields:
            ign_field.remove_callback()

    def add_to_preset(self, preset):
        for ign_field in self.__ignore_fields:
            key, field = ign_field.get_key_preset_and_field()
            if key:
                preset.set(self._part_name, key, getAttr(field))
        preset.set(self._part_name, "ignore_aovs", self.__ignore_aovs)
        preset.set(self._part_name, "output_denoising", getAttr("defaultArnoldRenderOptions.outputVarianceAOVs"))

    def apply(self, preset):
        for ign_field in self.__ignore_fields:
            key, field = ign_field.get_key_preset_and_field()
            if key and preset.contains(self._part_name, key):
                setAttr(field, preset.get(self._part_name, key))
        if preset.contains(self._part_name, "ignore_aovs"):
            self.__ignore_aovs = preset.get(self._part_name, "ignore_aovs")
            setAttr("defaultArnoldRenderOptions.aovMode", 2 if self.__ignore_aovs else 1)
        if preset.contains(self._part_name, "output_denoising"):
            setAttr("defaultArnoldRenderOptions.outputVarianceAOVs", preset.get(self._part_name, "output_denoising"))
