import bpy



class MESH_OT_node_searcher(bpy.types.Operator):
    """Search useless nodes"""
    bl_idname = "material.node_searcher"
    bl_label = "Node searcher"
    bl_description = "Search useless nodes"
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        return True


    def execute(self, context):
        print("test printing")
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
            text="Execute",
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
