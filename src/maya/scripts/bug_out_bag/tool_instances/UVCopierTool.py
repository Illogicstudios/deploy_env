from tool_models.MultipleActionTool import *


class UVCopierTool(MultipleActionTool):

    def __init__(self):
        actions = {
            "current_to_default": {
                "text": "Current UV set to default",
                "action": self.__current_uv_to_default,
                "row": 0
            },
            "merge": {
                "text": "Merge all UV sets",
                "action": self.__merge_all_uv,
                "row": 0
            }
        }
        super().__init__(name="UV Copier", pref_name="uv_copier_tool",
                         actions=actions, stretch=1)
        self.__selected_shapes = []

    def __current_uv_to_default(self):
        for shape in self.__selected_shapes:
            default_uv = getAttr(shape.name() + ".uvSet[0].uvSetName")
            try:
                polyUVSet(shape, rename=True, newUVSet='map1', uvSet=default_uv)
            except:
                pass
            try:
                default_uv = getAttr(shape.name() + ".uvSet[0].uvSetName")
                # Get the current UV set
                current_uv_set = polyUVSet(query=True, currentUVSet=True)[0]

                uvs = polyListComponentConversion(shape, toUV=True)
                # Copy the current UV set to the default UV set
                polyCopyUV(uvs, uvi=current_uv_set, uvs=default_uv)

                # Delete all UV sets except the default
                for uv_set in polyUVSet(shape, q=1, allUVSets=1):
                    if uv_set != "map1":
                        polyUVSet(delete=True, uvSet=uv_set)
            except:
                print("Current UV Set to Default failed on %s" % shape.name())

    def __merge_all_uv(self):
        for shape in self.__selected_shapes:
            default_uv = getAttr(shape+".uvSet[0].uvSetName")
            all_uv_sets = polyUVSet(shape, q=1, allUVSets=1)
            all_uv_sets.remove(default_uv)
            for uv_set in all_uv_sets:
                polyUVSet(currentUVSet = True, uvSet=uv_set)
                uvs = polyListComponentConversion(shape, toUV=True)
                polyCopyUV( uvs, uvi= uv_set, uvs=default_uv )
                polyUVSet( delete=True, uvSet=uv_set)
            if default_uv != "map1":
                polyUVSet(shape, rename=True, newUVSet='map1', uvSet=default_uv)

    def __refresh_btn(self):
        enabled = len(self.__selected_shapes) > 0
        if "button" in self._actions["current_to_default"]:
            self._actions["current_to_default"]["button"].setEnabled(enabled)
        if "button" in self._actions["merge"]:
            self._actions["merge"]["button"].setEnabled(enabled)

    def __retrieve_datas(self):
        selection = ls(selection=True)
        self.__selected_shapes = listRelatives(selection, allDescendents=True, shapes=True)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__retrieve_datas()
        self.__refresh_btn()

    def populate(self):
        layout = super(UVCopierTool, self).populate()
        self.__retrieve_datas()
        self.__refresh_btn()
        return layout
