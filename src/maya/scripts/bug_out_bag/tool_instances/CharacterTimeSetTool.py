from ..tool_models.ActionTool import *
from common.utils import *


class CharacterTimeSetTool(ActionTool):
    def __init__(self):
        super().__init__(name="Character Time Setter",pref_name="character_time_setter",
                         description="Set the MTOA Time Constant to the StandIn", button_text="Set")
        self.__selection = []

    def __retrieve_selection(self):
        """
        Retrieve the selection
        :return:
        """
        self.__selection.clear()
        for sl in pm.ls(selection=True, type="transform"):
            standin = pm.listRelatives(sl, type="aiStandIn")
            if len(standin) > 0:
                self.__selection.extend(standin)

    def on_selection_changed(self):
        """
        Refresh the button on selection changed
        :return:
        """
        self.__retrieve_selection()
        self.__refresh_btn()

    def __refresh_btn(self):
        """
        Refresh the button
        :return:
        """
        self._action_btn.setEnabled(len(self.__selection) > 0)

    def _action(self):
        """
        Set constant mtoa_constant_anim_time and mtoa_constant_anim_time for each StandIn
        :return:
        """
        for standin in self.__selection:
            pm.addAttr(standin, longName ="mtoa_constant_anim_time",
                    attributeType ="double", keyable=1, defaultValue =0)
            pm.expression(string=standin+".mtoa_constant_anim_time = time;",
                       object=standin, alwaysEvaluate=True, unitConversion="all")

    def populate(self):
        """
        Populate the CharacterTimeSetTool UI
        :return: layout
        """
        layout = super(CharacterTimeSetTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout