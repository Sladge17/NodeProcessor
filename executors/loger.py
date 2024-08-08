class Loger:

    @classmethod
    def node_output_not_exist(cls, type:str, name:str) -> None:
        print(f"{type.upper()} \"{name}\" does not have NODE \"Material Output\"")


    @classmethod
    def useless_nodes_not_exist(cls, type:str, name:str) -> None:
        print(f"{type.upper()} \"{name}\" does not have useless nodes")


    @classmethod
    def useless_nodes_list(cls, type:str, name:str, nodes_name:iter, nodes_type:iter) -> None:
        print(f"{type.upper()} \"{name}\" has useless nodes:")
        for node_name, node_type in zip(nodes_name, nodes_type):
            print(f" - NODE \"{node_name}\" of TYPE \"{node_type}\"")


    @classmethod
    def _materials_in_need(cls, materials:iter) -> None:
        if  not len(materials):
            print("(not using in materials)")
            return
        
        if len(materials) == 1:
            print(f"(using in MATERIAL: \"{materials[0]}\")")
            return
        
        materials = ", ".join(map(lambda material: f"\"{material}\"", materials))
        print(f"(using in MATERIALS: {materials})")


    @classmethod
    def useless_nodes_list_with_usage(
        cls, type:str, name:str, nodes_name:iter, nodes_type:iter, materials:iter
    ) -> None:
        cls.useless_nodes_list(type, name, nodes_name, nodes_type)
        cls._materials_in_need(materials)
