import enum
import os.path
import re
from functools import partial

import maya.OpenMaya as OpenMaya
import pymel.core as pm

from ..ControlRoomPart import *
from ..FormSlider import *
from ..PresetManager import *

_NBMAX_PRESET = 10


class PresetFilterDialog(QDialog):
    def __init__(self, preset):
        super(PresetFilterDialog, self).__init__(wrapInstance(int(omui.MQtUtil.mainWindow()), QWidget))

        # Model attributes
        self.__preset = preset
        self.__fields_selected = []

        # UI attributes
        self.__ui_width = 450
        self.__ui_height = 700
        self.__ui_min_width = 300
        self.__ui_min_height = 300
        self.__ui_pos = QDesktopWidget().availableGeometry().center() - QPoint(self.__ui_width, self.__ui_height) / 2
        self.__tab_widget = None

        # name the window
        self.setWindowTitle("Preset Filter Fields")
        # make the window a "tool" in Maya's eyes so that it stays on top when you click off
        self.setWindowFlags(QtCore.Qt.Tool)
        # Makes the object get deleted from memory, not just hidden, when it is closed.
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.__create_ui()
        self.__refresh_ui()

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

        title = QLabel("Select the fields that the preset must contain")
        title.setContentsMargins(5, 5, 5, 5)
        main_lyt.addWidget(title, 0, alignment=Qt.AlignCenter)

        # All Fields
        self.__ui_list_fields = QListWidget()
        self.__ui_list_fields.setContentsMargins(10, 10, 10, 10)
        self.__ui_list_fields.setSpacing(0)
        self.__ui_list_fields.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__ui_list_fields.itemSelectionChanged.connect(self.__on_selection_field_changed)
        main_lyt.addWidget(self.__ui_list_fields, 1)

        self.__ui_submit_btn = QPushButton("Submit preset filter fields")
        self.__ui_submit_btn.clicked.connect(self.__submit_filter)
        main_lyt.addWidget(self.__ui_submit_btn)

    # Refresh the ui according to the model attribute
    def __refresh_ui(self):
        try:
            self.__ui_list_fields.clear()
            first = True
            for part, fields in self.__preset.items():
                if not first:
                    item = QtWidgets.QListWidgetItem()
                    sep = QFrame()
                    sep.setFrameShape(QFrame.HLine)
                    sep.setFrameShadow(QFrame.Sunken)
                    item.setFlags(Qt.NoItemFlags)
                    self.__ui_list_fields.addItem(item)
                    self.__ui_list_fields.setItemWidget(item, sep)
                for field_name, value in fields.items():
                    if type(value) is float:
                        value = round(value, 3)
                    item = QtWidgets.QListWidgetItem()
                    item.setData(Qt.UserRole, {"part": part, "field": field_name})
                    widget_preset = QWidget()
                    widget_preset.setStyleSheet("this{border: 1px solid red }")
                    lyt = QHBoxLayout(widget_preset)
                    lyt.setContentsMargins(2, 2, 2, 2)
                    lyt.addWidget(QLabel(field_name), 2, alignment=Qt.AlignVCenter)
                    lyt.addWidget(QLabel(str(value)), 1, alignment=Qt.AlignVCenter)

                    widget_preset.setLayout(lyt)
                    item.setSizeHint(widget_preset.sizeHint())

                    self.__ui_list_fields.addItem(item)
                    self.__ui_list_fields.setItemWidget(item, widget_preset)
                first = False
            self.__refresh_btn()
        except:
            pass

    def __refresh_btn(self):
        self.__ui_submit_btn.setEnabled(len(self.__fields_selected) > 0)

    def __on_selection_field_changed(self):
        self.__fields_selected.clear()
        for item in self.__ui_list_fields.selectedItems():
            self.__fields_selected.append(item.data(Qt.UserRole))
        self.__refresh_btn()

    def __submit_filter(self):
        self.__preset.filter(self.__fields_selected)
        self.accept()


class EventFilterPreset(QObject):
    def __init__(self, control_room, preset):
        super().__init__()
        self.__control_room = control_room
        self.__preset = preset

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Enter:
            self.__control_room.set_hovered_preset(self.__preset)
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.__control_room.set_hovered_preset(None)
            return True
        return False


