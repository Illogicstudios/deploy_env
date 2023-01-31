import os
from functools import partial

import sys

from pymel.core import *
import maya.OpenMayaUI as omui

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from PySide2.QtWidgets import *
from PySide2.QtCore import *

from shiboken2 import wrapInstance

import utils

import maya.OpenMaya as OpenMaya

from AOV import *

########################################################################################################################

# Available AOVs are sorted and ordered in groups. The higher the group number, the higher it will be in the list
LIGHT_GROUP_AOVS_ORDER_GROUP = 1
AOVS = {
    "N": DefaultAOV("N", 2, PrecisionMode.FullPrecision),
    "P": DefaultAOV("P", 2, PrecisionMode.FullPrecision),
    "Z": DefaultAOV("Z", 2, PrecisionMode.FullAndHalfPrecision),
    "volume": DefaultAOV("volume", 2),
    "emission": DefaultAOV("emission", 2),
    "crypto_asset": CryptomatteAOV("crypto_asset", 2),
    "crypto_material": CryptomatteAOV("crypto_material", 2),
    "crypto_object": CryptomatteAOV("crypto_object", 2),
    "uv": UVAOV("uv", 2),
    "sheen": DefaultAOV("sheen", 0),
    "specular": DefaultAOV("specular", 0),
    "transmission": DefaultAOV("transmission", 0),
    "sss": DefaultAOV("sss", 0),
    "coat": DefaultAOV("coat", 0),
    "occlusion": OcclusionAOV("occlusion", 0),
    "motionVectorBlur": MotionVectorBlurAOV("motionVectorBlur", 0),
}


########################################################################################################################

