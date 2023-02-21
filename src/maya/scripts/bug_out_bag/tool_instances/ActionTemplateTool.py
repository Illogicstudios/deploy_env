from tool_models.ActionTool import *


class ActionTemplateTool(ActionTool):
    def __init__(self):
        super().__init__(name="Action Tool",pref_name="action_template_tool",
                         description="Run the Template Action", button_text="Run")

    def _action(self):
        print(self._name)
