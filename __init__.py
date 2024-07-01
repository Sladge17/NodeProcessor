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



class MESH_OT_node_searcher(bpy.types.Operator):
    """Search useless nodes"""
    bl_idname = "material.node_searcher"
    bl_label = "Node searcher"
    bl_description = "Search useless nodes"
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
                origin[1] = min(origin[1], node.location[1])
            
            nodes_origin[material.name] = origin

        return nodes_origin  


    def _shift_useless_nodes(self, useless_nodes:list, node_origins:dict) -> None:
        is_first = True
        for useless_node in useless_nodes:
            if is_first:
                origin = node_origins[useless_node.material.name]
                origin[0] += Offsets.origin_shift_first.value
                origin[1] += Offsets.origin_shift_first.value
                useless_node.node.location = origin
                node_origins[useless_node.material.name] = origin
                is_first = False
                continue

            origin = node_origins[useless_node.material.name]
            origin[1] += Offsets.origin_shift_y.value
            useless_node.node.location = origin
            node_origins[useless_node.material.name] = origin


    def _set_node_attribute(self, useless_nodes:dict) -> None:
        for useless_node in useless_nodes:
            if not len(useless_node.node.inputs):
                continue

            cursor = useless_node.node.location.copy()
            cursor[0] += Offsets.origin_attr_x.value

            for node_input in useless_node.node.inputs:
                node_attribute =\
                    useless_node.material.node_tree.nodes.new(type='ShaderNodeAttribute')
                node_attribute.location = cursor

                useless_node.material.node_tree.links.new(
                    node_attribute.outputs['Alpha'],
                    node_input,
                )
                cursor[1] += Offsets.origin_attr_y.value        
    
    
    def execute(self, context):
        materials = self._get_materials()
        useless_nodes = self._get_useless_nodes(materials)
        self._log_useless_nodes(useless_nodes)
        node_origins = self._get_node_origins(materials)
        self._shift_useless_nodes(useless_nodes, node_origins)
        self._set_node_attribute(useless_nodes)
        return {'FINISHED'}



class VIEW3D_PT_node_searcher(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MaterialTools"
    bl_label = "NodeSearcher"


    def draw(self, context):
        column = self.layout.column(align=True)
        column.operator(
            'material.node_searcher',
            text="Print useless nodes",
            icon='FILE_TEXT',
        )
        column.scale_y = 1.4



def register():
    bpy.utils.register_class(MESH_OT_node_searcher)
    bpy.utils.register_class(VIEW3D_PT_node_searcher)



def unregister():
    bpy.utils.register_class(VIEW3D_PT_node_searcher)
    bpy.utils.unregister_class(MESH_OT_node_searcher)



bl_info = {
    "name": "Node Searcher",
    "author": "Sosov Maxim",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "category": "",
    "location": "",
    "description": "",
    "warning": "",
    "doc_url": "",
    "wiki_url": "",
}



if __name__ == "__main__":
    register()
