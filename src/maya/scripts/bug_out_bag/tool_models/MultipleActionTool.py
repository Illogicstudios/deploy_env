from BobTool import *


class MultipleActionTool(BobTool, ABC):
    def __init__(self, name, pref_name, actions, stretch=0, tooltip=""):
        super().__init__(name, pref_name, tooltip)
        self._actions = actions
        self.__row = 0
        self.__stretch = stretch
        for action in self._actions.values():
            if "row" in action:
                self.__row = max(self.__row, action["row"])

    def _add_ui_before_buttons(self, lyt):
        pass

    def populate(self):
        layout = super(MultipleActionTool, self).populate()
        # Get the collapsible widget (the only widget of the layout)
        collapsible = layout.itemAt(0).widget()
        content_layout = QVBoxLayout(collapsible.contentWidget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        # Add a button and assign the action button to its clicked event

        self._add_ui_before_buttons(content_layout)

        layouts = []
        for i in range(self.__row + 1):
            lyt = QHBoxLayout()
            layouts.append(lyt)
            lyt.setAlignment(Qt.AlignCenter)
            content_layout.addLayout(lyt)
        for action in self._actions.values():
            row = 0
            if "row" in action:
                row = action["row"]
            action_btn = QPushButton(action["text"])
            action_btn.clicked.connect(action["action"])
            action["button"] = action_btn
            stretch = self.__stretch
            if "stretch" in action:
                stretch = action["stretch"]
            if stretch > 0:
                action_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            layouts[row].addWidget(action_btn, stretch)
        return layout
