import re

from shiboken2 import wrapInstance
from functools import partial

import maya.OpenMayaUI as omui

from ..tool_models.ActionTool import *
from common.utils import *


class HierarchyCheckVisualizeer(QDialog):
    def __init__(self, tool, sel_1, sel_2, object_diff_data_1, object_diff_data_2):
        """
        Constructor
        :param tool
        :param sel_1: object selected 1
        :param sel_2: object selected 1
        :param object_diff_data_1: differences in hierarchies from object 2
        :param object_diff_data_2: differences in hierarchies from object 2
        """
        super(HierarchyCheckVisualizeer, self).__init__(wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget))
        self.__tool = tool

        # Model attributes
        self.__opened = False
        self.__sel_1 = sel_1
        self.__sel_2 = sel_2
        self.__object_diff_data_1 = object_diff_data_1
        self.__object_diff_data_2 = object_diff_data_2

        # UI attributes
        self.__ui_width = 600
        self.__ui_height = 400
        self.__ui_min_width = 300
        self.__ui_min_height = 300
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width, self.__ui_height) / 2

        # name the window
        self.setWindowTitle("Check Hierarchy Visualizer")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Create the layout, linking it to actions and refresh the display
        self.__create_ui()
        self.refresh_ui()

    def showEvent(self, arg__1: QtGui.QShowEvent) -> None:
        """
        On show event create the callbacks and initialize some values
        :return:
        """
        self.__tool.set_opened(True)
        self.__opened = True

    def hideEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        """
        On hide event remove callbacks and change some values
        :return:
        """
        self.__tool.set_opened(False)
        self.__opened = False

    def __create_ui(self):
        """
        Create the UI
        :return:
        """
        # Reinit attributes of the UI
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(self.__ui_pos)

        # Main Layout
        main_lyt = QHBoxLayout()
        self.setLayout(main_lyt)
        main_lyt.setContentsMargins(5, 8, 5, 8)

        grid_widget = QWidget()
        grid_widget.setStyleSheet("font-size:12px")
        grid_layout = QGridLayout(grid_widget)
        main_lyt.addWidget(grid_widget)

        grid_layout.addWidget(QLabel("Objects present only in <b>" + self.__sel_1 + "</b> :"), 0, 0)
        grid_layout.addWidget(QLabel("Objects present only in <b>" + self.__sel_2 + "</b> :"), 0, 1)
        self.__ui_list_view_1 = QListWidget()
        self.__ui_list_view_1.setSpacing(2)
        grid_layout.addWidget(self.__ui_list_view_1, 1, 0)
        self.__ui_list_view_2 = QListWidget()
        self.__ui_list_view_2.setSpacing(2)
        self.__ui_list_view_1.currentItemChanged.connect(partial(self.__on_object_selected,self.__ui_list_view_2))
        self.__ui_list_view_2.currentItemChanged.connect(partial(self.__on_object_selected,self.__ui_list_view_1))
        grid_layout.addWidget(self.__ui_list_view_2, 1, 1)

    def refresh_ui(self):
        """
        Refresh the ui according to the model attribute
        :return:
        """
        self.__ui_list_view_1.clear()
        self.__ui_list_view_2.clear()
        for obj_diff in self.__object_diff_data_1:
            item = QListWidgetItem(obj_diff[0].name(long=True)+"   ["+obj_diff[1]+"]")
            item.setData(Qt.UserRole, obj_diff[0])
            self.__ui_list_view_1.addItem(item)
        for obj_diff in self.__object_diff_data_2:
            item = QListWidgetItem(obj_diff[0].name(long=True)+"   ["+obj_diff[1]+"]")
            item.setData(Qt.UserRole, obj_diff[0])
            self.__ui_list_view_2.addItem(item)

    def __on_object_selected(self, list_to_clear, item, previous):
        """
        Select the item in the scene selected when selected in the list
        :param list_to_clear
        :param item
        :param previous
        :return:
        """
        if item is not None:
            list_to_clear.setCurrentItem(None)
            pm.select(item.data(Qt.UserRole))


