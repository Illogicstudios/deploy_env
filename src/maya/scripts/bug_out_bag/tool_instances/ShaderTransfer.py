from tool_models.ActionTool import *
from utils import *


class ShaderTransfer(ActionTool):

    def __init__(self):
        tooltip = "Select a 2 objects (first is the source and second is the target) then click Transfer"
        super().__init__(name="Shader Transfer", pref_name="shader_transfer_tool",
                         description="Transfer shading sets (need 2 selections)",
                         button_text="Transfer", tooltip=tooltip)

    def _action(self):
        selection = ls(sl=True)

        if len(selection) >= 2:
            meshes_source = listRelatives(selection[0], allDescendents=True, type="mesh")
            meshes_target = listRelatives(selection[1], allDescendents=True, type="mesh")

            for mesh_s in meshes_source:
                if "ShapeOrig" not in mesh_s.name():
                    mesh_s_name = mesh_s.name(long=None)
                    for mesh_t in meshes_target:
                        mesh_t_name = mesh_t.name(long=None)
                        if mesh_s_name == mesh_t_name:
                            select(mesh_s, r=True)
                            select(mesh_t, tgl=True)
                            transferShadingSets(sampleSpace=0, searchMethod=3)

    # Refresh the button
    def __refresh_btn(self):
        self._action_btn.setEnabled(len(ls(sl=True)) >= 2)

    # Refresh the button on selection changed
    def on_selection_changed(self):
        self.__refresh_btn()

    def on_populate_done(self):
        self.__refresh_btn()
