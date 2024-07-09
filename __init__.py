import bpy


OFFSET_OUTER_X = 200

OFFSET_INNER_X = 100
OFFSET_INNER_Y = 100

USELESS_NODES = "Useless nodes"



class Logger:

    @classmethod
    def node_material_output_not_exist(cls, material_name:str) -> None:
        print(f"MATERIAL \"{material_name}\" does not have NODE \"Material Output\"")


    @classmethod
    def useless_nodes_not_exist(cls, material_name:str) -> None:
        print(f"MATERIAL \"{material_name}\" does not have useless nodes")


    @classmethod
    def useless_nodes_list(cls, material_name:str, nodes_name:iter, nodes_type:iter) -> None:
        print(f"MATERIAL \"{material_name}\" has useless nodes:")
        for name, type in zip(nodes_name, nodes_type):
            print(f" - NODE \"{name}\" of TYPE \"{type}\"")



class MaterialExecutor:
    def __init__(self, material) -> None:
        self._material = material
        self._valid_material = True
        self._useful_nodes_list = []
        self._useless_nodes_list = []
        self._useful_nodes_border = [float('inf'), float('-inf')]
        self._location_y_min = float('inf')
        self._nodes_attribute_list = []


    def _set_useful_node(self, parent_node) -> None:
        for inpt in parent_node.inputs:
            if inpt.is_linked:
                self._useful_nodes_list.append(inpt.links[0].from_node)
                self._set_useful_node(inpt.links[0].from_node)


    def _set_useful_nodes_list(self) -> None:
        try:
            node_material_output = self._material.node_tree.nodes['Material Output']
        except KeyError:
            self._valid_material = False
            return
        
        self._set_useful_node(node_material_output)



    def _set_useless_nodes_list(self) -> None:
        for node in self._material.node_tree.nodes:
            if node.name == 'Material Output':
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
            self._material.node_tree.nodes.new(type='ShaderNodeAttribute')
        self._nodes_attribute_list.append(node)
        
        node.location = (
            location[0] - OFFSET_INNER_X - node.width,
            location[1],
        )
        self._material.node_tree.links.new(
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
            self._material.node_tree.nodes.new(type='NodeFrame')
        node_frame.label = USELESS_NODES

        for node in self._useless_nodes_list:
            node.parent = node_frame

        for node in self._nodes_attribute_list:
            node.parent = node_frame


    def _remove_node_frame(self) -> None:
        for node in self._material.node_tree.nodes:
            if node.type == 'FRAME' and node.label == USELESS_NODES:
                self._material.node_tree.nodes.remove(node)
    
    
    def process_material_nodes(self) -> None:
        self._remove_node_frame()
        self._sort_nodes()
        if not self._valid_material or not self._useless_nodes_list:
            return
        
        self._set_useful_nodes_border()
        self._process_useless_nodes()
        self._set_node_frame()


    def log_material_info(self) -> None:
        if not self._valid_material:
            Logger.node_material_output_not_exist(self._material.name)
            return
        
        if not self._useless_nodes_list:
            Logger.useless_nodes_not_exist(self._material.name)
            return
        
        Logger.useless_nodes_list(
            self._material.name,
            map(lambda node: node.name, self._useless_nodes_list),
            map(lambda node: node.type, self._useless_nodes_list),
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
        materials = [None] * (len(materials_bpy) - 1)
        i = 0
        for material in materials_bpy:
            if material.name == 'Dots Stroke':
                continue

            materials[i] = MaterialExecutor(material)
            i += 1

        return materials    
    

    def _process_materials_nodes(self, material_holder):
        for material_executor in material_holder:
            material_executor.process_material_nodes()


    def _log_materials_info(self, material_holder):
        for material_executor in material_holder:
            material_executor.log_material_info()


    def execute(self, context):
        materials_holder = self._get_materials_holder()
        self._process_materials_nodes(materials_holder)
        self._log_materials_info(materials_holder)
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
            icon='FILE_TEXT',
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
