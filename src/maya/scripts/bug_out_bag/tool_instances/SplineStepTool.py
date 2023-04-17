from tool_models.MultipleActionTool import *
from utils import *

class SplineStepTool(MultipleActionTool):
    def __init__(self):
        actions = {
            "spline": {
                "text": "Spline",
                "action": self.__spline,
                "row": 0
            },
            "step": {
                "text": "Step",
                "action": self.__step,
                "row": 0
            },
            "keyframe_spline": {
                "text": "Keys to Spline",
                "action": self.__keys_to_spline,
                "row": 1
            },
            "keyframe_step": {
                "text": "Keys to Step",
                "action": self.__keys_to_step,
                "row": 1
            },
        }
        super().__init__(name="Spline Step", pref_name="spline_step_tool",
                         actions=actions, stretch=1)
        self.__selected = []

    def __step(self):
        pm.keyTangent(g=True, inTangentType="linear", outTangentType="step")
        self.__refresh_btn()

    def __spline(self):
        pm.keyTangent(g=True, inTangentType="auto", outTangentType="auto")
        self.__refresh_btn()

    def __keys_to_step(self):
        pm.selectKey(self.__selected)
        pm.keyTangent(outTangentType ="step")
        self.__refresh_btn()

    def __keys_to_spline(self):
        pm.selectKey(self.__selected)
        pm.keyTangent(outTangentType ="auto", inTangentType ="auto")
        self.__refresh_btn()

    def __refresh_btn(self):
        in_tangent, out_tangent, weighted_tangent = pm.keyTangent(g=True, query=True)
        stepped_enabled = in_tangent != "linear" or out_tangent != "step"
        spline_enabled = in_tangent != "auto" or out_tangent != "auto"
        keys_btn_enabled = len(self.__selected)>0
        if "button" in self._actions["step"]:
            self._actions["step"]["button"].setEnabled(stepped_enabled)
        if "button" in self._actions["spline"]:
            self._actions["spline"]["button"].setEnabled(spline_enabled)
        if "button" in self._actions["keyframe_step"]:
            self._actions["keyframe_step"]["button"].setEnabled(keys_btn_enabled)
        if "button" in self._actions["keyframe_spline"]:
            self._actions["keyframe_spline"]["button"].setEnabled(keys_btn_enabled)

    def __retrieve_datas(self):
        self.__selected = pm.ls(selection=True)
        self.__selected.extend(pm.listRelatives(allDescendents=True,type="transform"))

    def on_selection_changed(self):
        self.__retrieve_datas()
        self.__refresh_btn()

    def populate(self):
        layout = super(SplineStepTool, self).populate()
        self.__retrieve_datas()
        self.__refresh_btn()
        return layout