class PresetsPart(ControlRoomPart):

    def __init__(self, control_room, asset_path, part_name):
        super(PresetsPart, self).__init__(control_room, "Presets", part_name)
        self.__ui_presets_lyt = None
        self.__asset_path = asset_path
        self.__spacer = None
        self.__maya_callback = None
        self.__event_filters = []

    def populate(self):
        self.__ui_presets_lyt = QVBoxLayout()
        self.__ui_presets_lyt.setContentsMargins(2, 4, 2, 4)
        self.__ui_presets_lyt.setSpacing(5)
        return self.__ui_presets_lyt

    def refresh_ui(self):
        try:
            self.__event_filters.clear()
            if self.__spacer is not None:
                self.__ui_presets_lyt.removeItem(self.__spacer)
            clear_layout(self.__ui_presets_lyt)
            preset_manager = PresetManager.get_instance()
            presets = preset_manager.get_presets()
            default_presets = preset_manager.get_default_presets()

            presets_tuples = [(p, True) for p in default_presets] + [(p, False) for p in presets]

            index = 0

            icon_size = QtCore.QSize(16, 16)
            icon_container_size = QtCore.QSize(24, 24)

            for preset, is_default in presets_tuples:
                event_filter = EventFilterPreset(self._control_room, preset)
                self.__event_filters.append(event_filter)
                # Card
                widget_preset = QWidget()
                widget_preset.installEventFilter(event_filter)
                widget_preset.setMinimumWidth(120)
                widget_preset.setStyleSheet(".QWidget{background:#383838; border-radius:4px}")
                lyt_preset = QVBoxLayout(widget_preset)
                lyt_preset.setSpacing(10)
                # Label
                lbl_name_preset = QLabel(preset.get_name())
                lbl_name_preset.setStyleSheet("font-weight:bold")
                lyt_preset.addWidget(lbl_name_preset, alignment=Qt.AlignCenter)
                # Actions
                lyt_actions = QHBoxLayout()
                lyt_actions.setSpacing(5)
                lyt_actions.setAlignment(Qt.AlignCenter)
                lyt_preset.addLayout(lyt_actions)
                # Apply button
                apply_btn = QPushButton()
                apply_btn.setIconSize(QtCore.QSize(18, 18))
                apply_btn.setFixedSize(icon_container_size)
                apply_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "apply.png"))))
                apply_btn.clicked.connect(partial(self.__apply_preset, preset))
                lyt_actions.addWidget(apply_btn)
                # Delete btn
                delete_btn = QPushButton()
                delete_btn.setIconSize(icon_size)
                delete_btn.setFixedSize(icon_container_size)
                delete_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "delete.png"))))
                if is_default:
                    delete_btn.setEnabled(False)
                    delete_btn.setToolTip("Default presets can't be removed")
                else:
                    delete_btn.clicked.connect(partial(self.__delete_preset, preset))
                lyt_actions.addWidget(delete_btn)
                self.__ui_presets_lyt.insertWidget(index, widget_preset, 1)
                index += 1

            if index < _NBMAX_PRESET:
                # New Preset Button
                add_preset_btn = QPushButton("New Preset")
                add_preset_btn.setStyleSheet("margin:0px 20px")
                # if index == 0:
                #     add_preset_btn.setStyleSheet("padding: 3px;margin-top:18px")
                add_preset_btn.setIconSize(QtCore.QSize(18, 18))
                add_preset_btn.setIcon(QIcon(QPixmap(os.path.join(self.__asset_path, "add.png"))))
                add_preset_btn.clicked.connect(partial(self.__generate_new_preset))
                self.__ui_presets_lyt.insertWidget(index, add_preset_btn, 1, Qt.AlignCenter)
                index += 1

            if index < _NBMAX_PRESET:
                # Spacer
                self.__spacer = QSpacerItem(0, 0)
                self.__ui_presets_lyt.insertItem(index, self.__spacer)
                self.__ui_presets_lyt.setStretch(index, _NBMAX_PRESET - index)
            else:
                self.__spacer = None
        except:
            pass

    # Generate a new preset
    def __generate_new_preset(self):
        result = pm.promptDialog(
            title='New Preset',
            message='Enter the name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')
        if result == 'OK':
            preset_manager = PresetManager.get_instance()
            name = pm.promptDialog(query=True, text=True)
            if not re.match(r"^\w+$", name):
                print_warning(["\"" + name + "\" is a bad preset name", "The preset has not been created"])
                return
            if preset_manager.has_preset_with_name(name):
                print_warning(["Preset \"" + name + "\" already exists", "The preset has not been created"])
                return
            self._control_room.generate_preset(name)
            self.refresh_ui()

    # Delete the preset
    def __delete_preset(self, preset):
        answer_delete = pm.confirmDialog(
            title='Confirm',
            message="Are you sure to delete the preset " + preset.get_name() + " ?",
            button=['Yes', 'No'],
            defaultButton='Yes',
            dismissString='No')
        if answer_delete == "Yes":
            preset_manager = PresetManager.get_instance()
            preset_manager.remove_preset(preset)
            preset_manager.save_presets()
            self.refresh_ui()

    def __apply_preset(self, preset):
        self._control_room.apply_preset(preset)
        self.refresh_ui()

    # Callback when a Scene is opened
    def __callback_scene_opened(self):
        PresetManager.get_instance().retrieve_presets()
        self.refresh_ui()

    def add_callbacks(self):
        self.__maya_callback = pm.scriptJob(event=["SceneOpened", self.__callback_scene_opened])

    def remove_callbacks(self):
        pm.scriptJob(kill=self.__maya_callback)

    def add_to_preset(self, preset):
        # Nothing
        pass

    def apply(self, preset):
        # Nothing
        pass

    def filter(self, preset):
        filter_preset = PresetFilterDialog(preset)
        if filter_preset.exec_():
            return True
        return False
