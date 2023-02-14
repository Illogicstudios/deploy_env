from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import utils
from BobElement import *
from BobCollapsibleWidget import *


class BobCategory(BobElement):
    def __init__(self, name, prefs, bob_tools):
        super().__init__(name)
        self.__prefs = prefs
        self._bob_tools = bob_tools
        for bob_tool in bob_tools:
            bob_tool.set_prefs(self.__prefs)

    def populate(self):
        scroll = QScrollArea()
        scroll.setFocusPolicy(Qt.NoFocus)
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(3, 6, 3, 8)
        layout.setSpacing(5)

        for bob_tool in self._bob_tools:
            layout_tool = bob_tool.populate()
            layout.addLayout(layout_tool)

        layout.addStretch(1)

        widget.setLayout(layout)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        return scroll

    def on_selection_changed(self):
        for bob_tool in self._bob_tools:
            bob_tool.on_selection_changed()

    def on_dag_changed(self):
        for bob_tool in self._bob_tools:
            bob_tool.on_dag_changed()

    def save_prefs(self):
        for bob_tool in self._bob_tools:
            bob_tool.save_prefs()

    def retrieve_prefs(self):
        for bob_tool in self._bob_tools:
            bob_tool.retrieve_prefs()
