from ..tool_models.ActionTool import *


class ShadingGroupRenamer(ActionTool):
    def __init__(self):
        super().__init__(name="Shading Group Renamer",pref_name="shading_group_renamer",
                         description="Rename Shading Group from Surface Shader", button_text="Rename")

    def _action(self):
        # Get all shading groups in the scene
        shading_groups = pm.ls(type='shadingEngine')

        # Iterate through shading groups
        for sg in shading_groups:
            # Find connected surface shader
            surface_shader = sg.surfaceShader.listConnections()
            try:
                if surface_shader:
                    old_name = sg.name()
                    shader = surface_shader[0]
                    # Rename the shading group based on the surface shader's name
                    new_sg_name = shader.nodeName() + '_SG'
                    rename(sg, new_sg_name)
                    print(f'Renamed {old_name} to {new_sg_name}')
                else:
                    print(f'Skipping {sg} as no surface shader is connected')
            except:
                    print(f'Error while trying to rename {sg}')
