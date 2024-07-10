import bpy

from .executors import MaterialExecutor, GroupExecutor



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
    

    def _get_groups_holder(self) -> list:
        groups_bpy = bpy.data.node_groups
        groups_holder = [None] * len(groups_bpy)
        for i in range(len(groups_bpy)):
            groups_holder[i] = GroupExecutor(
                groups_bpy[i],
                list(map(
                    lambda material: material.name,
                    bpy.data.user_map(subset=bpy.data.node_groups)\
                    [bpy.data.node_groups[groups_bpy[i].name]]
                )),
            )

        return groups_holder


    def _process_nodes(self, holder):
        for executor in holder:
            executor.process_nodes()


    def _log_instances_info(self, holder):
        for executor in holder:
            executor.log_instance_info()


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
