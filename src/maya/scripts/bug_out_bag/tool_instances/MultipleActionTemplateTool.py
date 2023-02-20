from tool_models.MultipleActionTool import *


class MultipleActionTemplateTool(MultipleActionTool):

    def __init__(self):
        actions = [
            {
                "text": "Action 1",
                "action": self.__action_1,
                "row":0
            },
            {
                "text": "Action 2",
                "action": self.__action_2,
                "row":1
            },
            {
                "text": "Action 3",
                "action": self.__action_3
            },
            {
                "text": "Action 4",
                "action": self.__action_4,
                "row":1
            }
        ]
        super().__init__(name="Multiple Action Tool", pref_name="multiple_action_template_tool",
                         actions=actions, stretch=True)

    def __action_1(self):
        print("Action 1")

    def __action_2(self):
        print("Action 2")

    def __action_3(self):
        print("Action 3")

    def __action_4(self):
        print("Action 4")