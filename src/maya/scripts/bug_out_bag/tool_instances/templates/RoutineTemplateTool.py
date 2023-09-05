from tool_models.RoutineTool import *


class RoutineTemplateTool(RoutineTool):

    def __init__(self):
        # TODO Modify fields as you want (pref_name should be unique)
        steps = {
            "step_1": {
                "action": self.__action_1,
                "text": "Step 1"
            },
            "step_2": {
                "action": self.__action_2,
                "text": "Step 2"
            },
            "step_3": {
                "action": self.__action_3,
                "text": "Step 3",
                "checked": False
            }
        }
        super().__init__(name="Routine Template Tool", pref_name="routine_template",
                         steps=steps, button_text="Run", tooltip="Descriptive tooltip" , step_checked_default=True)

    def __action_1(self):
        # TODO Enter the code you want the tool to execute on action 1
        print("Step 1")

    def __action_2(self):
        # TODO Enter the code you want the tool to execute on action 2
        print("Step 2")

    def __action_3(self):
        # TODO Enter the code you want the tool to execute on action 3
        print("Step 3")

    # ...