class AOVManager(QDialog):

    def __init__(self, prnt=wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget)):
        super(AOVManager, self).__init__(prnt)

        # Model attributes
        # for Light Groups part
        self.__lights_selected = []
        self.__name_light_group_default = True
        self.__light_groups = {}
        self.__selection_lg = None
        self.__selection_lg_light = None
        # For Aovs Part
        self.__active_aovs = []
        self.__available_aovs = {}
        self.__active_aovs_selected = []
        self.__available_aovs_selected = []

        # UI attributes
        self.__reinit_ui()

        # name the window
        self.setWindowTitle("AOV Manager")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.__create_callback()

        if self.test_arnold_renderer():
            # Create the layout, linking it to actions and refresh the display
            self.__create_ui()
            self.__refresh_ui()
        else:
            self.close()

    def test_arnold_renderer(self):
        arnold_renderer_loaded = objExists("defaultArnoldDriver")
        if not arnold_renderer_loaded:
            msg = QMessageBox()
            msg.setWindowTitle("Error AOV Manager with Arnold Renderer")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Arnold Renderer not loaded")
            msg.setInformativeText('AOV Manager can\'t run without the Arnold Renderer loaded. You '
                                   'can load the Arnold Renderer by opening the Render Settings Window')
            msg.exec_()
        return arnold_renderer_loaded

    # Create callbacks when DAG changes and the selection changes
    def __create_callback(self):
        self.__selection_callback = \
            OpenMaya.MEventMessage.addEventCallback("SelectionChanged", self.__on_selection_changed)
        self.__dag_callback = \
            OpenMaya.MEventMessage.addEventCallback("DagObjectCreated", self.__on_dag_changed)

    # Remove callbacks
    def closeEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        OpenMaya.MMessage.removeCallback(self.__selection_callback)
        OpenMaya.MMessage.removeCallback(self.__dag_callback)

    # Update the properties of the drivers
    @staticmethod
    def __update_drivers():
        if objExists("aov_full_driver"):
            full_driver = ls("aov_full_driver", type="aiAOVDriver")[0]
        else:
            full_driver = createNode('aiAOVDriver', name="aov_full_driver")
        full_driver.halfPrecision.set(0)
        full_driver.mergeAOVs.set(1)
        full_driver.multipart.set(1)
        full_driver.prefix.set("<RenderLayer>/<Scene>/<Scene>_utility")

        if objExists("defaultArnoldDriver"):
            half_driver = ls("defaultArnoldDriver", type="aiAOVDriver")[0]
        else:
            half_driver = createNode('aiAOVDriver', name="defaultArnoldDriver")

        half_driver.exrCompression.set(9)
        half_driver.mergeAOVs.set(1)
        half_driver.multipart.set(1)
        half_driver.halfPrecision.set(1)

        if objExists("defaultRenderGlobals"):
            ls("defaultRenderGlobals")[0].imageFilePrefix.set("<RenderLayer>/<Scene>/<Scene>")

    # Get all the lights in the scene
    @staticmethod
    def __get_all_lights():
        return ls(type=["light"] + listNodeTypes("light"), dag=True)

    # Retrieve all the available aovs and the active ones.
    def __retrieve_aovs(self):
        aov_possible_keys = list(AOVS.keys()) + \
                            [aov for aov in list(self.__light_groups)]

        unfiltered_active_aovs = [(aov.name().strip("aiAOV_"), aov) for aov in ls(type="aiAOV")]

        # Active AOVs
        self.__active_aovs = []
        for aov_name, aov in unfiltered_active_aovs:
            name = aov_name.strip("RGBA_")
            if "RGBA_" in aov_name:
                light_lg = ls(type=["light"] + listNodeTypes("light"), dag=True)
                found = False
                for light in light_lg:
                    if light.aiAov.get() == name:
                        found = True
                        break
                if not found:
                    delete(aov)
                    self.__retrieve_aovs()
                    return
            if name in aov_possible_keys:
                self.__active_aovs.append((aov_name, aov))

        active_aov_name = [aov[0].strip("RGBA_") for aov in self.__active_aovs]

        # Available AOVs
        self.__available_aovs = {}
        for aov_name, aov in AOVS.items():
            order_group = aov.get_order_group()
            if aov_name not in active_aov_name:
                if order_group not in self.__available_aovs:
                    self.__available_aovs[order_group] = []
                self.__available_aovs[order_group].append((aov_name, aov))
        for aov_name in self.__light_groups:
            if aov_name not in active_aov_name:
                if LIGHT_GROUP_AOVS_ORDER_GROUP not in self.__available_aovs:
                    self.__available_aovs[LIGHT_GROUP_AOVS_ORDER_GROUP] = []
                name = "RGBA_" + aov_name
                self.__available_aovs[LIGHT_GROUP_AOVS_ORDER_GROUP].append(
                    (name, LightGroupAOV(name, LIGHT_GROUP_AOVS_ORDER_GROUP)))

    # Retrieve all the light groups in the scene (!="default")
    def __retrieve_light_groups(self):
        lights = AOVManager.__get_all_lights()
        self.__light_groups = {}
        for light in lights:
            aov_light_group = light.aiAov.get()
            if "default" not in aov_light_group:
                if aov_light_group not in self.__light_groups:
                    self.__light_groups[aov_light_group] = []
                self.__light_groups[aov_light_group].append(light)

    # initialize the ui
    def __reinit_ui(self):
        self.__ui_width = 600
        self.__ui_height = 500
        self.__ui_min_width = 400
        self.__ui_min_height = 300

    # Create the ui
    def __create_ui(self):
        # Reinit attributes of the UI
        self.__reinit_ui()
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        # asset_path = os.path.dirname(__file__) + "/assets/asset.png"

        # Main Layout
        main_lyt = QVBoxLayout()
        main_lyt.setSpacing(8)
        self.setLayout(main_lyt)
        tab_widget = QTabWidget()
        main_lyt.addWidget(tab_widget)

        # ################################################## Tabs ######################################################

        # Layout Tab 1 : AOVs
        aovs_lyt = QVBoxLayout()
        aov_widget = QWidget()
        aov_widget.setLayout(aovs_lyt)
        tab_widget.addTab(aov_widget, "AOVs")

        # Layout Tab 2 : Lights
        lights_lyt = QGridLayout()
        lights_lyt.setColumnStretch(0, 2)
        lights_lyt.setColumnStretch(1, 3)
        light_widget = QWidget()
        light_widget.setLayout(lights_lyt)
        tab_widget.addTab(light_widget, "Light Groups")

        # ############################################# Tab 1 : AOVs ###################################################


        # Widget ML.1.1 : Update Drivers
        update_drivers_btn = QPushButton("Update Drivers")
        update_drivers_btn.clicked.connect(AOVManager.__update_drivers)
        aovs_lyt.addWidget(update_drivers_btn)

        # Layout ML.1.2 : AOVs
        aovs_grid = QGridLayout()
        aovs_grid.setColumnStretch(0, 1)
        aovs_grid.setColumnStretch(1, 1)
        aovs_lyt.addLayout(aovs_grid)

        # Widget ML.1.2.1 : Available AOVs
        available_aovs_title = QLabel("Available AOVs")
        available_aovs_title.setAlignment(Qt.AlignCenter)
        aovs_grid.addWidget(available_aovs_title, 0, 0)
        # Widget ML.1.2.2 : Active AOVs
        active_aovs = QLabel("Active AOVs")
        active_aovs.setAlignment(Qt.AlignCenter)
        aovs_grid.addWidget(active_aovs, 0, 1)

        # Widget ML.1.2.3 : List Available AOVs
        self.__ui_list_available_aovs_view = QListWidget()
        self.__ui_list_available_aovs_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__ui_list_available_aovs_view.itemSelectionChanged.connect(self.__on_selection_available_aovs_changed)
        aovs_grid.addWidget(self.__ui_list_available_aovs_view, 1, 0)
        # Widget ML.1.2.4 : List Active AOVs
        self.__ui_list_active_aovs_view = QListWidget()
        self.__ui_list_active_aovs_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__ui_list_active_aovs_view.itemSelectionChanged.connect(self.__on_selection_active_aovs_changed)
        aovs_grid.addWidget(self.__ui_list_active_aovs_view, 1, 1)

        # Widget ML.1.2.5 : Add AOV to active
        self.__ui_add_aov_to_active_btn = QPushButton(">>>")
        self.__ui_add_aov_to_active_btn.clicked.connect(partial(self.__add_aovs_to_active))
        aovs_grid.addWidget(self.__ui_add_aov_to_active_btn, 2, 0)
        # Widget ML.1.2.6: Remove AOV from Active
        self.__ui_remove_aov_to_active_btn = QPushButton("<<<")
        self.__ui_remove_aov_to_active_btn.clicked.connect(self.__remove_selected_aovs_from_active)
        aovs_grid.addWidget(self.__ui_remove_aov_to_active_btn, 2, 1)

        # ########################################## Tab 2 : Light Groups ##############################################

        # Widget ML.2.1 : Lights title
        lights_title = QLabel("Lights")
        lights_title.setAlignment(Qt.AlignCenter)
        lights_lyt.addWidget(lights_title, 0, 0)
        # Widget ML.2.2 : Light groups title
        lg_title = QLabel("Light Groups AOV")
        lg_title.setAlignment(Qt.AlignCenter)
        lights_lyt.addWidget(lg_title, 0, 1)

        # Widget ML.2.3 : List Lights
        self.__ui_light_list_view = QListWidget()
        self.__ui_light_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__ui_light_list_view.itemSelectionChanged.connect(self.__on_light_selection_changed)
        lights_lyt.addWidget(self.__ui_light_list_view, 1, 0)
        # Layout ML.2.4 : Light groups
        lg_lyt = QVBoxLayout()
        lights_lyt.addLayout(lg_lyt, 1, 1)
        # Layout ML.2.4.1 : Light group name
        lg_name_lyt = QHBoxLayout()
        lg_lyt.addLayout(lg_name_lyt, 1)
        # Widget ML.2.4.1.1 : Light group name prefix
        lg_prefix = QLabel("RGBA_")
        lg_name_lyt.addWidget(lg_prefix)
        # Widget ML.2.4.1.2 : Light group name edit
        self.__ui_lg_name_edit = QLineEdit("")
        self.__ui_lg_name_edit.textEdited.connect(self.__on_light_group_name_changed)
        lg_name_lyt.addWidget(self.__ui_lg_name_edit)
        # Widget ML.2.4.2 : Button create light group or rename light group
        self.__ui_lg_submit_btn = QPushButton()
        self.__ui_lg_submit_btn.clicked.connect(self.__submit_light_group)
        lg_lyt.addWidget(self.__ui_lg_submit_btn)
        # Widget ML.2.4.3 : Tree List light group
        self.__ui_lg_tree_widget = QTreeWidget()
        self.__ui_lg_tree_widget.setHeaderHidden(True)
        self.__ui_lg_tree_widget.itemSelectionChanged.connect(self.__on_selection_lg_changed)
        lg_lyt.addWidget(self.__ui_lg_tree_widget)

        # Widget ML.2.5 : Add light to light group button
        self.__ui_add_selected_light_to_lg_btn = QPushButton("Add to light group selected")
        self.__ui_add_selected_light_to_lg_btn.setEnabled(False)
        self.__ui_add_selected_light_to_lg_btn.clicked.connect(self.__add_lights_to_light_group)
        lights_lyt.addWidget(self.__ui_add_selected_light_to_lg_btn, 2, 0)
        # Widget ML.2.6: Create a light group by light button
        create_lg_by_light_btn = QPushButton("Create a light group by light")
        create_lg_by_light_btn.clicked.connect(self.__create_light_group_by_light)
        lights_lyt.addWidget(create_lg_by_light_btn, 3, 0)

        # Widget ML.2.7 : Remove light or a light group button
        self.__ui_remove_selection_lg = QPushButton("Remove Selection")
        self.__ui_remove_selection_lg.setEnabled(False)
        self.__ui_remove_selection_lg.clicked.connect(self.__remove_selection_lg)
        lights_lyt.addWidget(self.__ui_remove_selection_lg, 2, 1)
        # Widget ML.2.8 : Remove all light groups button
        self.__ui_remove_all_lg_btn = QPushButton("Remove all")
        self.__ui_remove_all_lg_btn.setEnabled(False)
        self.__ui_remove_all_lg_btn.clicked.connect(self.__remove_all_light_groups)
        lights_lyt.addWidget(self.__ui_remove_all_lg_btn, 3, 1)

    # Refresh the ui according to the model attribute
    def __refresh_ui(self):
        # Light groups
        self.__retrieve_light_groups()
        self.__refresh_lights_list()
        self.__refresh_light_group_name()
        self.__refresh_light_group_list()
        self.__refresh_lg_btn()
        # AOVs
        self.__retrieve_aovs()
        self.__refresh_active_aovs_list()
        self.__refresh_available_aovs_list()
        self.__refresh_aov_btn()

    # Refresh the list of lights in UI
    def __refresh_lights_list(self):
        self.__ui_light_list_view.clear()
        lights = self.__get_all_lights()
        for light in lights:
            if "default" in light.aiAov.get():
                transform = light.getTransform()
                item = QtWidgets.QListWidgetItem()
                item.setText(transform.name())
                item.setData(Qt.UserRole, transform)
                self.__ui_light_list_view.addItem(item)

    # Refresh the tree list of light groups in UI
    def __refresh_light_group_list(self):
        tmp_selection_lg = self.__selection_lg
        tmp_selection_lg_light = self.__selection_lg_light

        self.__ui_lg_tree_widget.clear()

        for lg, lights in self.__light_groups.items():
            item = QtWidgets.QTreeWidgetItem(["RGBA_" + lg])
            item.setData(0, Qt.UserRole, lg)
            self.__ui_lg_tree_widget.addTopLevelItem(item)
            for light in lights:
                child = QtWidgets.QTreeWidgetItem([light.name()])
                child.setData(0, Qt.UserRole, light)
                item.addChild(child)
            item.setExpanded(True)
        self.__selection_lg = tmp_selection_lg
        self.__selection_lg_light = tmp_selection_lg_light

    # Refresh the name of light group to be created or renamed
    def __refresh_light_group_name(self):
        rename_lg = False
        if self.__selection_lg is not None and self.__selection_lg_light is None:
            lights = self.__get_all_lights()
            for light in lights:
                if light.aiAov.get() == self.__selection_lg:
                    rename_lg = True
                    break
        if rename_lg:
            self.__ui_lg_submit_btn.setText("Rename the light group")
            self.__ui_lg_name_edit.setText(self.__selection_lg)
            self.__name_light_group_default = True
        else:
            self.__selection_lg = None
            self.__ui_lg_submit_btn.setText("Create light group with selected lights")
            if self.__name_light_group_default:
                if len(self.__lights_selected) > 0:
                    name = self.__lights_selected[0].name()
                    while "RGBA_" + name in self.__light_groups.keys():
                        if not name[-1].isdigit():
                            name += '1'
                        elif name[-1] == '9':
                            new_name = ""
                            len_name = len(name)
                            for i in range(len_name):
                                if i != len_name - 1:
                                    new_name += name[i]
                            new_name += '1'
                            name = new_name
                        else:
                            new_name = ""
                            len_name = len(name)
                            for i in range(len_name):
                                if i != len_name - 1:
                                    new_name += name[i]
                            new_name += str(int(name[-1]) + 1)
                            name = new_name
                    self.__ui_lg_name_edit.setText(name)
                else:
                    self.__ui_lg_name_edit.setText("")

    # Refresh the list of active AOVs in UI
    def __refresh_active_aovs_list(self):
        self.__ui_list_active_aovs_view.clear()
        aovs = self.__active_aovs
        for aov_name, aov in aovs:
            item = QtWidgets.QListWidgetItem()
            item.setText(aov_name)
            item.setData(Qt.UserRole, aov)
            self.__ui_list_active_aovs_view.addItem(item)

    # Refresh the list of available AOVs in UI
    def __refresh_available_aovs_list(self):
        self.__ui_list_available_aovs_view.clear()
        available_aovs = sorted(self.__available_aovs.items(), reverse=True)
        first = True
        for order_group, aovs in available_aovs:
            if not first:
                item = QtWidgets.QListWidgetItem()
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setFrameShadow(QFrame.Sunken)
                item.setFlags(Qt.NoItemFlags)
                self.__ui_list_available_aovs_view.addItem(item)
                self.__ui_list_available_aovs_view.setItemWidget(item, sep)
            for aov_name, data in aovs:
                item = QtWidgets.QListWidgetItem()
                item.setText(aov_name)
                item.setData(Qt.UserRole, data)
                self.__ui_list_available_aovs_view.addItem(item)
            first = False

    # Refresh the buttons
    def __refresh_lg_btn(self):
        self.__ui_lg_submit_btn.setEnabled(
            len(self.__ui_lg_name_edit.text()) > 0 and
            ((self.__selection_lg is not None and self.__selection_lg_light is None) or
             len(self.__lights_selected) > 0))

        self.__ui_add_selected_light_to_lg_btn.setEnabled(
            len(self.__lights_selected) > 0 and self.__selection_lg is not None)
        self.__ui_remove_selection_lg.setEnabled(
            self.__selection_lg_light is not None or self.__selection_lg is not None)
        self.__ui_remove_all_lg_btn.setEnabled(len(self.__light_groups) > 0)

    # Refresh the button in UI
    def __refresh_aov_btn(self):
        self.__ui_add_aov_to_active_btn.setEnabled(len(self.__available_aovs_selected) > 0)
        self.__ui_remove_aov_to_active_btn.setEnabled(len(self.__active_aovs_selected) > 0)

    # Refresh the UI on selection changed
    def __on_selection_changed(self, *args, **kwargs):
        self.__refresh_ui()

    # Refresh the UI on dag changed
    def __on_dag_changed(self, *args, **kwargs):
        self.__refresh_ui()

    # Update the selected lights
    def __on_light_selection_changed(self):
        self.__lights_selected = []
        for item in self.__ui_light_list_view.selectedItems():
            self.__lights_selected.append(item.data(Qt.UserRole))
        self.__refresh_light_group_name()
        self.__refresh_lg_btn()

    # On Name of light group to be created or updated changed
    def __on_light_group_name_changed(self):
        self.__name_light_group_default = False
        self.__refresh_lg_btn()

    # Update the selected light groups or lights of light groups
    def __on_selection_lg_changed(self):
        item = self.__ui_lg_tree_widget.currentItem()
        if item is not None:
            selection = item.data(0, Qt.UserRole)
            if type(selection) == str:
                self.__selection_lg_light = None
                self.__selection_lg = selection
            else:
                self.__selection_lg_light = selection
                self.__selection_lg = item.parent().data(0, Qt.UserRole)
        else:
            self.__selection_lg_light = None
            self.__selection_lg = None
        self.__refresh_light_group_name()
        self.__refresh_lg_btn()

    # Update the available AOVs selected
    def __on_selection_available_aovs_changed(self):
        self.__available_aovs_selected = []
        for item in self.__ui_list_available_aovs_view.selectedItems():
            self.__available_aovs_selected.append(item.data(Qt.UserRole))
        self.__refresh_aov_btn()


    # Update the active AOVs selected
    def __on_selection_active_aovs_changed(self):
        self.__active_aovs_selected = []
        for item in self.__ui_list_active_aovs_view.selectedItems():
            self.__active_aovs_selected.append(item.data(Qt.UserRole))
        self.__refresh_aov_btn()


    # Create a new light group or rename a existant one
    def __submit_light_group(self, lights=None, name=None):
        undoInfo(openChunk=True)
        if name is None:
            name = self.__ui_lg_name_edit.text()

        if self.__selection_lg is not None and self.__selection_lg_light is None:
            lights = self.__get_all_lights()
            for light in lights:
                if light.aiAov.get() == self.__selection_lg:
                    light.aiAov.set(name)

            name_lg = "aiAOV_RGBA_" + self.__selection_lg
            if objExists(name_lg):
                delete(ls(name_lg)[0])
                name_aov = "aiAOV_RGBA_" + name
                self.__add_aovs_to_active([LightGroupAOV(name_aov, LIGHT_GROUP_AOVS_ORDER_GROUP)])
        else:
            if lights is None:
                lights = self.__lights_selected

            lights_filtered = []

            for light in lights:
                if "default" in light.aiAov.get():
                    lights_filtered.append(light)

            self.__add_lights_to_light_group(lights_filtered, "RGBA_" + name)

        self.__retrieve_light_groups()
        self.__retrieve_aovs()
        self.__name_light_group_default = True
        self.__refresh_light_group_name()
        self.__refresh_light_group_list()
        self.__refresh_lights_list()
        self.__refresh_available_aovs_list()
        self.__refresh_active_aovs_list()
        self.__refresh_lg_btn()
        undoInfo(closeChunk=True)

    # Create a light group by light
    def __create_light_group_by_light(self):
        undoInfo(openChunk=True)
        lights = self.__get_all_lights()
        for light in lights:
            light = light.getTransform()
            self.__submit_light_group([light], light.name())
        undoInfo(closeChunk=True)

    # Update all lights to remove all light groups
    def __remove_all_light_groups(self):
        undoInfo(openChunk=True)
        lights = self.__get_all_lights()
        for light in lights:
            light.aiAov.set("default")
        self.__retrieve_light_groups()
        self.__retrieve_aovs()
        self.__refresh_light_group_list()
        self.__refresh_lights_list()
        self.__refresh_available_aovs_list()
        self.__refresh_active_aovs_list()
        self.__refresh_lg_btn()
        undoInfo(closeChunk=True)

    # Add a set of lights in a light group (default : selected)
    def __add_lights_to_light_group(self, lights=None, light_group=None):
        undoInfo(openChunk=True)
        if lights is None:
            lights = self.__lights_selected

        if light_group is None:
            light_group = self.__selection_lg

        for light in lights:
            light.aiAov.set(light_group.strip("RGBA_"))

        self.__retrieve_light_groups()
        self.__retrieve_aovs()
        self.__selection_lg = None
        self.__selection_lg_light = None
        self.__refresh_light_group_list()
        self.__refresh_lights_list()
        self.__refresh_available_aovs_list()
        self.__refresh_lg_btn()
        undoInfo(closeChunk=True)

    # Remove a light from a light group or delete a light group
    def __remove_selection_lg(self):
        undoInfo(openChunk=True)
        if self.__selection_lg_light is not None:
            self.__selection_lg_light.aiAov.set("default")
        elif self.__selection_lg is not None:
            for light in self.__light_groups[self.__selection_lg]:
                light.aiAov.set("default")
        self.__retrieve_light_groups()
        self.__retrieve_aovs()
        self.__selection_lg = None
        self.__selection_lg_light = None
        self.__refresh_light_group_list()
        self.__refresh_lights_list()
        self.__refresh_available_aovs_list()
        self.__refresh_active_aovs_list()
        self.__refresh_lg_btn()
        undoInfo(closeChunk=True)

    # Add a set of available AOVs to active AOVs
    def __add_aovs_to_active(self, selection_available_aovs=None):
        take_selected = selection_available_aovs is None
        if take_selected:
            undoInfo(openChunk=True)
            selection_available_aovs = self.__available_aovs_selected

        AOVManager.__update_drivers()
        full_driver = ls("aov_full_driver", type="aiAOVDriver")[0]
        half_driver = ls("defaultArnoldDriver", type="aiAOVDriver")[0]

        for aov in selection_available_aovs:
            aov.create_aov(half_driver, full_driver)

        print("# AOVs created")

        self.__retrieve_aovs()
        self.__refresh_active_aovs_list()
        self.__refresh_available_aovs_list()
        self.__refresh_aov_btn()
        if take_selected:
            undoInfo(closeChunk=True)

    # Remove a set of AOVs from active AOVs
    def __remove_selected_aovs_from_active(self):
        undoInfo(openChunk=True)
        delete(self.__active_aovs_selected)
        self.__active_aovs_selected = []
        self.__retrieve_aovs()
        self.__refresh_active_aovs_list()
        self.__refresh_available_aovs_list()
        self.__refresh_aov_btn()
        undoInfo(closeChunk=True)
