from ..tool_models.RoutineTool import *


class CleanerTool(RoutineTool):

    def __init__(self):
        steps = {
            "optimize_scene_size": {
                "action": CleanerTool.__optimize_scene_size,
                "text": "Optimize scene size"
            },
            "delete_unknown_nodes": {
                "action": CleanerTool.__delete_unknown_node,
                "text": "Delete unknown nodes"
            },
            "remove_unknown_plugins": {
                "action": CleanerTool.__remove_unknown_plugins,
                "text": "Remove unknown plugins"
            },
            "unlock_all_nodes": {
                "action": CleanerTool.__unlock_all_nodes,
                "text": "Unlock all nodes"
            },
            "remove_cgabblastpanel_error": {
                "action": CleanerTool.__remove_blast_panel_error,
                "text": "Remove CgAbBlastPanel Error"
            },
            "fix_initialshadinggroup": {
                "action": CleanerTool.__fix_isg,
                "text": "Fix initialShadingGroup"
            }
        }
        super().__init__(name="Cleaner", pref_name="cleaner",
                         steps=steps, button_text="Clean",
                         step_checked_default=True, checkbox_pref=True)

    @staticmethod
    def __optimize_scene_size():
        """
        Optimize the scene size by cleaning the scene
        :return:
        """
        print("\nvvvvvvvvvvvvvvvv Optimize Scene Size vvvvvvvvvvvvvvvv")
        pm.mel.source('cleanUpScene')
        pm.mel.scOpt_performOneCleanup({
            "nurbsSrfOption",
            "setsOption",
            "transformOption",
            "renderLayerOption",
            "renderLayerOption",
            "animationCurveOption",
            "groupIDnOption",
            "unusedSkinInfsOption",
            "groupIDnOption",
            "shaderOption",
            "ptConOption",
            "pbOption",
            "snapshotOption",
            "unitConversionOption",
            "referencedOption",
            "brushOption",
            "unknownNodesOption",
        })
        print("^^^^^^^^^^^^^^^^ Optimize Scene Size ^^^^^^^^^^^^^^^\n")

    @staticmethod
    def __delete_unknown_node():
        """
        Delete all the unknown Nodes from the scene
        :return:
        """
        print("\nvvvvvvvvvvvvvvv Delete Unknown Nodes vvvvvvvvvvvvvvvv")
        unknown = pm.ls(type="unknown")
        if unknown:
            print("Removing:" + unknown)
            pm.delete(unknown)
        else:
            print("No unknown nodes found")
        print("^^^^^^^^^^^^^^^ Delete Unknown Nodes ^^^^^^^^^^^^^^^^\n")

    @staticmethod
    def __remove_unknown_plugins():
        """
        Remove the unknown Plugins from the scene
        :return:
        """
        print("\nvvvvvvvvvvvvvv Remove Unknown Plugins vvvvvvvvvvvvvvv")
        old_plug = pm.unknownPlugin(query=True, list=True)
        if old_plug:
            for plug in old_plug:
                print("Removing:" + plug)
                try:
                    pm.unknownPlugin(plug, remove=True)
                except Exception as e:
                    print(e)
        else:
            print("No unknown plugin found")
        print("^^^^^^^^^^^^^^ Remove Unknown Plugins ^^^^^^^^^^^^^^^\n")

    @staticmethod
    def __unlock_all_nodes():
        """
        Unlock all the Nodes in the scene
        :return:
        """
        print("\n------------------ Unlock All Nodes -----------------\n")
        all_nodes = pm.ls()
        if all_nodes:
            for node in all_nodes:
                pm.lockNode(node, l=False)

    @staticmethod
    def __remove_blast_panel_error():
        """
        Fix the CgAbBlastPanel Error
        :return:
        """
        print("\n------------ Remove CgAbBlastPanel Error ------------\n")
        for model_panel in pm.getPanel(typ="modelPanel"):
            # Get callback of the model editor
            callback = pm.modelEditor(model_panel, query=True, editorChanged=True)
            # If the callback is the erroneous `CgAbBlastPanelOptChangeCallback`
            if callback == "CgAbBlastPanelOptChangeCallback":
                # Remove the callbacks from the editor
                pm.modelEditor(model_panel, edit=True, editorChanged="")
        if pm.objExists("uiConfigurationScriptNode"):
            pm.delete("uiConfigurationScriptNode")

    @staticmethod
    def __fix_isg():
        """
        Fix the initialShadingGroup Error
        :return:
        """
        print("\n-------------- Fix initialShadingGroup --------------\n")
        pm.lockNode('initialShadingGroup', lock=0, lockUnpublished=0)
        pm.lockNode('initialParticleSE', lock=0, lockUnpublished=0)
