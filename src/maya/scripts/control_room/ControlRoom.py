import os
from functools import partial

import sys

import pymel.core as pm
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from shiboken2 import wrapInstance

from common.utils import *

from common.Prefs import *

import maya.OpenMaya as OpenMaya

from .PresetManager import *

import maya.mel as mel
import maya.app.renderSetup.model.override as maya_override
import maya.app.renderSetup.model.renderSetup as render_setup
import maya.app.renderSetup.model.utils as render_setup_utils

from .parts.FeatureOverridesPart import *
from .parts.DepthOfFieldPart import *
from .parts.MotionBlurPart import *
from .parts.ImageSizePart import *
from .parts.SamplingPart import *
from .parts.AdaptiveSamplingPart import *
from .parts.PresetsPart import *

# ######################################################################################################################

_FILE_NAME_PREFS = "control_room"

OVERRIDE_BG_COLOR = "rgb(100,50,25)"
OVERRIDE_LABEL_COLOR = "rgb(230,115,60)"
PRESET_CONTAINS_LABEL_COLOR = "rgb(151, 154, 206)"
PRESET_CONTAINS_AND_DIFFERENT_LABEL_COLOR = "rgb(53, 200, 223)"


# ######################################################################################################################


class ControlRoom(QDialog):

    # Generic function that create an override for an attribute of an object
    @staticmethod
    def create_override(obj_name, attr_name):
        visible_layer = render_setup.instance().getVisibleRenderLayer()
        col = visible_layer.renderSettingsCollectionInstance()
        return col.createAbsoluteOverride(obj_name, attr_name)

    # Generic function that remove an override
    @staticmethod
    def remove_override(override):
        if override is not None:
            maya_override.delete(override)

    # Generic function that retrieve an override for an attribute of an object
    @staticmethod
    def retrieve_override(obj_name, attr_name):
        visible_layer = render_setup.instance().getVisibleRenderLayer()
        for override in render_setup_utils.getOverridesRecursive(visible_layer):
            if override.typeName() == "absUniqueOverride" and obj_name == override.targetNodeName() and attr_name == override.attributeName():
                return override
        return None

    def __init__(self, prnt=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(ControlRoom, self).__init__(prnt)

        # Common Preferences (common preferences on all tools)
        self.__common_prefs = Prefs()
        # Preferences for this tool
        self.__prefs = Prefs(_FILE_NAME_PREFS)

        asset_path = os.path.dirname(__file__) + "/assets"

        # Model attributes
        self.__parts = [
            FeatureOverridesPart(self, "feature_overrides"),
            DepthOfFieldPart(self, "dof"),
            MotionBlurPart(self, "motion_blur"),
            ImageSizePart(self, "image_size"),
            SamplingPart(self, "sampling"),
            AdaptiveSamplingPart(self, "adaptive_sampling"),
        ]
        self.__preset_part = PresetsPart(self, asset_path, "assets")
        self.__hovered_preset = None
        self.__new_scene_callback = None

        # UI attributes
        self.__ui_width = 550
        self.__ui_height = 780
        self.__ui_min_width = 550
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width, self.__ui_height) / 2

        self.__retrieve_prefs()

        # name the window
        self.setWindowTitle("Control Room")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        if ControlRoom.test_arnold_renderer():
            # Create the layout, linking it to actions and refresh the display
            self.__create_ui()
            self.__refresh_ui()
            self.__add_callbacks()
        else:
            self.close()

    # Test if Arnold is loaded and display a warning popup if it is not
    @staticmethod
    def test_arnold_renderer():
        arnold_renderer_loaded = pm.objExists("defaultArnoldRenderOptions")
        if not arnold_renderer_loaded:
            msg = QMessageBox()
            msg.setWindowTitle("Error Control Room with Arnold Renderer")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Arnold Renderer not loaded")
            msg.setInformativeText('Control Room can\'t run without the Arnold Renderer loaded. You '
                                   'can load the Arnold Renderer by opening the Render Settings Window')
            msg.exec_()
        return arnold_renderer_loaded

    # Save preferences
    def __save_prefs(self):
        size = self.size()
        self.__prefs["window_size"] = {"width": size.width()}
        pos = self.pos()
        self.__prefs["window_pos"] = {"x": pos.x(), "y": pos.y()}

    # Retrieve preferences
    def __retrieve_prefs(self):
        if "window_size" in self.__prefs:
            size = self.__prefs["window_size"]
            self.__ui_width = size["width"]
        if "window_pos" in self.__prefs:
            pos = self.__prefs["window_pos"]
            self.__ui_pos = QPoint(pos["x"], pos["y"])

    # Remove callbacks and save preferences
    def hideEvent(self, arg__1: QCloseEvent) -> None:
        self.__remove_callbacks()
        self.__save_prefs()

    # Create the ui
    def __create_ui(self):
        # Reinit attributes of the UI
        self.setMinimumWidth(self.__ui_min_width)
        self.setFixedHeight(self.__ui_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(self.__ui_pos)

        # Main Layout
        main_lyt = QHBoxLayout()
        main_lyt.setContentsMargins(3, 8, 3, 0)
        main_lyt.setSpacing(10)
        main_lyt.setAlignment(Qt.AlignTop)
        self.setLayout(main_lyt)

        # Parts Layout
        parts_lyt = QVBoxLayout()
        parts_lyt.setSpacing(5)
        parts_lyt.setAlignment(Qt.AlignTop)
        for part in self.__parts:
            parts_lyt.addLayout(part.create_ui())
        main_lyt.addLayout(parts_lyt)

        # Presets Part
        main_lyt.addLayout(self.__preset_part.create_ui())

    # Refresh the ui according to the model attribute
    def __refresh_ui(self):
        for part in self.__parts:
            part.refresh_ui()
        self.__preset_part.refresh_ui()

    def set_hovered_preset(self, preset):
        self.__hovered_preset = preset
        for part in self.__parts:
            part.refresh_ui()

    def get_hovered_preset(self):
        return self.__hovered_preset

    def get_stylesheet_color_for_field(self, part_name, field_name, val, override=None):
        if self.__hovered_preset and self.__hovered_preset.contains(part_name, field_name):
            if self.__hovered_preset.get(part_name, field_name) != val:
                ss_color = "color:" + cr.PRESET_CONTAINS_AND_DIFFERENT_LABEL_COLOR
            else:
                ss_color = "color:" + cr.PRESET_CONTAINS_LABEL_COLOR
        elif override is not None:
            ss_color = "color:" + cr.OVERRIDE_LABEL_COLOR
        else:
            ss_color = ""
        return ss_color

    def on_new_scene(self):
        self.hide()
        self.close()

    # Add the callbacks of all parts
    def __add_callbacks(self):
        self.__new_scene_callback = pm.scriptJob(runOnce=True, event=["SceneOpened", self.on_new_scene])
        for part in self.__parts:
            part.add_callbacks()
        self.__preset_part.add_callbacks()

    # Remove the callbacks of all parts
    def __remove_callbacks(self):
        for part in self.__parts:
            part.remove_callbacks()
        self.__preset_part.remove_callbacks()

    # Generate a preset with the attributes of all parts
    def generate_preset(self, preset_name):
        preset_manager = PresetManager.get_instance()
        preset = Preset(name=preset_name, active=True)
        for part in self.__parts:
            part.add_to_preset(preset)
        self.__preset_part.add_to_preset(preset)
        success_creation = self.__preset_part.filter(preset)
        if success_creation:
            preset_manager.add_preset(preset)
            preset_manager.save_presets()

    # Apply a preset to all parts
    def apply_preset(self, preset):
        for part in self.__parts:
            part.apply(preset)
        self.__preset_part.apply(preset)
        self.__refresh_ui()
