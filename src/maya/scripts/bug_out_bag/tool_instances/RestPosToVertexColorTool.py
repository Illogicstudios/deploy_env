from tool_models.ActionTool import *


class RestPosToVertexColorTool(ActionTool):
    @staticmethod
    def store_rest(obj):
        rest = "Pref"
        colorSets = pm.polyColorSet(query=True, allColorSets=True)

        if not colorSets or not rest in colorSets:
            pm.polyColorSet(create=True, colorSet=rest, clamped=False, rpt="RGB")
        pm.polyColorSet(obj, currentColorSet=True, colorSet=rest)
        verts = obj.verts
        for v in verts:
            pos = pm.xform(v, q=True, ws=True, t=True)
            pm.select(v)
            pm.polyColorPerVertex(rgb=pos)
        obj.aiExportColors.set(1)

    def __init__(self):
        super().__init__(name="Rest Pos to Vertex Color", pref_name="rest_pos_to_vertex_color_tool",
                         description="Store rest position to the vertex color", button_text="Store")
        self.__selection = []

    def _action(self):
        selection = self.__selection
        for elem in selection:
            RestPosToVertexColorTool.store_rest(elem)
        pm.select(selection)

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(len(self.__selection) > 0)

    def __retrieve_selection(self):
        transform = pm.ls(sl=True)
        self.__selection = pm.listRelatives(transform, ad=True, type="mesh")

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        layout = super(RestPosToVertexColorTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
