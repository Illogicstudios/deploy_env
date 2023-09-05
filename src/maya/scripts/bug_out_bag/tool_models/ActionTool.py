from ..BobTool import *


class ActionTool(BobTool, ABC):
    """
    Tool that executes one action with a single button
    """
    def __init__(self, name, pref_name, description, tooltip="", button_text="Run"):
        super().__init__(name, pref_name, tooltip)
        self.__description = description
        self.__button_text = button_text
        self._action_btn = None

    @abstractmethod
    def _action(self):
        """
        Function executed when the button is pressed
        :return:
        """
        pass

    def __action_with_chunks(self):
        """
        Enclosing the action function in order to be able to rollback it
        :return:
        """
        pm.undoInfo(openChunk=True)
        self._action()
        pm.undoInfo(closeChunk=True)

    def populate(self):
        """
        Populate the ActionTool UI
        :return:
        """
        layout = super().populate()
        # Get the collapsible widget (the only widget of the layout)
        collapsible = layout.itemAt(0).widget()
        content_layout = QHBoxLayout(collapsible.contentWidget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        # Add a button and assign the action button to its clicked event
        hlyt = QHBoxLayout()
        content_layout.addLayout(hlyt)

        desc_lbl = QLabel(self.__description)
        desc_lbl.setContentsMargins(5, 0, 0, 0)
        desc_lbl.setWordWrap(True)
        hlyt.addWidget(desc_lbl, 1)

        self._action_btn = QPushButton(self.__button_text)
        self._action_btn.clicked.connect(self.__action_with_chunks)
        hlyt.addWidget(self._action_btn)
        return layout