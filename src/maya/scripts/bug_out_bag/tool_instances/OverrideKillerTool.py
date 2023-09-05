from ..tool_models.ActionTool import *

from common.utils import *


class OverrideKillerTool(ActionTool):
    def __init__(self):
        super().__init__(name="Override Killer", pref_name="override_killer",
                         description="Disable all the \"Enable Overrides\" in the scene", button_text="Run")
        
    def _action(self):
        """
        Remove all the override from transforms and shapes
        :return:
        """
        for sel in pm.ls(type=["shape", "transform"]):
            try:
                sel.overrideEnabled.set(0)
            except Exception:
                print_warning("'" + sel + ".overrideEnabled' is locked or connected and cannot be modified")
