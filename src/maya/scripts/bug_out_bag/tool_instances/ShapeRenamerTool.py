from ..tool_models.ActionTool import *
from common.utils import *

class ShapeRenamerTool(ActionTool):
    def __init__(self):
        super().__init__(name="Shape Renamer", pref_name="shape_renamer_tool",
                         description="Rename the shapes of selection", button_text="Rename")
        self.__selection = []

    def _action(self):
        for data in self.__selection:
            pm.rename(data["shapes"][0],data["transform"].name()+"Shape")

    def __retrieve_selection(self):
        self.__selection = []
        for sl in pm.ls(selection=True, type="transform"):
            shapes = pm.listRelatives(sl, shapes=True)
            if len(shapes) > 0:
                self.__selection.append({"transform": sl, "shapes": shapes})

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(len(self.__selection) > 0)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        layout = super(ShapeRenamerTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