class HierarchyCheckTool(ActionTool):

    def __init__(self):
        tooltip = "Select 2 objects then click Check"
        super().__init__(name="Check Hierarchy", pref_name="check_hierarchy",
                         description="Check if same hierarchies (need 2 selections)", button_text="Check",
                         tooltip=tooltip)
        self.__selection = []
        self.__hierarchy_visualizer = None

    @staticmethod
    def trim_name(name):
        """
        Get only the end of a name of an object
        :param name:
        :return:
        """
        return re.match("^(?:.*:)?(?:.*\|)?(\w+)$",name).group(1)

    def _action(self):
        """
        Check that hierarchies are the same
        :return:
        """
        def check_if_same_objects(obj_1, obj_2):
            obj_diff_1 = []
            obj_diff_2 = []
            children_data_1 = {HierarchyCheckTool.trim_name(child_1.name()): child_1 for child_1 in
                               pm.listRelatives(obj_1, children=True)}
            children_data_2 = {HierarchyCheckTool.trim_name(child_2.name()): child_2 for child_2 in
                               pm.listRelatives(obj_2, children=True)}
            children_name_1 = list(children_data_1.keys())
            children_name_1_copy = children_name_1.copy()
            children_name_2 = list(children_data_2.keys())
            corresp = []
            # Check Correspondences objects1 --> objects2
            for child_name_1 in children_name_1:
                child_1 = children_data_1[child_name_1]
                if child_name_1 in children_name_2:
                    child_2 = children_data_2[child_name_1]
                    child_1_type = child_1.nodeType()
                    child_2_type = child_2.nodeType()
                    processed = False
                    if child_1_type != child_2_type:
                        # Type Different
                        obj_diff_1.append((child_1, "type"))
                        obj_diff_2.append((child_2, "type"))
                        processed = True
                    elif child_1_type == "mesh":
                        child_1_nb_vertices = len(child_1.vtx)
                        child_2_nb_vertices = len(child_2.vtx)
                        if child_1_nb_vertices != child_2_nb_vertices:
                            # If count vertices different
                            obj_diff_1.append((child_1, "mesh"))
                            obj_diff_2.append((child_2, "mesh"))
                            processed = True
                    if not processed:
                        # Corresp found
                        corresp.append((child_1, child_2))
                    children_name_2.remove(child_name_1)
                    children_name_1_copy.remove(child_name_1)
                else:
                    obj_diff_1.append((child_1, "name"))

            # Check Correspondences objects2 --> objects1
            for child_name_2 in children_name_2:
                if child_name_2 in children_name_1_copy:
                    corresp.append((children_data_1[child_name_2], children_data_2[child_name_2]))
                else:
                    obj_diff_2.append((children_data_2[child_name_2], "name"))

            # Recursive Check
            for corresp_data in corresp:
                res1, res2 = check_if_same_objects(corresp_data[0], corresp_data[1])
                for object_data_diff in res1:
                    if object_data_diff[0] not in obj_diff_1:
                        obj_diff_1.append(object_data_diff)
                for object_data_diff in res2:
                    if object_data_diff[0] not in obj_diff_2:
                        obj_diff_2.append(object_data_diff)
            return obj_diff_1, obj_diff_2

        if len(self.__selection) >= 2:
            sel_1 = self.__selection[0]
            sel_2 = self.__selection[1]
            objects_diff_data_1, objects_diff_data_2 = check_if_same_objects(sel_1, sel_2)

            if len(objects_diff_data_1) == 0 and len(objects_diff_data_2) == 0:
                msg = QMessageBox()
                msg.setWindowTitle("Same hierarchy")
                msg.setIcon(QMessageBox.Information)
                msg.setText("Objects match each other")
                msg.exec_()
            else:
                # If differences found, show the visualizer
                try:
                    self.__hierarchy_visualizer.hide()
                except Exception:
                    self.__hierarchy_visualizer = HierarchyCheckVisualizeer(self, sel_1, sel_2, objects_diff_data_1,
                                                                            objects_diff_data_2)
                self.__hierarchy_visualizer.show()
                self.__hierarchy_visualizer.refresh_ui()

    def set_opened(self, opened):
        """
        Setter of the state opened
        :param opened
        :return:
        """
        self.__dialog_opened = opened
        self.__refresh_btn()

    def __refresh_btn(self):
        """
        Refresh the button
        :return:
        """
        self._action_btn.setEnabled(len(self.__selection) >= 2)

    def __retrieve_selection(self):
        """
        Reieve the selection
        :return:
        """
        self.__selection = pm.ls(sl=True)

    def on_selection_changed(self):
        """
        Refresh the button on selection changed
        :return:
        """
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        """
        Populate the HierarchyCheckTool UI
        :return:
        """
        layout = super(HierarchyCheckTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
