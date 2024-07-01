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



def register():
    bpy.utils.register_class(MESH_OT_node_searcher)



def unregister():
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
