from tool_models.ActionTool import *


class ActionTemplateTool(ActionTool):
    def __init__(self):
        # TODO Modify fields as you want (pref_name should be unique)
        super().__init__(name="Action Tool",pref_name="action_template",
                         description="Run the Template Action", button_text="Run", tooltip="Descriptive tooltip")

    def _action(self):
        # TODO Enter the code you want the tool to execute
        print(self._name)
