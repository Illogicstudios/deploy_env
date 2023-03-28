from abc import *

import maya.OpenMaya as OpenMaya

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from utils import *


class ControlRoomPart(ABC):
    def __init__(self, control_room, name, part_name):
        self._control_room = control_room
        self._name = name
        self._part_name = part_name

    # Generate the part's UI
    def create_ui(self):
        lyt = QVBoxLayout()
        lyt.setSpacing(2)
        lyt.setAlignment(Qt.AlignTop)

        title_label = QLabel(self._name)
        title_label.setContentsMargins(5, 5, 5, 5)
        title_label.setStyleSheet("background-color:#5D5D5D;font-weight:bold")
        lyt.addWidget(title_label, 0, Qt.AlignTop)

        lyt.addLayout(self.populate())
        return lyt

    # Generate the UI content of the part
    @abstractmethod
    def populate(self):
        pass

    # Refresh the part's UI
    @abstractmethod
    def refresh_ui(self):
        pass

    # Add the part's callbacks
    @abstractmethod
    def add_callbacks(self):
        pass

    # Remove the part's callbacks
    @abstractmethod
    def remove_callbacks(self):
        pass

    # Generate the part's attributes in the preset
    @abstractmethod
    def add_to_preset(self, preset):
        pass

    # Apply the preset
    @abstractmethod
    def apply(self, preset):
        pass
