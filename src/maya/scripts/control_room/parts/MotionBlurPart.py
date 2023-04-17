from ControlRoomPart import *
from FormSlider import *
import pymel.core as pm


class MotionBlurPart(ControlRoomPart):
    def __init__(self, control_room, part_name):
        super(MotionBlurPart, self).__init__(control_room, "Motion Blur", part_name)
        self.__form_sliders = [
            FormSlider(self._control_room, FormSliderType.IntSlider, "Keys", part_name,
                       "defaultArnoldRenderOptions.motion_steps", "motion_blur_keys", 2, 30, 300),
            FormSlider(self._control_room, FormSliderType.FloatSlider, "Motion Step", part_name,
                       "defaultArnoldRenderOptions.motion_frames", "motion_blur_step", 0, 1),
        ]
        self.__ui_motion_blur_cb = None
        self.__ui_instant_shutter_cb = None
        self.__motion_blur_callback = None
        self.__instant_shutter_callback = None
        self.__layer_callback = None
        self.__motion_blur_override = None
        self.__instant_shutter_override = None
        self.__action_add_motion_blur_override = QAction(text="Add Override")
        self.__action_add_motion_blur_override.triggered.connect(self.__create_motion_blur_override)
        self.__action_remove_motion_blur_override = QAction(text="Remove Override")
        self.__action_remove_motion_blur_override.triggered.connect(self.__remove_motion_blur_override)

        self.__action_add_instant_shutter_override = QAction(text="Add Override")
        self.__action_add_instant_shutter_override.triggered.connect(self.__create_instant_shutter_override)
        self.__action_remove_instant_shutter_override = QAction(text="Remove Override")
        self.__action_remove_instant_shutter_override.triggered.connect(self.__remove_instant_shutter_override)

        self.__retrieve_motion_blur_override()
        self.__retrieve_instant_shutter_override()

    # Create the enable motion blur override
    def __create_motion_blur_override(self):
        self.__motion_blur_override = \
            cr.ControlRoom.create_override("defaultArnoldRenderOptions", "motion_blur_enable")

    # Remove the enable motion blur override
    def __remove_motion_blur_override(self):
        cr.ControlRoom.remove_override(self.__motion_blur_override)
        self.__motion_blur_override = None

    # Retrieve the enable motion blur override
    def __retrieve_motion_blur_override(self):
        self.__motion_blur_override = \
            cr.ControlRoom.retrieve_override("defaultArnoldRenderOptions", "motion_blur_enable")

    # Create the instant shutter override
    def __create_instant_shutter_override(self):
        self.__instant_shutter_override = \
            cr.ControlRoom.create_override("defaultArnoldRenderOptions", "ignoreMotionBlur")

    # Remove the instant shutter override
    def __remove_instant_shutter_override(self):
        cr.ControlRoom.remove_override(self.__instant_shutter_override)
        self.__instant_shutter_override = None

    # Retrieve the instant shutter override
    def __retrieve_instant_shutter_override(self):
        self.__instant_shutter_override = \
            cr.ControlRoom.retrieve_override("defaultArnoldRenderOptions", "ignoreMotionBlur")

    def populate(self):
        content = QVBoxLayout()
        content.setContentsMargins(4, 4, 1, 4)

        lyt_cb = QHBoxLayout()
        self.__ui_motion_blur_cb = QCheckBox("Enable Motion Blur")
        self.__ui_motion_blur_cb.stateChanged.connect(self.__on_motion_blur_changed)
        self.__ui_motion_blur_cb.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__ui_motion_blur_cb.addAction(self.__action_add_motion_blur_override)
        self.__ui_motion_blur_cb.addAction(self.__action_remove_motion_blur_override)
        lyt_cb.addWidget(self.__ui_motion_blur_cb)
        self.__ui_instant_shutter_cb = QCheckBox("Instantaneous Shutter")
        self.__ui_instant_shutter_cb.stateChanged.connect(self.__on_instant_shutter_changed)
        self.__ui_instant_shutter_cb.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__ui_instant_shutter_cb.addAction(self.__action_add_instant_shutter_override)
        self.__ui_instant_shutter_cb.addAction(self.__action_remove_instant_shutter_override)
        lyt_cb.addWidget(self.__ui_instant_shutter_cb)
        content.addLayout(lyt_cb)

        form_layout = QFormLayout()
        content.addLayout(form_layout)

        for fs in self.__form_sliders:
            lbl, slider = fs.generate_ui()
            form_layout.addRow(lbl, slider)
        return content

    def refresh_ui(self):
        try:
            motion_blur_enable  = pm.getAttr("defaultArnoldRenderOptions.motion_blur_enable")
            ignore_motion_blur = pm.getAttr("defaultArnoldRenderOptions.ignoreMotionBlur")

            hovered_preset = self._control_room.get_hovered_preset()
            if hovered_preset and hovered_preset.contains(self._part_name, "enable_motion_blur"):
                self._preset_hovered = True
                self.__ui_motion_blur_cb.setChecked(hovered_preset.get(self._part_name, "enable_motion_blur"))
                self._preset_hovered = False
            else:
                self.__ui_motion_blur_cb.setChecked(motion_blur_enable)

            if hovered_preset and hovered_preset.contains(self._part_name, "instant_shutter"):
                self._preset_hovered = True
                self.__ui_instant_shutter_cb.setChecked(hovered_preset.get(self._part_name, "instant_shutter"))
                self._preset_hovered = False
            else:
                self.__ui_instant_shutter_cb.setChecked(ignore_motion_blur)

            for fs in self.__form_sliders:
                fs.refresh_ui()

            visible_layer = render_setup.instance().getVisibleRenderLayer()
            is_default_layer = visible_layer.name() == "defaultRenderLayer"
            self.__action_add_motion_blur_override.setEnabled(
                not is_default_layer and self.__motion_blur_override is None)
            self.__action_remove_motion_blur_override.setEnabled(
                not is_default_layer and self.__motion_blur_override is not None)
            self.__action_add_instant_shutter_override.setEnabled(
                not is_default_layer and self.__instant_shutter_override is None)
            self.__action_remove_instant_shutter_override.setEnabled(
                not is_default_layer and self.__instant_shutter_override is not None)

            motion_blur_stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                self._part_name, "enable_motion_blur", motion_blur_enable, self.__motion_blur_override)
            self.__ui_motion_blur_cb.setStyleSheet("QCheckBox{" + motion_blur_stylesheet_lbl + "}")

            instant_shutter_stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                self._part_name, "instant_shutter", ignore_motion_blur, self.__instant_shutter_override)
            self.__ui_instant_shutter_cb.setStyleSheet("QCheckBox{" + instant_shutter_stylesheet_lbl + "}")
            self.__retrieve_motion_blur_override()
            self.__retrieve_instant_shutter_override()
        except:
            pass

    # On motion blur enable checkbox changed
    def __on_motion_blur_changed(self, state):
        if not self._preset_hovered:
            pm.setAttr("defaultArnoldRenderOptions.motion_blur_enable", state == 2)

    # On instant shutter checkbox changed
    def __on_instant_shutter_changed(self, state):
        if not self._preset_hovered:
            pm.setAttr("defaultArnoldRenderOptions.ignoreMotionBlur", state == 2)

    def add_callbacks(self):
        self.__motion_blur_callback = pm.scriptJob(
            attributeChange=["defaultArnoldRenderOptions.motion_blur_enable", self.refresh_ui])
        self.__instant_shutter_callback = pm.scriptJob(
            attributeChange=["defaultArnoldRenderOptions.ignoreMotionBlur", self.refresh_ui])
        for fs in self.__form_sliders:
            fs.add_callbacks()
        self.__layer_callback = pm.scriptJob(event=["renderLayerManagerChange", self.refresh_ui])

    def remove_callbacks(self):
        pm.scriptJob(kill=self.__motion_blur_callback)
        pm.scriptJob(kill=self.__instant_shutter_callback)
        for fs in self.__form_sliders:
            fs.remove_callbacks()
        pm.scriptJob(kill=self.__layer_callback)

    def add_to_preset(self, preset):
        preset.set(self._part_name, "enable_motion_blur", pm.getAttr("defaultArnoldRenderOptions.motion_blur_enable"))
        preset.set(self._part_name, "instant_shutter", pm.getAttr("defaultArnoldRenderOptions.ignoreMotionBlur"))
        for fs in self.__form_sliders:
            key, field = fs.get_key_preset_and_field()
            preset.set(self._part_name, key, pm.getAttr(field))

    def apply(self, preset):
        if preset.contains(self._part_name, "enable_motion_blur"):
            pm.setAttr("defaultArnoldRenderOptions.motion_blur_enable", preset.get(self._part_name, "enable_motion_blur"))
        if preset.contains(self._part_name, "instant_shutter"):
            pm.setAttr("defaultArnoldRenderOptions.ignoreMotionBlur", preset.get(self._part_name, "instant_shutter"))
        for fs in self.__form_sliders:
            key, field = fs.get_key_preset_and_field()
            if preset.contains(self._part_name, key):
                pm.setAttr(field, preset.get(self._part_name, key))
