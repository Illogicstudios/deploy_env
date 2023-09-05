import maya.OpenMaya as OpenMaya
from ..tool_models.ActionTool import *
from common.utils import *


class RestPosToVertexColorTool(ActionTool):

    @staticmethod
    def store_rest(shape):
        """
        Store the rest pos to the color vertex of the shape
        :param shape
        :return:
        """
        print(shape)
        color_set_name = "Pref"

        mobj = shape.__apimobject__()
        dag_path = shape.__apimdagpath__()
        mesh_fn = OpenMaya.MFnMesh(mobj)

        # Check if the color set exists and create it if it doesn't
        existing_color_sets = pm.polyColorSet(shape, query=True, allColorSets=True) or []

        if color_set_name not in existing_color_sets:
            pm.polyColorSet(shape, create=True, colorSet=color_set_name, clamped=False, rpt="RGB")

        # Set "Pref" as the current color set
        mesh_fn.setCurrentColorSetName(color_set_name)

        vertex_color_list = OpenMaya.MColorArray()
        mesh_fn.getVertexColors(vertex_color_list)
        len_vertex_list = vertex_color_list.length()

        fn_component = OpenMaya.MFnSingleIndexedComponent()
        fn_component.create(OpenMaya.MFn.kMeshVertComponent)
        fn_component.setCompleteData(len_vertex_list)

        vertex_index_list = OpenMaya.MIntArray()
        fn_component.getElements(vertex_index_list)

        # Get the vertex positions using the provided code
        in_mesh_m_point_array = OpenMaya.MPointArray()
        current_in_mesh_m_fn_mesh = OpenMaya.MFnMesh(dag_path)
        current_in_mesh_m_fn_mesh.getPoints(in_mesh_m_point_array, OpenMaya.MSpace.kWorld)

        point_list = []
        for i in range(in_mesh_m_point_array.length()):
            point_list.append([in_mesh_m_point_array[i][0], in_mesh_m_point_array[i][1], in_mesh_m_point_array[i][2]])

        # Set the vertex colors using the vertex positions
        for k in range(len_vertex_list):
            vertex_color_list[k].r = point_list[k][0]
            vertex_color_list[k].g = point_list[k][1]
            vertex_color_list[k].b = point_list[k][2]

        mesh_fn.setVertexColors(vertex_color_list, vertex_index_list, None)

    def __init__(self):
        super().__init__(name="Rest Pos to Vertex Color", pref_name="rest_pos_to_vertex_color_tool",
                         description="Store rest position to the vertex color", button_text="Store")
        self.__selection = []

    def _action(self):
        """
        Rest pos to Color Vertex on all selected transforms and shapes
        :return:
        """
        selection = self.__selection
        for elem in selection:
            RestPosToVertexColorTool.store_rest(elem)
        pm.select(selection)

    def __refresh_btn(self):
        """
        Refresh the button
        :return:
        """
        self._action_btn.setEnabled(len(self.__selection) > 0)

    def __retrieve_selection(self):
        """
        Retrieve the selected transforms and shapes
        :return:
        """
        transform = pm.ls(sl=True)
        shapes = pm.ls(sl=True, shapes=True)
        self.__selection = pm.listRelatives(transform, ad=True, type="mesh")
        for shape in shapes:
            if shape not in self.__selection:
                self.__selection.append(shape)

    def on_selection_changed(self):
        """
        Refresh the button on selection changed
        :return:
        """
        self.__retrieve_selection()
        self.__refresh_btn()

    def populate(self):
        """
        Populate the RestPosToColorVertexTool UI
        :return:
        """
        layout = super(RestPosToVertexColorTool, self).populate()
        self.__retrieve_selection()
        self.__refresh_btn()
        return layout
