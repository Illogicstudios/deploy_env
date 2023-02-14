from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from pymel.core import *

from BobElement import *
from BobCollapsibleWidget import *


class BobTool(BobElement, ABC):
    def __init__(self, name, pref_name, tooltip=""):
        super(BobTool, self).__init__(name)
        self.__tooltip = tooltip
        self._pref_name = pref_name
        self._prefs = None

    def populate(self):
        layout = QVBoxLayout()
        collapsible = BobCollapsibleWidget(self._name, self._pref_name, self._prefs, bg_color="rgb(50, 50, 50)",
                                           widget_color="rgb(80, 80, 100)", margins=[3, 3, 3, 3])
        collapsible.setToolTip(self.__tooltip)
        layout.addWidget(collapsible)
        return layout

    def on_selection_changed(self):
        pass

    def on_dag_changed(self):
        pass

    def save_prefs(self):
        pass

    def retrieve_prefs(self):
        pass

    def set_prefs(self, prefs):
        self._prefs = prefs
