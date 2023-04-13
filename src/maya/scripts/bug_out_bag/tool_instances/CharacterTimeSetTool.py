from tool_models.ActionTool import *
from utils import *


class CharacterTimeSetTool(ActionTool):
    def __init__(self):
        super().__init__(name="Character Time Setter",pref_name="character_time_setter",
                         description="Set the MTOA Time Constant to the StandIn", button_text="Set")
        self.__selection = []

    def __retrieve_selection(self):
        self.__selection.clear()
        for sl in ls(selection=True, type="transform"):
            standin = listRelatives(sl, type="aiStandIn")
            if len(standin) > 0:
                self.__selection.extend(standin)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__retrieve_selection()
        self.__refresh_btn()

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(len(self.__selection) > 0)

    def _action(self):
        for standin in self.__selection:
            addAttr(standin, longName ="mtoa_constant_anim_time",
                    attributeType ="double", keyable=1, defaultValue =0)
            expression(string=standin+".mtoa_constant_anim_time = time;",
                       object=standin, alwaysEvaluate=True, unitConversion="all")

    def populate(self):
        layout = super(CharacterTimeSetTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout