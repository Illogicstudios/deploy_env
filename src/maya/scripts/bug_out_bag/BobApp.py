import os
import sys

from functools import partial

import pymel.core as pm
import maya.OpenMayaUI as omui
import maya.OpenMaya as OpenMaya

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from shiboken2 import wrapInstance

import common.utils

from common.Prefs import *
from .BobCategory import *

from .tool_instances.LockTool import *
from .tool_instances.CleanFreezeTool import *
from .tool_instances.CleanerTool import *
from .tool_instances.TextureCheckTool import *
from .tool_instances.ShaderTransferTool import *
from .tool_instances.RestPosToVertexColorTool import *
from .tool_instances.DeleteOrigTool import *
from .tool_instances.UVCopierTool import *
from .tool_instances.ShapeRenamerTool import *
from .tool_instances.SplineStepTool import *
from .tool_instances.OverrideKillerTool import *
from .tool_instances.ShadingGroupRenamerTool import *
from .tool_instances.HierarchyCheckTool import *
from .tool_instances.CharacterTimeSetTool import *
from .tool_instances.TraceSetTool import *

# ######################################################################################################################

_FILE_NAME_PREFS = "bug_out_bag"


# See bob_categories in __init__ to edit tools and categories

# ######################################################################################################################


class BobApp(QDialog):

    def __init__(self, prnt=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(BobApp, self).__init__(prnt)

        # Common Preferences (common preferences on all illogic tools)
        self.__common_prefs = Prefs()
        # Preferences for this tool
        self.__prefs = Prefs(_FILE_NAME_PREFS)

        # Model attributes
        self.__bob_categories = [
            BobCategory("Utils", self.__prefs, [
                LockTool(),
                ShaderTransferTool(),
                RestPosToVertexColorTool(),
                UVCopierTool(),
                SplineStepTool(),
                CharacterTimeSetTool(),
                TraceSetTool()
            ]),
            BobCategory("Clean", self.__prefs, [
                CleanFreezeTool(),
                CleanerTool(),
                TextureCheckTool(),
                DeleteOrigTool(),
                ShapeRenamerTool(),
                ShadingGroupRenamerTool(),
                OverrideKillerTool(),
                HierarchyCheckTool(),
            ]),
        ]
        self.__selected_category = 0

        # UI attributes
        self.__ui_width = 400
        self.__ui_height = 700
        self.__ui_min_width = 300
        self.__ui_min_height = 300
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width, self.__ui_height) / 2
        self.__tab_widget = None

        self.__retrieve_prefs()

        # name the window
        self.setWindowTitle("Bug-out bag")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.__create_callback()

        # Create the layout, linking it to actions and refresh the display
        self.__create_ui()
        self.__refresh_ui()

    def __save_prefs(self):
        """
        Save preferences
        :return:
        """
        size = self.size()
        self.__prefs["window_size"] = {"width": size.width(), "height": size.height()}
        pos = self.pos()
        self.__prefs["window_pos"] = {"x": pos.x(), "y": pos.y()}
        self.__prefs["selected_category"] = self.__selected_category
        for bob_categ in self.__bob_categories:
            bob_categ.save_prefs()

    def __retrieve_prefs(self):
        """
        Retrieve preferences
        :return:
        """
        if "window_size" in self.__prefs:
            size = self.__prefs["window_size"]
            self.__ui_width = size["width"]
            self.__ui_height = size["height"]

        if "window_pos" in self.__prefs:
            pos = self.__prefs["window_pos"]
            self.__ui_pos = QPoint(pos["x"], pos["y"])

        if "selected_category" in self.__prefs:
            self.__selected_category = self.__prefs["selected_category"]
        for bob_categ in self.__bob_categories:
            bob_categ.retrieve_prefs()

    def __create_callback(self):
        """
        Create callbacks when DAG changes and the selection changes
        :return:
        """
        self.__selection_callback = \
            OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.__on_selection_changed)
        self.__dag_callback = \
            OpenMaya.MEventMessage.addEventCallback("DagObjectCreated", self.__on_dag_changed)

    def hideEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        """
        Remove callbacks
        :return:
        """
        OpenMaya.MMessage.removeCallback(self.__selection_callback)
        OpenMaya.MMessage.removeCallback(self.__dag_callback)
        self.__save_prefs()

    def __create_ui(self):
        """
        Create the ui
        """
        # Reinit attributes of the UI
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(self.__ui_pos)

        # Main Layout
        main_lyt = QVBoxLayout()
        main_lyt.setContentsMargins(5, 8, 5, 8)
        self.setLayout(main_lyt)
        self.__tab_widget = QTabWidget()
        self.__tab_widget.currentChanged.connect(self.__tab_changed)
        main_lyt.addWidget(self.__tab_widget)

    def __refresh_ui(self):
        """
        Refresh the ui according to the model attribute
        :return:
        """
        current_index = self.__selected_category
        self.__tab_widget.clear()
        for bob_categ in self.__bob_categories:
            bob_categ_lyt = bob_categ.populate()
            self.__tab_widget.addTab(bob_categ_lyt, bob_categ.get_name())
        self.__tab_widget.setCurrentIndex(current_index)

    def __on_selection_changed(self, *args, **kwargs):
        """
        Distribute to categories the selection changed event
        :return:
        """
        for bob_categ in self.__bob_categories:
            bob_categ.on_selection_changed()

    def __on_dag_changed(self, *args, **kwargs):
        """
        Distribute to categories the dag changed event
        :return:
        """
        for bob_categ in self.__bob_categories:
            bob_categ.on_dag_changed()

    def __tab_changed(self, index):
        """
        Retrieve the tab index
        :param index
        :return:
        """
        self.__selected_category = index
