import bpy
from enum import Enum



class Offsets(Enum):
    origin_attr_x = -200
    origin_attr_y = -200
    origin_shift_first = -100
    origin_shift_y = -300



class UselessNode:
    def __init__(self, material, node):
        self.material = material
        self.node = node



class MESH_OT_node_processor(bpy.types.Operator):
    """Processing useless nodes"""
    bl_idname = "material.node_processor"
    bl_label = "Node Processor"
    bl_description = "Processing useless nodes"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return True


    def _get_materials(self):
        materials = []
        for material in bpy.data.materials:
            if material.name == 'Dots Stroke':
                continue
            
            materials.append(material)

        return materials

    
    def _is_useful_node(self, node) -> bool:
        node_useful = False
        for output in node.outputs:
            if output.is_linked:
                node_useful = True
                break

        return node_useful
    
    
    def _get_useless_nodes(self, matetials:list) -> list:
        useless_nodes = []
        for material in matetials:
            for node in material.node_tree.nodes:
                if node.name == 'Material Output':
                    continue
                
                if self._is_useful_node(node):
                    continue

                useless_nodes.append(UselessNode(material, node))
        
        return useless_nodes
    

    def _log_useless_nodes(self, useless_nodes:list) -> None:
        for useless_node in useless_nodes:
            print(f"NODE: {useless_node.node.name} of TYPE: {useless_node.node.type} for MATERIAL: {useless_node.material.name}")


    def _get_node_origins(self, matetials:list) ->dict:
        nodes_origin = {}
        for material in matetials:
            origin = [float('inf'), float('inf')]
            for node in material.node_tree.nodes:
                origin[0] = min(origin[0], node.location[0])
                origin[1] = min(origin[1], node.location[1] - node.height)
            
            nodes_origin[material.name] = origin

        return nodes_origin  


    def _shift_useless_nodes(self, useless_nodes:list, node_origins:dict) -> None:
        is_first = True
        for useless_node in useless_nodes:
            if is_first:
                origin = node_origins[useless_node.material.name].copy()
                origin[0] += Offsets.origin_shift_first.value
                origin[1] += Offsets.origin_shift_first.value
                useless_node.node.location = (
                    origin[0] - useless_node.node.width,
                    origin[1]
                )
                is_first = False
                continue

            origin[1] += Offsets.origin_shift_y.value
            useless_node.node.location = (
                origin[0] - useless_node.node.width,
                origin[1]
            )


    def _set_node_attribute(self, useless_nodes:list, node_origins: dict) -> None:
        for origin in node_origins:
            node_origins[origin] += [0, 0]

        for useless_node in useless_nodes:
            if not len(useless_node.node.inputs):
                node_origins[useless_node.material.name][2] =\
                    useless_node.node.location[0] - useless_node.node.width
                node_origins[useless_node.material.name][3] =\
                    useless_node.node.location[1] - useless_node.node.height
                continue

            origin = useless_node.node.location.copy()
            origin[0] += Offsets.origin_attr_x.value

            for node_input in useless_node.node.inputs:
                node_attribute =\
                    useless_node.material.node_tree.nodes.new(type='ShaderNodeAttribute')
                node_attribute.location = origin

                useless_node.material.node_tree.links.new(
                    node_attribute.outputs['Alpha'],
                    node_input,
                )
                node_origins[useless_node.material.name][2] =\
                    node_attribute.location[0] - node_attribute.width
                node_origins[useless_node.material.name][3] =\
                    node_attribute.location[1] - node_attribute.height
                origin[1] += Offsets.origin_attr_y.value
    
    
    def _set_frame(self, node_origins: dict) -> None:
        for origin in node_origins:
            if not node_origins[origin][2]:
                continue

            frame = bpy.data.materials[origin].node_tree.nodes.new(type='NodeFrame')
            frame.location[0] = node_origins[origin][2]
            frame.location[1] = node_origins[origin][1]
            frame.width = node_origins[origin][0] - node_origins[origin][2]
            frame.height = node_origins[origin][1] - node_origins[origin][3] + 100
    
    
    def execute(self, context):
        materials = self._get_materials()
        useless_nodes = self._get_useless_nodes(materials)
        if not useless_nodes:
            print("MESSAGE: Useless nodes not exist")
            return {'FINISHED'}
        
        self._log_useless_nodes(useless_nodes)
        node_origins = self._get_node_origins(materials)
        self._shift_useless_nodes(useless_nodes, node_origins)
        self._set_node_attribute(useless_nodes, node_origins)
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
    "version": (1, 0),
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
