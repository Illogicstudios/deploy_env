import os
import re

from functools import partial

import maya.OpenMaya as OpenMaya

from utils import *

from tool_models.ActionTool import *

import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

# ######################################################################################################################

# name_regexp is used to compare a retrieved colorspace with known olorspaces
# regexps are used to detect a colorspace pattern in a file name

_KNOWN_COLORSPACE = [
    {
        "name": "sRGB",
        "short_name": "sRGB",
        "name_regexp": r"sRGB",
        "regexp": {
            r".*sRGB.*": 0
        }
    },
    {
        "name": "Raw",
        "short_name": "Raw",
        "name_regexp": r"Raw",
        "regexp": {
            r".*Raw.*": 0,
            r".*ior.*\.jpg": 1,
            r".*(?:height|disp|metalness|glossiness|mask|nrm|bump|normal|rough).*": 2
        }
    },
    {
        "name": "ACEScg",
        "short_name": "ACEScg",
        "name_regexp": r"ACEScg",
        "regexp": {
            r".*ACEScg.*": 0
        }
    },
    {
        "name": "scene-linear Rec.709-sRGB",
        "short_name": "lin.Rec709",
        "name_regexp": r"scene-linear Rec[\.| ]709[\-|\/]sRGB",
        "regexp": {
            r".*\.hdr": 1
        }
    }
]

_STYLESHEET_FOUND = {
    "enabled": ".QPushButton{background-color:rgb(137,137,255);color:black}",
    "disabled": ".QPushButton{background-color:rgb(40,40,100);color:gray}",
}

_STYLESHEET_COLORSPACE_NOT_FOUND = {
    "enabled": ".QPushButton{background-color:rgb(150,150,150);color:black}",
    "disabled": ".QPushButton{background-color:rgb(25,25,25);color:gray}",
}


# ######################################################################################################################


class TextureCheckTool(ActionTool):
    def __init__(self):

        tooltip = "Check if File Nodes with same file have different colorspaces or" \
                  " if there are File Nodes with unknwown colorspaces "
        super().__init__(name="Check Texture", pref_name="check_texture",
                         description="Verify the colorspaces of all the textures",
                         button_text="Check", tooltip=tooltip)

        self.__dialog_opened = False
        self.__texture_check_dialog = TextureCheckDialog(self)

    # Launch the Dialog to check textures
    def _action(self):
        try:
            self.__texture_check_dialog.hide()
        except RuntimeError:
            self.__texture_check_dialog = TextureCheckDialog(self)
        self.__texture_check_dialog.show()
        self.__texture_check_dialog.refresh_ui()

    def populate(self):
        layout = super(TextureCheckTool, self).populate()
        self.__refresh_btn()
        return layout

    # setter of the state opened
    def set_opened(self, opened):
        self.__dialog_opened = opened
        self.__refresh_btn()

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(not self.__dialog_opened and len(ls(type="file")) > 0)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__refresh_btn()

