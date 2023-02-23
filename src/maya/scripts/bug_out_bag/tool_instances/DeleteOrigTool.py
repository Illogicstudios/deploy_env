from tool_models.ActionTool import *


class DeleteOrigTool(ActionTool):
    def __init__(self):
        super().__init__(name="Delete Orig", pref_name="delete_orig_tool",
                         description="Delete orig objects of the selected objects", button_text="Delete")

    def _action(self):
        selection = ls(sl=True)
        selected_shapes = listRelatives(selection,shapes=True, allDescendents=True, type="mesh")

        if len(selected_shapes) > 0:
            unused_intermediate_objects = []
            for node in selected_shapes:
                if len(node.inputs()) == 0 \
                        and len(node.outputs()) == 0 \
                        and node.intermediateObject.get() \
                        and node.referenceFile() is None:
                    unused_intermediate_objects.append(node)
            delete(unused_intermediate_objects)

    # Refresh the button
    def __refresh_btn(self):
        selection = ls(sl=True)
        selected_shapes = listRelatives(selection,shapes=True, allDescendents=True, type="mesh")
        self._action_btn.setEnabled(len(selected_shapes) > 0)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__refresh_btn()

    def populate(self):
        layout = super(DeleteOrigTool, self).populate()
        self.__refresh_btn()
        return layout
