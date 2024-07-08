import bpy



class MaterialData:
    def __init__(self, material) -> None:
        self._material = material
        self._useful_nodes = []
        self._useless_nodes = []


    def _set_useful_node(self, parent_node) -> None:
        for node_input in parent_node.inputs:
            if node_input.is_linked:
                self._useful_nodes.append(node_input.links[0].from_node)
                self._set_useful_node(node_input.links[0].from_node)


    def _set_useful_nodes(self) -> None:
        self._set_useful_node(self._material.node_tree.nodes['Material Output'])


    def _set_useless_nodes(self) -> None:
        for node in self._material.node_tree.nodes:
            if node.name == 'Material Output':
                continue

            if not node in self._useful_nodes:
                self._useless_nodes.append(node)


    def sort_material_nodes(self):
        self._set_useful_nodes()
        self._set_useless_nodes()



class MESH_OT_node_processor(bpy.types.Operator):
    """Processing useless nodes"""
    bl_idname = "material.node_processor"
    bl_label = "Node Processor"
    bl_description = "Processing useless nodes"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context) -> bool:
        return True
    
    
    def _get_materials_data(self) -> list:
        materials_bpy = bpy.data.materials
        materials = [None] * (len(materials_bpy) - 1)
        i = 0
        for material in materials_bpy:
            if material.name == 'Dots Stroke':
                continue

            materials[i] = MaterialData(material)
            i += 1

        return materials    
    

    def _sort_materials_nodes(self, materials_data):
        for material_data in materials_data:
            material_data.sort_material_nodes()


    def execute(self, context):
        materials_data = self._get_materials_data()
        self._sort_materials_nodes(materials_data)

        print(materials_data[0]._useless_nodes)
        print(materials_data[1]._useless_nodes)

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
