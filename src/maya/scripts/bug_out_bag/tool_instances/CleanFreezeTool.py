from ..tool_models.ActionTool import *


class CleanFreezeTool(ActionTool):

    @staticmethod
    def __get_transforms_selected():
        """
        Get all the transform Nodes selected (recursive)
        :return: transform Nodes selected
        """
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
        """
        Action that perform the CleanFreeze process
        :return:
        """
        self.__unlock_selection()
        self.__delete_history()
        self.__freeze_transform()
        self.__center_pivot()
        self.__lock_selection()

    def __freeze_transform(self):
        """
        Freeze all the transform selected
        :return:
        """
        for item in self.__selection:
            pm.makeIdentity(item["transform"], apply=True)

    def __center_pivot(self):
        """
        Center the pivot of all transform selected
        :return:
        """
        for item in self.__selection:
            pm.xform(item["transform"], pivots=(0, 0, 0), worldSpace=True)

    def __delete_history(self):
        """
        Delete the history of all the transform selected
        :return:
        """
        for item in self.__selection:
            pm.delete(item["transform"], constructionHistory=True)

    def __retrieve_selection(self):
        """
        Retrieve all the values of transform Nodes selected
        :return:
        """
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
        """
        Unlock all the nodes selected
        :return:
        """
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
        """
        Lock all the nodes selected
        :return:
        """
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

    def __refresh_btn(self):
        """
        Refresh the button
        :return:
        """
        self._action_btn.setEnabled(len(self.__selection) > 0)

    def on_selection_changed(self):
        """
        Refresh the button on selection changed
        :return:
        """
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        """
        Populate the CleanFreezeTool UI
        :return: layout
        """
        layout = super(CleanFreezeTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
