from ControlRoomPart import *
from FormSlider import *
import pymel.core as pm


class SamplingPart(ControlRoomPart):
    def __init__(self, control_room, part_name):
        super(SamplingPart, self).__init__(control_room, "Sampling", part_name)
        self.__form_sliders = [
            FormSlider(self._control_room, FormSliderType.IntSlider, "Camera (AA)", part_name,
                       "defaultArnoldRenderOptions.AASamples", "camera_aa", 0, 10, 100),
            FormSlider(self._control_room, FormSliderType.IntSlider, "Diffuse", part_name,
                       "defaultArnoldRenderOptions.GIDiffuseSamples", "diffuse", 0, 10, 100),
            FormSlider(self._control_room, FormSliderType.IntSlider, "Specular", part_name,
                       "defaultArnoldRenderOptions.GISpecularSamples", "specular", 0, 10, 100),
            FormSlider(self._control_room, FormSliderType.IntSlider, "Transmission", part_name,
                       "defaultArnoldRenderOptions.GITransmissionSamples", "transmission", 0, 10, 100),
            FormSlider(self._control_room, FormSliderType.IntSlider, "SSS", part_name,
                       "defaultArnoldRenderOptions.GISssSamples", "sss", 0, 10, 100),
            FormSlider(self._control_room, FormSliderType.IntSlider, "Volume Indirect", part_name,
                       "defaultArnoldRenderOptions.GIVolumeSamples", "volume_indirect", 0, 10, 100),
            FormSlider(self._control_room, FormSliderType.IntSlider, "Ray Depth Diffuse", part_name,
                       "defaultArnoldRenderOptions.GIDiffuseDepth", "ray_depth_diffuse", 0, 16, 160),
            FormSlider(self._control_room, FormSliderType.IntSlider, "Ray Depth Specular", part_name,
                       "defaultArnoldRenderOptions.GISpecularDepth", "ray_depth_specular", 0, 16, 160),
        ]
        self.__ui_progressive_render_cb = None
        self.__progressive_render_callback = None
        self.__layer_callback = None

        self.__progressive_render_override = None
        self.__action_add_progressive_render_override = QAction(text="Add Override")
        self.__action_add_progressive_render_override.triggered.connect(self.__create_progressive_render_override)
        self.__action_remove_progressive_render_override = QAction(text="Remove Override")
        self.__action_remove_progressive_render_override.triggered.connect(self.__remove_progressive_render_override)

        self.__retrieve_progressive_render_override()

    # Create progressive render override
    def __create_progressive_render_override(self):
        self.__progressive_render_override = cr.ControlRoom.create_override("defaultArnoldRenderOptions",
                                                                            "enableProgressiveRender")

    # Remove progressive render override
    def __remove_progressive_render_override(self):
        cr.ControlRoom.remove_override(self.__progressive_render_override)
        self.__progressive_render_override = None

    # Retrieve progressive render override
    def __retrieve_progressive_render_override(self):
        self.__progressive_render_override = cr.ControlRoom.retrieve_override("defaultArnoldRenderOptions",
                                                                              "enableProgressiveRender")

    def populate(self):
        content = QVBoxLayout()
        content.setContentsMargins(4, 4, 1, 4)

        self.__ui_progressive_render_cb = QCheckBox("Enable Progressive Render")
        self.__ui_progressive_render_cb.stateChanged.connect(self.__on_progressive_render_changed)
        self.__ui_progressive_render_cb.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.__ui_progressive_render_cb.addAction(self.__action_add_progressive_render_override)
        self.__ui_progressive_render_cb.addAction(self.__action_remove_progressive_render_override)

        content.addWidget(self.__ui_progressive_render_cb)

        form_layout = QFormLayout()
        content.addLayout(form_layout)

        for fs in self.__form_sliders:
            lbl, slider = fs.generate_ui()
            form_layout.addRow(lbl, slider)
        return content

    def refresh_ui(self):
        try:
            visible_layer = render_setup.instance().getVisibleRenderLayer()
            is_default_layer = visible_layer.name() == "defaultRenderLayer"
            progressive_render_enabled = pm.getAttr("defaultArnoldRenderOptions.enableProgressiveRender")

            hovered_preset = self._control_room.get_hovered_preset()
            if hovered_preset and hovered_preset.contains(self._part_name, "enable_progressive_render"):
                self._preset_hovered = True
                self.__ui_progressive_render_cb.setChecked(hovered_preset.get(self._part_name, "enable_progressive_render"))
                self._preset_hovered = False
            else:
                self.__ui_progressive_render_cb.setChecked(progressive_render_enabled)

            for fs in self.__form_sliders:
                fs.refresh_ui()

            self.__action_add_progressive_render_override.setEnabled(
                not is_default_layer and self.__progressive_render_override is None)
            self.__action_remove_progressive_render_override.setEnabled(
                not is_default_layer and self.__progressive_render_override is not None)

            stylesheet_lbl = self._control_room.get_stylesheet_color_for_field(
                self._part_name, "enable_progressive_render",
                progressive_render_enabled, self.__progressive_render_override)
            self.__ui_progressive_render_cb.setStyleSheet("QCheckBox{" + stylesheet_lbl + "}")
            self.__retrieve_progressive_render_override()
        except:
            pass

    # On enable progressive render checkbox changed
    def __on_progressive_render_changed(self, state):
        if not self._preset_hovered:
            pm.setAttr("defaultArnoldRenderOptions.enableProgressiveRender", state == 2)

    def add_callbacks(self):
        self.__progressive_render_callback = pm.scriptJob(
            attributeChange=["defaultArnoldRenderOptions.enableProgressiveRender", self.refresh_ui])
        for fs in self.__form_sliders:
            fs.add_callbacks()
        self.__layer_callback = pm.scriptJob(event=["renderLayerManagerChange", self.refresh_ui])

    def remove_callbacks(self):
        pm.scriptJob(kill=self.__progressive_render_callback)
        for fs in self.__form_sliders:
            fs.remove_callbacks()
        pm.scriptJob(kill=self.__layer_callback)

    def add_to_preset(self, preset):
        preset.set(self._part_name, "enable_progressive_render", pm.getAttr("defaultArnoldRenderOptions.enableProgressiveRender"))
        for fs in self.__form_sliders:
            key, field = fs.get_key_preset_and_field()
            preset.set(self._part_name, key, pm.getAttr(field))

    def apply(self, preset):
        if preset.contains(self._part_name, "enable_progressive_render"):
            pm.setAttr("defaultArnoldRenderOptions.enableProgressiveRender", preset.get(self._part_name, "enable_progressive_render"))
        for fs in self.__form_sliders:
            key, field = fs.get_key_preset_and_field()
            if preset.contains(self._part_name, key):
                pm.setAttr(field, preset.get(self._part_name, key))
