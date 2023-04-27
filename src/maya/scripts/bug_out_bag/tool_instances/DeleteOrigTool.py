from ..tool_models.ActionTool import *


class DeleteOrigTool(ActionTool):
    def __init__(self):
        super().__init__(name="Delete Orig", pref_name="delete_orig_tool",
                         description="Delete orig objects of the selected objects", button_text="Delete")
        self.__selection = []

    def _action(self):
        if len(self.__selection) > 0:
            unused_intermediate_objects = []
            for node in self.__selection:
                if len(node.inputs()) == 0 \
                        and len(node.outputs()) == 0 \
                        and node.intermediateObject.get() \
                        and node.referenceFile() is None:
                    unused_intermediate_objects.append(node)
            pm.delete(unused_intermediate_objects)

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(len(self.__selection) > 0)

    def __retrieve_selection(self):
        selection = pm.ls(sl=True)
        self.__selection = pm.listRelatives(selection,shapes=True, allDescendents=True, type="mesh")

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        layout = super(DeleteOrigTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