class TextureCheckDialog(QDialog):
    def __init__(self, tool):
        super(TextureCheckDialog, self).__init__(wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget))
        self.__tool = tool

        # Model attributes
        self.__known_cs = _KNOWN_COLORSPACE
        self.__bad_cs_tex = {}
        self.__script_jobs = []
        self.__opened = False

        # UI attributes
        self.__ui_width = 700
        self.__ui_height = 400
        self.__ui_min_width = 400
        self.__ui_min_height = 300
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width, self.__ui_height) / 2

        # name the window
        self.setWindowTitle("Check Texture")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.__bad_cs_tex = {}

        # Create the layout, linking it to actions and refresh the display
        self.__create_ui()
        self.refresh_ui()

    # Refresh the datas and the ui of the filepath corresponding
    def __on_node_changed(self, filepath):
        self.__clear_script_jobs()
        if filepath in self.__bad_cs_tex:
            self.__bad_cs_tex.pop(filepath)
        self.build_bad_cs_tex(self.__bad_cs_tex, filepath)
        self.refresh_ui()

    # On file node created refresh the datas and the ui of its filepath
    def __on_file_created(self, *args, **kwargs):
        select(OpenMaya.MFnDependencyNode(args[0]).name())
        filepath = ls(selection=True)[0].fileTextureName.get()
        self.__on_node_changed(filepath)

    # On file node deleted refresh the datas and the ui of its filepath
    def __on_file_deleted(self, *args, **kwargs):
        select(OpenMaya.MFnDependencyNode(args[0]).name())
        filepath = ls(selection=True)[0].fileTextureName.get()
        self.__on_node_changed(filepath)

    # create the callbacks
    def __create_callback(self):
        self.__node_created_callback = OpenMaya.MDGMessage.addNodeAddedCallback(self.__on_file_created, "file")
        self.__node_deleted_callback = OpenMaya.MDGMessage.addNodeRemovedCallback(self.__on_file_deleted, "file")

    # On show event create the callbacks and initialize some values
    def showEvent(self, arg__1: QtGui.QShowEvent) -> None:
        self.__bad_cs_tex = self.build_bad_cs()
        self.__create_callback()
        self.__tool.set_opened(True)
        self.__opened = True

    # On hide event remove callbacks and change some values
    def hideEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        OpenMaya.MMessage.removeCallback(self.__node_created_callback)
        OpenMaya.MMessage.removeCallback(self.__node_deleted_callback)
        self.__tool.set_opened(False)
        self.__opened = False
        self.__clear_script_jobs()

    # Retrieve colorspaces pattern in a filename
    def __get_detected_colorspace(self, filename, colorspaces=None):
        match = None
        importance = -1

        for colorspace_data in self.__known_cs:
            if colorspaces is None or colorspace_data["name"] in colorspaces:
                for regexp, cs_imp in colorspace_data["regexp"].items():
                    if re.match(regexp, filename, re.IGNORECASE):
                        if importance < 0 or importance > cs_imp:
                            match = colorspace_data["name"]
                            importance = cs_imp
        return match

    # build datas of bad textures
    def build_bad_cs(self, test_call=False):
        bad_cs_tex = {}
        textures_file = ls(type="file")
        distinct_filepath = []
        for tex in textures_file:
            filepath = tex.fileTextureName.get()
            if filepath not in distinct_filepath:
                distinct_filepath.append(filepath)

        for filepath in distinct_filepath:
            self.build_bad_cs_tex(bad_cs_tex, filepath, test_call)

        return bad_cs_tex

    # build datas of bad textures for a filepath
    def build_bad_cs_tex(self, bad_cs_tex, filepath, test_call=False):
        textures_file = ls(type="file")

        # Initiate all the known colorspaces fields in the dict
        bad_cs_tex[filepath] = {"colorspaces": {}, "unknown_colorspaces": {}}
        for cs in self.__known_cs:
            bad_cs_tex[filepath]["colorspaces"][cs["name"]] = \
                {"textures": [], "found": False, "button": None, }

        for tex in textures_file:
            retrieved_filepath = tex.fileTextureName.get()
            if filepath == retrieved_filepath:
                if not test_call:
                    self.__script_jobs.append(scriptJob(
                        attributeChange=[tex + ".fileTextureName", partial(self.__on_node_changed, filepath)]))
                    self.__script_jobs.append(scriptJob(
                        attributeChange=[tex + ".colorSpace", partial(self.__on_node_changed, filepath)]))

                # Get the colorspace of the file node
                colorspace = tex.colorSpace.get()
                colorspace_known = False
                for colorspace_data in self.__known_cs:
                    if re.match(colorspace_data["name_regexp"], colorspace, re.IGNORECASE):
                        colorspace_known = True
                        colorspace = colorspace_data["name"]
                        break

                # Determine if the colorspace is known or not
                if not colorspace_known:
                    if colorspace not in bad_cs_tex[filepath]["unknown_colorspaces"]:
                        bad_cs_tex[filepath]["unknown_colorspaces"][colorspace] = []
                    bad_cs_tex[filepath]["unknown_colorspaces"][colorspace].append(tex)
                else:
                    bad_cs_tex[filepath]["colorspaces"][colorspace]["textures"].append(tex)
                    bad_cs_tex[filepath]["colorspaces"][colorspace]["found"] = True

        if filepath in bad_cs_tex:
            length_unknown = len(bad_cs_tex[filepath]["unknown_colorspaces"])
            nb_different_cs = 0
            for cs_tex_data in bad_cs_tex[filepath]["colorspaces"].values():
                nb_different_cs += min(1,len(cs_tex_data["textures"]))
            if nb_different_cs < 2 and length_unknown < 1:
                bad_cs_tex.pop(filepath)

    # Clear all script jobs linked to filenode
    def __clear_script_jobs(self):
        for sj in self.__script_jobs:
            evalDeferred(partial(scriptJob, kill=sj, force=True))
        self.__script_jobs.clear()

    # Select the filenodes corresponding to the row in table
    def __on_selection_table_changed(self):
        selection = []
        for s in self.__ui_file_cs_table.selectionModel().selectedRows():
            selection.extend(self.__ui_file_cs_table.item(s.row(), 0).data(Qt.UserRole))
        select(selection)

    # Create the ui
    def __create_ui(self):
        # Reinit attributes of the UI
        self.setMinimumSize(self.__ui_min_width, self.__ui_min_height)
        self.resize(self.__ui_width, self.__ui_height)
        self.move(self.__ui_pos)

        # Main Layout
        main_lyt = QVBoxLayout()
        self.setLayout(main_lyt)
        main_lyt.setContentsMargins(5, 8, 5, 8)

        nb_known_cs = len(self.__known_cs)
        self.__ui_file_cs_table = QTableWidget(0, nb_known_cs + 1)
        headers_label = ["File Name"]
        for known_cs_datas in self.__known_cs:
            headers_label.append(known_cs_datas["short_name"])
        self.__ui_file_cs_table.setHorizontalHeaderLabels(headers_label)
        self.__ui_file_cs_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        horizontal_header = self.__ui_file_cs_table.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.__ui_file_cs_table.verticalHeader().hide()
        self.__ui_file_cs_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__ui_file_cs_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__ui_file_cs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.__ui_file_cs_table.itemSelectionChanged.connect(self.__on_selection_table_changed)
        main_lyt.addWidget(self.__ui_file_cs_table)

        self.__ui_submit_btn = QPushButton("Submit colorspace choices")
        self.__ui_submit_btn.clicked.connect(self.__submit_cs_choices)
        main_lyt.addWidget(self.__ui_submit_btn)

    # Refresh the ui according to the model attribute
    def refresh_ui(self):
        if not self.__opened:
            return

        try:
            self.__ui_submit_btn.setEnabled(len(self.__bad_cs_tex) > 0)
            self.__ui_file_cs_table.setRowCount(0)
        except:
            # Button has been internally removed (closed dialog)
            pass

        # Fill table
        row_index = 0
        bad_cs_tex = dict(sorted(self.__bad_cs_tex.items(), key=lambda x: x[0]))
        for filepath, file_cs_datas in bad_cs_tex.items():
            self.__ui_file_cs_table.insertRow(row_index)
            basename = os.path.basename(filepath)
            # Get colorspaces found for the filepath
            css_found = [cs for cs in file_cs_datas["colorspaces"].keys() if file_cs_datas["colorspaces"][cs]["found"]]
            # Get colorspaces for which a pattern has been detected in filename
            colorspace_detected = self.__get_detected_colorspace(basename, css_found)
            # Filepath + distinct colorspaces for the filepath
            filepath_widget = QTableWidgetItem(
                basename + " [" + ', '.join(css_found + list(file_cs_datas["unknown_colorspaces"].keys())) + "]")
            file_nodes = []
            for cs_tex_data in file_cs_datas["colorspaces"].values():
                file_nodes.extend(cs_tex_data["textures"])
            filepath_widget.setData(Qt.UserRole, file_nodes)
            self.__ui_file_cs_table.setItem(row_index, 0, filepath_widget)
            col_index = 1
            for known_cs_datas in self.__known_cs:
                lyt = QHBoxLayout()
                lyt.setContentsMargins(2, 2, 2, 2)
                frame = QFrame()
                frame.setLayout(lyt)
                btn = QPushButton(known_cs_datas["short_name"])

                colorspace_data = self.__bad_cs_tex[filepath]["colorspaces"][known_cs_datas["name"]]

                # Retrieve state if exists or give the default value else
                if "state" in colorspace_data:
                    state = colorspace_data["state"]
                else:
                    state = known_cs_datas["name"] == colorspace_detected

                # Retrieve stylesheet if exists or give default values else
                if "button" in colorspace_data and colorspace_data["button"] is not None and "stylesheet" in \
                        colorspace_data["button"]:
                    stylesheet = colorspace_data["button"]["stylesheet"]
                elif known_cs_datas["name"] == colorspace_detected or known_cs_datas["name"] in css_found:
                    stylesheet = _STYLESHEET_FOUND
                else:
                    stylesheet = _STYLESHEET_COLORSPACE_NOT_FOUND

                btn.clicked.connect(partial(self.__on_click_button, filepath, known_cs_datas["name"]))

                # Set the button in data to be able to refresh them on changed
                self.__bad_cs_tex[filepath]["colorspaces"][known_cs_datas["name"]]["state"] = state
                self.__bad_cs_tex[filepath]["colorspaces"][known_cs_datas["name"]]["button"] = {
                    "button": btn,
                    "stylesheet": stylesheet
                }

                lyt.addWidget(btn)
                self.__ui_file_cs_table.setCellWidget(row_index, col_index, frame)
                col_index += 1
            row_index += 1
            self.__refresh_button(filepath)

    # toggle the state of buttons in data
    def __on_click_button(self, filepath, colorspace):
        if not self.__bad_cs_tex[filepath]["colorspaces"][colorspace]["state"]:
            for cs in self.__bad_cs_tex[filepath]["colorspaces"].keys():
                self.__bad_cs_tex[filepath]["colorspaces"][cs]["state"] = False
        self.__bad_cs_tex[filepath]["colorspaces"][colorspace]["state"] = not \
            self.__bad_cs_tex[filepath]["colorspaces"][colorspace]["state"]
        self.__refresh_button(filepath)

    # Refresh a button according to its state and its stylesheet
    def __refresh_button(self, filepath):
        for cs in self.__bad_cs_tex[filepath]["colorspaces"].keys():
            cs_datas = self.__bad_cs_tex[filepath]["colorspaces"][cs]
            button_data = cs_datas["button"]
            btn = button_data["button"]
            state = cs_datas["state"]
            stylesheet = button_data["stylesheet"]
            btn.setStyleSheet(stylesheet["enabled" if state else "disabled"])

    # Assign the chosen colorspaces
    def __submit_cs_choices(self):
        filepath_data_to_build = []
        for filepath, cs_tex_datas in self.__bad_cs_tex.items():
            colorspace = None
            for cs, cs_tex_data in cs_tex_datas["colorspaces"].items():
                if cs_tex_data["state"]:
                    colorspace = cs
                    break
            if colorspace is not None:
                for cs_tex_data in cs_tex_datas["colorspaces"].values():
                    for tex in cs_tex_data["textures"]:
                        tex.colorSpace.set(colorspace)
                for textures in cs_tex_datas["unknown_colorspaces"].values():
                    for tex in textures:
                        tex.colorSpace.set(colorspace)
                filepath_data_to_build.append(filepath)
        for filepath in filepath_data_to_build:
            self.build_bad_cs_tex(self.__bad_cs_tex, filepath)
        self.refresh_ui()
