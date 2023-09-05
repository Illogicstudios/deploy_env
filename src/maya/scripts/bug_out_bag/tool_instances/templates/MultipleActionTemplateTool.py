from tool_models.MultipleActionTool import *


class MultipleActionTemplateTool(MultipleActionTool):
    def __init__(self):
        # TODO modify fields as you want (pref_name should be unique)
        actions = {
            "action_1": {
                "text": "Action 1",
                "action": self.__action_1,
                "row": 0
            },
            "action_2": {
                "text": "Action 2",
                "action": self.__action_2,
                "row": 1
            },
            "action_3": {
                "text": "Action 3",
                "action": self.__action_3
            },
            "action_4": {
                "text": "Action 4",
                "action": self.__action_4,
                "row": 1,
                "stretch": 2
            }
        }
        super().__init__(name="Multiple Action Tool", pref_name="multiple_action_template",
                         actions=actions, stretch=1, tooltip="Descriptive tooltip")

    def __action_1(self):
        # TODO Enter the code you want the tool to execute on action 1
        print("Action 1")

    def __action_2(self):
        # TODO Enter the code you want the tool to execute on action 2
        print("Action 2")

    def __action_3(self):
        # TODO Enter the code you want the tool to execute on action 3
        print("Action 3")

    def __action_4(self):
        # TODO Enter the code you want the tool to execute on action 4
        print("Action 4")

    # ...
