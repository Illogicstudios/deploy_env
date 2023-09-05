from ..tool_models.MultipleActionTool import *


class TraceSetTool(MultipleActionTool):
    def __init__(self):
        actions = {
            "action_1": {
                "text": "Input Exclude group",
                "action": self.__register_exclude_grp,
                "row": 0
            },
            "action_2": {
                "text": "Input Target group",
                "action": self.__register_target_grp,
                "row": 0
            }
        }
        super().__init__(name="Trace Set Tool", pref_name="trace_set_tool",
                         actions=actions, stretch=1, tooltip="Exclude some geos (Exclude group) from another group of geos (Target group)")
        self.__exclude_grp = []
        self.__target_grp = []

    def _add_ui_after_buttons(self, lyt):
        """
        Add labels and a button after buttons in UI
        :param lyt:
        :return:
        """
        after_btn_lyt = QVBoxLayout()
        lyt.addLayout(after_btn_lyt)
        lbl_lyt = QHBoxLayout()
        stylesheet_lbl = "QLabel{font-weight:bold;}"
        after_btn_lyt.addLayout(lbl_lyt)

        self.__exclude_grp_label = QLabel()
        self.__exclude_grp_label.setStyleSheet(stylesheet_lbl)
        self.__exclude_grp_label.setAlignment(Qt.AlignCenter)
        lbl_lyt.addWidget(self.__exclude_grp_label)

        self.__target_grp_label = QLabel()
        self.__target_grp_label.setStyleSheet(stylesheet_lbl)
        self.__target_grp_label.setAlignment(Qt.AlignCenter)
        lbl_lyt.addWidget(self.__target_grp_label)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Raised)
        after_btn_lyt.addWidget(line)

        self.__trace_set_btn = QPushButton("Run Trace Set")
        self.__trace_set_btn.setStyleSheet("padding:3px 25px")
        self.__trace_set_btn.clicked.connect(self.__trace_set)
        after_btn_lyt.addWidget(self.__trace_set_btn, alignment=Qt.AlignCenter)

    def __register_exclude_grp(self):
        """
        Register the exclude group
        """
        self.__exclude_grp = pm.ls(sl=True)
        self.__refresh_ui()

    def __register_target_grp(self):
        """
        Register the target group
        """
        self.__target_grp = pm.ls(sl=True)
        self.__refresh_ui()

    def __trace_set(self):
        """
        Launch Trace Set
        """
        geo_set = self.__exclude_grp
        shading_group_set = self.__target_grp

        if geo_set and shading_group_set:
            # Step 2: Prompt the user for a trace set name
            trace_set_name = pm.promptDialog(title='Trace Set Name', message='Enter Trace Set Name:', button=['OK', 'Cancel'],text='block_trace', defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')

            if trace_set_name == 'OK':
                trace_set_name = pm.promptDialog(query=True, text=True)

                # Step 3: Set the trace set name to the trace_sets attribute of the shape of the objects in the geo set
                for obj in geo_set:
                    obj_shapes = TraceSetTool.__get_all_shapes(obj)
                    for obj_shape in obj_shapes:
                        if obj_shape:
                            if pm.attributeQuery('trace_sets', node=obj_shape, exists=True):
                                pm.setAttr(f'{obj_shape}.trace_sets', trace_set_name, type='string')
                            else:
                                pm.warning(f"The attribute 'trace_sets' does not exist on {obj_shape}")

                # Step 4: For the shaders of objects in the shading group set, create or update a trace set node between the shader and the shading group
                for obj in shading_group_set:
                    shading_grps = pm.listConnections(TraceSetTool.__get_all_shapes(obj), type='shadingEngine')
                    if shading_grps:
                        for shading_grp in shading_grps:
                            try:
                                trace_set_nodes = pm.listConnections(shading_grp.surfaceShader, type='aiTraceSet')
                                if trace_set_nodes:
                                    trace_set_node = trace_set_nodes[0]
                                else:
                                    trace_set_node = pm.shadingNode('aiTraceSet', asUtility=True, name=f'{trace_set_name}_aiTraceSet')
                                    shader = pm.listConnections(shading_grp.surfaceShader, source=True)
                                    if shader:
                                        shader[0].outColor >> trace_set_node.passthrough
                                        trace_set_node.outColor >> shading_grp.surfaceShader
                                    else:
                                        pm.warning(f"No shader connected to {shading_grp}")

                                trace_set_node.inclusive.set(0)
                                trace_set_node.trace_set.set(trace_set_name)
                            except Exception as e:
                                pm.warning(f"An error occurred while processing {shading_grp}: {str(e)}")
                    else:
                        pm.warning(f"No shading groups connected to {obj}")
        else:
            pm.warning("Invalid sets specified. Please check the set names and try again.")

    @staticmethod
    def __get_all_shapes(node):
        shapes = []
        for child in node.listRelatives(ad=True):
            if child.type() == 'mesh':
                shapes.append(child)
        return shapes

    def populate(self):
        """
        Populate the LockToolUI
        :return:
        """
        layout = super(TraceSetTool, self).populate()
        self.__refresh_ui()
        return layout

    def __refresh_ui(self):
        nb_exclude_grp = len(self.__exclude_grp)
        nb_target_grp = len(self.__target_grp)
        self.__exclude_grp_label.setText(str(nb_exclude_grp)+" in exclude group")
        self.__target_grp_label.setText(str(nb_target_grp)+" in target group")
        self.__trace_set_btn.setEnabled(nb_exclude_grp >0 and nb_target_grp>0)
