from ..tool_models.ActionTool import *
from common.utils import *


class ShaderTransferTool(ActionTool):

    def __init__(self):
        tooltip = "Select 2 objects (first is the source and second is the target) then click Transfer"
        super().__init__(name="Shader Transfer", pref_name="shader_transfer_tool",
                         description="Transfer shading sets (need 2 selections)",
                         button_text="Transfer", tooltip=tooltip)
        self.__selection = []

    def _action(self):
        """
        Transfer shader from first selection to second selection
        :return:
        """
        if len(self.__selection) >= 2:
            meshes_source = pm.listRelatives(self.__selection[0], allDescendents=True, type="mesh")
            meshes_target = pm.listRelatives(self.__selection[1], allDescendents=True, type="mesh")

            for mesh_s in meshes_source:
                if "ShapeOrig" not in mesh_s.name():
                    mesh_s_name = mesh_s.name(long=None)
                    for mesh_t in meshes_target:
                        mesh_t_name = mesh_t.name(long=None)
                        if mesh_s_name == mesh_t_name:
                            pm.select(mesh_s, r=True)
                            pm.select(mesh_t, tgl=True)
                            pm.transferShadingSets(sampleSpace=0, searchMethod=3)

    def __refresh_btn(self):
        """
        Refresh the button
        :return:
        """
        self._action_btn.setEnabled(len(self.__selection) >= 2)

    def __retrieve_selection(self):
        """
        Retrieve the selection
        :return:
        """
        self.__selection = pm.ls(sl=True)

    def on_selection_changed(self):
        """
        Refresh the button on selection changed
        :return:
        """
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        """
        Populate the ShaderTransferTool
        :return:
        """
        layout = super(ShaderTransferTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
