from ..tool_models.ActionTool import *


class CleanFreezeTool(ActionTool):

    @staticmethod
    def __get_transforms_selected():
        selection = pm.ls(selection=True, type="transform")
        selection_arr = []
        selection_arr.extend(selection)
        for sel in selection:
            selection_arr.extend(pm.listRelatives(sel, allDescendents=True, type="transform"))
        return selection_arr

    def __init__(self):
        tooltip = "Freeze Transform of selection and set the pivot to (0,0,0) in world"
        super().__init__(name="Clean Freeze", pref_name="clean_freeze",
                         description="Freeze Transform and center pivot", button_text="Run", tooltip=tooltip)
        self.__selection = []

    def _action(self):
        self.__unlock_selection()
        self.__delete_history()
        self.__freeze_transform()
        self.__center_pivot()
        self.__lock_selection()

    def __freeze_transform(self):
        for item in self.__selection:
            pm.makeIdentity(item["transform"], apply=True)

    def __center_pivot(self):
        for item in self.__selection:
            pm.xform(item["transform"], pivots=(0, 0, 0), worldSpace=True)

    def __delete_history(self):
        for item in self.__selection:
            pm.delete(item["transform"], constructionHistory=True)

    def __retrieve_selection(self):
        selection = CleanFreezeTool.__get_transforms_selected()
        self.__selection.clear()
        for transform in selection:
            item = {
                "transform": transform,
                "translate": transform.translate.isLocked(),
                "translateX": transform.translateX.isLocked(),
                "translateY": transform.translateY.isLocked(),
                "translateZ": transform.translateZ.isLocked(),
                "rotate": transform.rotate.isLocked(),
                "rotateX": transform.rotateX.isLocked(),
                "rotateY": transform.rotateY.isLocked(),
                "rotateZ": transform.rotateZ.isLocked(),
                "scale": transform.scale.isLocked(),
                "scaleX": transform.scaleX.isLocked(),
                "scaleY": transform.scaleY.isLocked(),
                "scaleZ": transform.scaleZ.isLocked(),
            }
            self.__selection.append(item)

    def __unlock_selection(self):
        for item in self.__selection:
            transform = item["transform"]
            if item["translate"]: transform.translate.unlock()
            if item["translateX"]: transform.translateX.unlock()
            if item["translateY"]: transform.translateY.unlock()
            if item["translateZ"]: transform.translateZ.unlock()
            if item["rotate"]: transform.rotate.unlock()
            if item["rotateX"]: transform.rotateX.unlock()
            if item["rotateY"]: transform.rotateY.unlock()
            if item["rotateZ"]: transform.rotateZ.unlock()
            if item["scale"]: transform.scale.unlock()
            if item["scaleX"]: transform.scaleX.unlock()
            if item["scaleY"]: transform.scaleY.unlock()
            if item["scaleZ"]: transform.scaleZ.unlock()

    def __lock_selection(self):
        for item in self.__selection:
            transform = item["transform"]
            if item["translate"]: transform.translate.lock()
            if item["translateX"]: transform.translateX.lock()
            if item["translateY"]: transform.translateY.lock()
            if item["translateZ"]: transform.translateZ.lock()
            if item["rotate"]: transform.rotate.lock()
            if item["rotateX"]: transform.rotateX.lock()
            if item["rotateY"]: transform.rotateY.lock()
            if item["rotateZ"]: transform.rotateZ.lock()
            if item["scale"]: transform.scale.lock()
            if item["scaleX"]: transform.scaleX.lock()
            if item["scaleY"]: transform.scaleY.lock()
            if item["scaleZ"]: transform.scaleZ.lock()

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(len(self.__selection) > 0)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        layout = super(CleanFreezeTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
