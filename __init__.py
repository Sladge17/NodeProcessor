import bpy



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
    

    def _log_useless_nodes(self, useless_nodes:dict) -> None:
        for useless_node in useless_nodes:
            print(f"NODE: {useless_node.node.name} of TYPE: {useless_node.node.type} for MATERIAL: {useless_node.material.name}")


    def execute(self, context):
        useless_nodes = self._get_useless_nodes(self._get_materials())
        self._log_useless_nodes(useless_nodes)
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
