from tool_models.ActionTool import *


class RestPosToVertexColorTool(ActionTool):
    @staticmethod
    def store_rest(obj):
        rest = "Pref"
        colorSets = polyColorSet(query=True, allColorSets=True)

        if not colorSets or not rest in colorSets:
            polyColorSet(create=True, colorSet=rest, clamped=False, rpt="RGB")
        polyColorSet(obj, currentColorSet=True, colorSet=rest)
        verts = obj.verts
        for v in verts:
            pos = xform(v, q=True, ws=True, t=True)
            select(v)
            polyColorPerVertex(rgb=pos)

    def __init__(self):
        super().__init__(name="Rest Pos to Vertex Color",pref_name="rest_pos_to_vertex_color_tool",
                         description="Store rest position to the vertex color", button_text="Store")

    def _action(self):
        sel = ls(sl=True)
        for elem in listRelatives(sel, ad=True, type="mesh"):
            RestPosToVertexColorTool.store_rest(elem)

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(len(ls(sl=True)) > 0)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__refresh_btn()

    def on_populate_done(self):
        self.__refresh_btn()