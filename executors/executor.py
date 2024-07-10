from .logger import Logger



OFFSET_OUTER_X = 200

OFFSET_INNER_X = 100
OFFSET_INNER_Y = 100

USELESS_NODES = "Useless nodes"



class Executor:
    def __init__(self, type, name, material_canvas, output_node_name) -> None:
        self._type =type
        self._name = name
        self._material_canvas = material_canvas
        self._output_node_name = output_node_name
        self._valid_instance = True
        self._useful_nodes_list = []
        self._useless_nodes_list = []
        self._useful_nodes_border = [float('inf'), float('-inf')]
        self._location_y_min = float('inf')
        self._nodes_attribute_list = []


    def _remove_node_frame(self) -> None:
        for node in self._material_canvas.nodes:
            if node.type == 'FRAME' and node.label == USELESS_NODES:
                self._material_canvas.nodes.remove(node)


    def _set_useful_node(self, parent_node) -> None:
        for inpt in parent_node.inputs:
            if inpt.is_linked:
                self._useful_nodes_list.append(inpt.links[0].from_node)
                self._set_useful_node(inpt.links[0].from_node)


    def _set_useful_nodes_list(self) -> None:
        try:
            node_output = self._material_canvas.nodes[self._output_node_name]
        except KeyError:
            self._valid_instance = False
            return
        
        self._set_useful_node(node_output)


    def _set_useless_nodes_list(self) -> None:
        for node in self._material_canvas.nodes:
            if node.name == self._output_node_name:
                continue

            if not node in self._useful_nodes_list:
                self._useless_nodes_list.append(node)


    def _sort_nodes(self) -> None:
        self._set_useful_nodes_list()
        self._set_useless_nodes_list()


    def _set_useful_nodes_border(self) -> None:
        for node in self._useful_nodes_list:
            self._useful_nodes_border[0] =\
                min(self._useful_nodes_border[0], node.location[0])
            self._useful_nodes_border[1] =\
                max(self._useful_nodes_border[1], node.location[1])
    
    
    def _get_linked_output(self, node):
        for output in node.outputs:
            if output.is_linked:
                return output
            
        return None
    

    def _get_first_node(self, node):
        output = self._get_linked_output(node)
        while output:
            node = output.links[0].to_node
            output = self._get_linked_output(node)
        
        return node
    
    
    def _shift_useless_node(self, inpt, location, shifted_nodes) -> None:
        node = inpt.links[0].from_node
        self._process_useless_node(
            node,
            [
                location[0] - OFFSET_INNER_X - node.width,
                location[1],
            ],
            shifted_nodes,
        )
        location[1] -= node.height + OFFSET_INNER_Y
        self._location_y_min = min(self._location_y_min, location[1])


    def _set_node_attribute(self, inpt, location) -> None:
        node =\
            self._material_canvas.nodes.new(type='ShaderNodeAttribute')
        self._nodes_attribute_list.append(node)
        
        node.location = (
            location[0] - OFFSET_INNER_X - node.width,
            location[1],
        )
        self._material_canvas.links.new(
            node.outputs['Alpha'],
            inpt,
        )
        location[1] -= node.height + OFFSET_INNER_Y
        self._location_y_min = min(self._location_y_min, location[1])


    def _process_useless_node(self, node, location, shifted_nodes) -> None:
            node.location = location
            shifted_nodes.append(node)

            for inpt in node.inputs:
                if inpt.is_linked:
                    self._shift_useless_node(inpt, location, shifted_nodes)
                    continue

                self._set_node_attribute(inpt, location)

    
    def _process_useless_nodes(self) -> None:
        shifted_nodes = []
        not_shifted_nodes = set(self._useless_nodes_list)
        
        while not_shifted_nodes:
            for node in not_shifted_nodes:
                node = self._get_first_node(node)
                self._process_useless_node(
                    node,
                    [
                        self._useful_nodes_border[0] - OFFSET_OUTER_X - node.width,
                        self._useful_nodes_border[1],
                    ],
                    shifted_nodes,
                )
                self._useful_nodes_border[1] = min(
                    self._useful_nodes_border[1] - node.height - OFFSET_INNER_Y,
                    self._location_y_min,
                )
                not_shifted_nodes -= set(shifted_nodes)
                break


    def _set_node_frame(self) -> None:
        if not self._useless_nodes_list:
            return

        node_frame =\
            self._material_canvas.nodes.new(type='NodeFrame')
        node_frame.label = USELESS_NODES

        for node in self._useless_nodes_list:
            node.parent = node_frame

        for node in self._nodes_attribute_list:
            node.parent = node_frame


    def process_nodes(self) -> None:
        self._remove_node_frame()
        self._sort_nodes()
        if not self._valid_instance or not self._useless_nodes_list:
            return
        
        self._set_useful_nodes_border()
        self._process_useless_nodes()
        self._set_node_frame()


    def log_instance_info(self) -> None:
        if not self._valid_instance:
            Logger.node_output_not_exist(self._type, self._name)
            return
        
        if not self._useless_nodes_list:
            Logger.useless_nodes_not_exist(self._type, self._name)
            return
        
        if self._type == 'material':
            Logger.useless_nodes_list(
                self._type,
                self._name,
                map(lambda node: node.name, self._useless_nodes_list),
                map(lambda node: node.type, self._useless_nodes_list),
            )
            return

        Logger.useless_nodes_list_with_usage(
            self._type,
            self._name,
            map(lambda node: node.name, self._useless_nodes_list),
            map(lambda node: node.type, self._useless_nodes_list),
            self._materials,
        )
