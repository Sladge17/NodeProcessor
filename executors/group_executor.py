from .executor import Executor



class GroupExecutor(Executor):
    def __init__(self, group, materials) -> None:
        super().__init__(
            type="group",
            name=group.name,
            material_canvas=group,
            output_node_name='Group Output'
        )
        self._materials = materials
