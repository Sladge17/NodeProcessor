import bpy


OFFSET_OUTER_X = 200

OFFSET_INNER_X = 100
OFFSET_INNER_Y = 100

USELESS_NODES = "Useless nodes"



class Logger:

    @classmethod
    def node_output_not_exist(cls, type:str, name:str) -> None:
        print(f"{type.upper()} \"{name}\" does not have NODE \"Material Output\"")


    @classmethod
    def useless_nodes_not_exist(cls, type:str, name:str) -> None:
        print(f"{type.upper()} \"{name}\" does not have useless nodes")


    @classmethod
    def useless_nodes_list(cls, type:str, name:str, nodes_name:iter, nodes_type:iter) -> None:
        print(f"{type.upper()} \"{name}\" has useless nodes:")
        for node_name, node_type in zip(nodes_name, nodes_type):
            print(f" - NODE \"{node_name}\" of TYPE \"{node_type}\"")


    @classmethod
    def _materials_in_need(cls, materials:iter) -> None:
        if  not len(materials):
            print("(not using in materials)")
            return
        
        if len(materials) == 1:
            print(f"(using in MATERIAL: \"{materials[0]}\")")
            return
        
        materials = ", ".join(map(lambda material: f"\"{material}\"", materials))
        print(f"(using in MATERIALS: {materials})")


    @classmethod
    def useless_nodes_list_with_usage(
        cls, type:str, name:str, nodes_name:iter, nodes_type:iter, materials:iter
    ) -> None:
        cls.useless_nodes_list(type, name, nodes_name, nodes_type)
        cls._materials_in_need(materials)



class Executor:
    def __init__(self, type, name, material_canvas, output_node_name) -> None:
        self._type =type
        self._name = name
        self._material_canvas = material_canvas
        self._output_node_name = output_node_name
        self._valid_instance = True
        self._useful_nodes_list = []
        self._useless_nodes_list = []
        self._useful_nodes_border = [float('inf'), float('-inf')]
        self._location_y_min = float('inf')
        self._nodes_attribute_list = []


    def _remove_node_frame(self) -> None:
        for node in self._material_canvas.nodes:
            if node.type == 'FRAME' and node.label == USELESS_NODES:
                self._material_canvas.nodes.remove(node)


    def _set_useful_node(self, parent_node) -> None:
        for inpt in parent_node.inputs:
            if inpt.is_linked:
                self._useful_nodes_list.append(inpt.links[0].from_node)
                self._set_useful_node(inpt.links[0].from_node)


    def _set_useful_nodes_list(self) -> None:
        try:
            node_output = self._material_canvas.nodes[self._output_node_name]
        except KeyError:
            self._valid_instance = False
            return
        
        self._set_useful_node(node_output)


    def _set_useless_nodes_list(self) -> None:
        for node in self._material_canvas.nodes:
            if node.name == self._output_node_name:
                continue

            if not node in self._useful_nodes_list:
                self._useless_nodes_list.append(node)


    def _sort_nodes(self) -> None:
        self._set_useful_nodes_list()
        self._set_useless_nodes_list()


    def _set_useful_nodes_border(self) -> None:
        for node in self._useful_nodes_list:
            self._useful_nodes_border[0] =\
                min(self._useful_nodes_border[0], node.location[0])
            self._useful_nodes_border[1] =\
                max(self._useful_nodes_border[1], node.location[1])
    
    
    def _get_linked_output(self, node):
        for output in node.outputs:
            if output.is_linked:
                return output
            
        return None
    

    def _get_first_node(self, node):
        output = self._get_linked_output(node)
        while output:
            node = output.links[0].to_node
            output = self._get_linked_output(node)
        
        return node
    
    
    def _shift_useless_node(self, inpt, location, shifted_nodes) -> None:
        node = inpt.links[0].from_node
        self._process_useless_node(
            node,
            [
                location[0] - OFFSET_INNER_X - node.width,
                location[1],
            ],
            shifted_nodes,
        )
        location[1] -= node.height + OFFSET_INNER_Y
        self._location_y_min = min(self._location_y_min, location[1])


    def _set_node_attribute(self, inpt, location) -> None:
        node =\
            self._material_canvas.nodes.new(type='ShaderNodeAttribute')
        self._nodes_attribute_list.append(node)
        
        node.location = (
            location[0] - OFFSET_INNER_X - node.width,
            location[1],
        )
        self._material_canvas.links.new(
            node.outputs['Alpha'],
            inpt,
        )
        location[1] -= node.height + OFFSET_INNER_Y
        self._location_y_min = min(self._location_y_min, location[1])


    def _process_useless_node(self, node, location, shifted_nodes) -> None:
            node.location = location
            shifted_nodes.append(node)

            for inpt in node.inputs:
                if inpt.is_linked:
                    self._shift_useless_node(inpt, location, shifted_nodes)
                    continue

                self._set_node_attribute(inpt, location)

    
    def _process_useless_nodes(self) -> None:
        shifted_nodes = []
        not_shifted_nodes = set(self._useless_nodes_list)
        
        while not_shifted_nodes:
            for node in not_shifted_nodes:
                node = self._get_first_node(node)
                self._process_useless_node(
                    node,
                    [
                        self._useful_nodes_border[0] - OFFSET_OUTER_X - node.width,
                        self._useful_nodes_border[1],
                    ],
                    shifted_nodes,
                )
                self._useful_nodes_border[1] = min(
                    self._useful_nodes_border[1] - node.height - OFFSET_INNER_Y,
                    self._location_y_min,
                )
                not_shifted_nodes -= set(shifted_nodes)
                break


    def _set_node_frame(self) -> None:
        if not self._useless_nodes_list:
            return

        node_frame =\
            self._material_canvas.nodes.new(type='NodeFrame')
        node_frame.label = USELESS_NODES

        for node in self._useless_nodes_list:
            node.parent = node_frame

        for node in self._nodes_attribute_list:
            node.parent = node_frame


    def process_nodes(self) -> None:
        self._remove_node_frame()
        self._sort_nodes()
        if not self._valid_instance or not self._useless_nodes_list:
            return
        
        self._set_useful_nodes_border()
        self._process_useless_nodes()
        self._set_node_frame()


    def log_instance_info(self) -> None:
        if not self._valid_instance:
            Logger.node_output_not_exist(self._type, self._name)
            return
        
        if not self._useless_nodes_list:
            Logger.useless_nodes_not_exist(self._type, self._name)
            return
        
        if self._type == 'material':
            Logger.useless_nodes_list(
                self._type,
                self._name,
                map(lambda node: node.name, self._useless_nodes_list),
                map(lambda node: node.type, self._useless_nodes_list),
            )
            return

        Logger.useless_nodes_list_with_usage(
            self._type,
            self._name,
            map(lambda node: node.name, self._useless_nodes_list),
            map(lambda node: node.type, self._useless_nodes_list),
            self._materials,
        )



