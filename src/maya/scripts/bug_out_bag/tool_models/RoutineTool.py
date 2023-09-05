from functools import partial

from ..BobTool import *


class RoutineTool(BobTool, ABC):
    """
    Tool that performs a routine, i.e. a sequence of functions. Only certain steps can be executed.
    The UI and the actions are customizable.
    Example :
    {
        "step_1": {
            "action": self.__some_function_1,       # Function executed on routine launched if step checked
            "text": "Step 1"                        # Text on the step
        },
        "step_2": {
            "action": self__some_function_2,
            "text": "Step 2"
        },
        "step_3": {
            "action": self.__some_function_3,
            "text": "Step 3",
            "checked": False                        # State checked at start
        }
    }
    """
    def __init__(self, name, pref_name, steps, tooltip="", button_text="Run",
                 step_checked_default = True, checkbox_pref= True):
        """
        Constructor
        :param name
        :param pref_name
        :param steps (see above)
        :param tooltip
        :param button_text
        :param step_checked_default: State checked by default
        :param checkbox_pref
        """
        super().__init__(name, pref_name,tooltip)
        self.__checkbox_pref = checkbox_pref
        self.__description = "description"
        self.__button_text = button_text

        self.__steps = steps
        for step_id in steps.keys():
            if "checked" not in self.__steps[step_id]:
                self.__steps[step_id]["checked"] = step_checked_default
            self.__steps[step_id]["checkbox"] = None
        self.__run_btn = None
        self.__refreshing = False
        self.__global_cb = None

    def populate(self):
        """
        Populate the RoutineTool UI
        :return:
        """
        layout = super().populate()
        # Get the collapsible widget (the only widget of the layout)
        collapsible = layout.itemAt(0).widget()
        content_layout = QHBoxLayout(collapsible.contentWidget)
        content_layout.setContentsMargins(5, 5, 5, 10)
        # Add a button and assign the action button to its clicked event
        vlyt = QVBoxLayout()
        content_layout.addLayout(vlyt)

        hlyt = QHBoxLayout()
        vlyt.addLayout(hlyt)
        self.__global_cb = QCheckBox()
        self.__global_cb.stateChanged.connect(self.__on_global_state_changed)
        hlyt.addWidget(self.__global_cb)
        self.__run_btn = QPushButton(self.__button_text)
        self.__run_btn.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.__run_btn.clicked.connect(self.__run)
        hlyt.addWidget(self.__run_btn,0,Qt.AlignRight)

        for step_id, step in self.__steps.items():
            lyt_step = QHBoxLayout()
            step_cb = QCheckBox()
            step_cb.setChecked(step["checked"])
            self.__steps[step_id]["checkbox"] = step_cb
            step_cb.stateChanged.connect(partial(self.__on_step_state_modified,step_id))
            lyt_step.addWidget(step_cb)
            step_label = QLabel(step["text"])
            step_label.setWordWrap(True)
            lyt_step.addWidget(step_label,1)
            vlyt.addLayout(lyt_step)

        self.__refresh_ui()
        return layout

    def __run(self):
        """
        Run the routine
        :return:
        """
        for step in self.__steps.values():
            if step["checked"]:
                step["action"]()

    def __refresh_ui(self):
        """
        Refresh the UI
        :return:
        """
        enabled = False
        checked = True
        for step in self.__steps.values():
            if step["checked"]:
                enabled = True
            else:
                checked = False
        self.__refreshing = True
        self.__run_btn.setEnabled(enabled)
        self.__global_cb.setChecked(checked)
        self.__refreshing = False

    def __on_step_state_modified(self, step_key, state):
        """
        On checkbox state changed retrieve the value
        :param step_key
        :param state
        :return:
        """
        self.__steps[step_key]["checked"] = state == 2
        self.__refresh_ui()

    def __on_global_state_changed(self, state):
        """
        On global checkbox state changed, retrieve the value and change the step checked state
        :param state:
        :return:
        """
        if not self.__refreshing:
            for step_name in self.__steps.keys():
                self.__steps[step_name]["checkbox"].setChecked(state == 2)
            self.__refresh_ui()

    def retrieve_prefs(self):
        if self.__checkbox_pref:
            if self._pref_name in self._prefs:
                pref = self._prefs[self._pref_name]
                for step_id in self.__steps.keys():
                    if step_id in pref:
                        self.__steps[step_id]["checked"] = pref[step_id]

    def save_prefs(self):
        if self.__checkbox_pref:
            pref = self._prefs[self._pref_name] if self._pref_name in self._prefs else {}
            for step_id in self.__steps.keys():
                pref[step_id] = self.__steps[step_id]["checked"]

            self._prefs[self._pref_name] = pref

