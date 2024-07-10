from .executor import Executor



class MaterialExecutor(Executor):
    def __init__(self, material) -> None:
        super().__init__(
            type="material",
            name=material.name,
            material_canvas=material.node_tree,
            output_node_name='Material Output'
        )