class GroupExecutor(Executor):
    def __init__(self, group) -> None:
        super().__init__(
            type="group",
            name=group.name,
            material_canvas=group,
            output_node_name='Group Output'
        )
        self._materials = list(map(
            lambda material: material.name,
            bpy.data.user_map(subset=bpy.data.node_groups)\
            [bpy.data.node_groups[self._name]]
        ))



class MaterialExecutor(Executor):
    def __init__(self, material) -> None:
        super().__init__(
            type="material",
            name=material.name,
            material_canvas=material.node_tree,
            output_node_name='Material Output'
        )



class MESH_OT_node_processor(bpy.types.Operator):
    """Processing useless nodes"""
    bl_idname = "material.node_processor"
    bl_label = "Node Processor"
    bl_description = "Processing useless nodes"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context) -> bool:
        return True
    
    
    def _get_materials_holder(self) -> list:
        materials_bpy = bpy.data.materials
        materials_holder = [None] * (len(materials_bpy) - 1)
        i = 0
        for material in materials_bpy:
            if material.name == 'Dots Stroke':
                continue

            materials_holder[i] = MaterialExecutor(material)
            i += 1

        return materials_holder    
    

    def _process_nodes(self, holder):
        for executor in holder:
            executor.process_nodes()


    def _log_instances_info(self, holder):
        for executor in holder:
            executor.log_instance_info()


    def _get_groups_holder(self) -> list:
        groups_bpy = bpy.data.node_groups
        groups_holder = [None] * len(groups_bpy)
        for i in range(len(groups_bpy)):
            groups_holder[i] = GroupExecutor(groups_bpy[i])

        return groups_holder


    def execute(self, context):
        materials_holder = self._get_materials_holder()
        group_holder = self._get_groups_holder()
        self._process_nodes(materials_holder)
        self._process_nodes(group_holder)
        self._log_instances_info(materials_holder)
        self._log_instances_info(group_holder)
        return {'FINISHED'}



class VIEW3D_PT_node_processor(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MaterialTools"
    bl_label = "NodeProcessor"


    def draw(self, context):
        column = self.layout.column(align=True)
        column.operator(
            'material.node_processor',
            text="Process useless nodes",
        )
        column.scale_y = 1.4



def register():
    bpy.utils.register_class(MESH_OT_node_processor)
    bpy.utils.register_class(VIEW3D_PT_node_processor)



def unregister():
    bpy.utils.register_class(VIEW3D_PT_node_processor)
    bpy.utils.unregister_class(MESH_OT_node_processor)



bl_info = {
    "name": "Node Processor",
    "author": "Sosov Maxim",
    "version": (1, 1),
    "blender": (3, 6, 0),
    "category": "",
    "location": "VIEW_3D > UI > MaterialTools > NodeProcessor",
    "description": "Processing useless nodes",
    "warning": "",
    "doc_url": "",
    "wiki_url": "",
}



if __name__ == "__main__":
    register()
