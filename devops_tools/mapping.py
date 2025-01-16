import typing as t
from dataclasses import dataclass, is_dataclass

from queue import SimpleQueue, Queue

from dataclasses import dataclass

import inspect

import logging


T= t.TypeVar('T')


# https://stackoverflow.com/questions/56832881/check-if-a-field-is-typing-optional
def is_optional(field):
    return t.get_origin(field) is t.Union and \
           type(None) in t.get_args(field)

def is_generic(destination_type) -> True:
    return t.get_origin(destination_type)



@dataclass
class MapReference(t.Generic[T]):
    value: T
    
    def __repr__(self):
        return self.value

@dataclass
class MapNodeContext(t.Generic[T]):
    current_queue: SimpleQueue
    parent_node: 'MapNode'
    pass

@dataclass
class MapNode(t.Generic[T]):
    context: MapNodeContext[T]
    source: T
    destination_type: t.Type[T]
    value: t.Optional[MapReference] = None
    dict_key_source: t.Optional[str] = None


type_map: dict[t.Type, t.Callable] = {
    t.Dict: lambda: dict(),
    t.List: lambda: list()
    
}

def list_source_map(node: MapNode, 
                    sub_context: MapNodeContext) -> None:
    
    origin_type = t.get_origin(node.destination_type)
    
    if origin_type is not None and \
            issubclass(origin_type, list) :
                
        current_list_node: t.List = list()
                
        logging.debug("mapping source list to origin list type ...")

        for value in node.source:
            
            current_list_type, = t.get_args(node.destination_type)
            
            logging.debug(f"mapping attribute of type {current_list_type} (destination type hint) ...")
            logging.debug(f"instanciating {current_list_type} for deep reference...")

            sub_node = MapNode(
                source=value, destination_type=current_list_type,
                context=sub_context)
            
            node.value = current_list_node
            
            node.context.current_queue.put(sub_node)
            
        return
            
    if  inspect.isclass(node.destination_type) and \
            issubclass(node.destination_type, list):
    
        logging.debug("untyped list to list mapping for node ...")
        
        for value in node.source:
            
            class_name = type(value)
            logging.debug(f"mapping attribute of type {class_name} ...")
            logging.debug(f"instanciating {class_name} for deep reference...")
            # sub_context.reference = class_name()

            sub_node = MapNode(
                source=value, destination_type=class_name,
                context=sub_context)

            # sub_node.value = class_name()            
            node.context.current_queue.put(sub_node)


def tuple_source_map(node: MapNode, 
                    sub_context: MapNodeContext) -> None:
    
    origin_type = t.get_origin(node.destination_type)
    
    if origin_type is not None and \
            issubclass(origin_type, tuple) :
                
        current_list_node: t.Tuple = tuple()
                
        logging.debug("mapping source list to origin list type ...")

        arguments = t.get_args(node.destination_type)
        
        arguments_size = len(arguments)
        
        for current_argument_index in range(0, arguments_size):
            
            current_argument_value = node.source[current_argument_index]
            current_argument_type = arguments[current_argument_index]
            
            logging.debug(f"mapping attribute of type {current_argument_type} (destination type hint) ...")
            logging.debug(f"instanciating {current_argument_type} for deep reference...")

            sub_node = MapNode(
                source=current_argument_value, destination_type=current_argument_type,
                context=sub_context)
            
            sub_node.context.parent_node = node
            
            node.value = current_list_node
            node.context.current_queue.put(sub_node)
            
            
        return
            
    if  inspect.isclass(node.destination_type) and \
            issubclass(node.destination_type, list):
    
        logging.debug("untyped list to list mapping for node ...")
        
        for value in node.source:
            
            class_name = type(value)
            logging.debug(f"mapping attribute of type {class_name} ...")
            logging.debug(f"instanciating {class_name} for deep reference...")
            # sub_context.reference = class_name()

            sub_node = MapNode(
                source=value, destination_type=class_name,
                context=sub_context)

            # sub_node.value = class_name()            
            node.context.current_queue.put(sub_node)
       

def dict_source_map(node: MapNode, 
                    sub_context: MapNodeContext) -> None:
    
    origin_type = t.get_origin(node.destination_type)
    
    if origin_type is not None and \
        issubclass( origin_type, dict ):

        # create new dict reference
        node.value = dict()

        for key, value in node.source.items():

                        
            typing_args = t.get_args(node.destination_type)
            
            if len(typing_args) == 2 :
                key_type, value_type = t.get_args(node.destination_type)
            else:
                value_type = dict
                        
            logging.debug(f"mapping attribute of type {value_type} ...")
            
            sub_node = MapNode(
                source= value, destination_type=value_type,context=sub_context,
                dict_key_source= key)
            
            logging.debug(f"instanciating {value_type} for deep reference...")
            sub_node.value = value_type()
            
            logging.debug("creating dict entry")
            node.value[key] = sub_node.value
            
            node.context.current_queue.put(sub_node)
            
        return            

    if is_dataclass( node.destination_type ):
        
        node.value = node.destination_type()

        for field_name, field in node.destination_type.__dataclass_fields__.items():
            # assert(field_name in source)
            if not field_name in node.source:
                setattr(node.value, field_name, )
                continue

            
            sub_node = MapNode(
                source= node.source[field_name], destination_type=field.type,
                context=sub_context, dict_key_source= field_name)
            
            node.context.current_queue.put(sub_node)
            
def populate_parent(node: MapNode) -> None:
    if node.context.parent_node is None:
        return
    
    if is_dataclass( node.context.parent_node.value ):    
        if node.dict_key_source is not None:
            node.context.parent_node.value.__dict__[node.dict_key_source] = node.value
        return
            
    if issubclass( type(node.context.parent_node.value), dict):
        if node.dict_key_source is not None:
            node.context.parent_node.value[node.dict_key_source] = node.value
        return
            
    if issubclass( type(node.context.parent_node.value), list):
        node.context.parent_node.value.append( node.value )
        return
    
    if issubclass( type(node.context.parent_node.value), tuple):
        node.context.parent_node.value = node.context.parent_node.value + (node.value,)
        return
def walk_through(node: MapNode) -> None:
    
    sub_context = MapNodeContext(node.context.current_queue, node)
    
    
    while (True):
        if isinstance(node.source, list):
            list_source_map(node, sub_context)
            break

        if isinstance(node.source, dict) :      
            dict_source_map(node, sub_context)
            break
        
        if isinstance(node.source, tuple) :      
            tuple_source_map(node, sub_context)
            break

        # other types are not supported and affected as is
        node.value = node.source
        break

    populate_parent(node)


def map_node(node: MapNode) -> None:


    if is_optional(node.destination_type):
        node.context.current_queue.put(
            MapNode(node.context, node.source,
                t.get_args(node.destination_type)[0],node.value, node.dict_key_source))
        
        return

    walk_through(node)


def deep_map_from_raw(source: dict|list|tuple, destination_type: t.Type[T]) -> T:
    node_queue = SimpleQueue[MapNode]()
    
    root_node = MapNode(
        source=source, destination_type= destination_type, 
        context= MapNodeContext(current_queue=node_queue, parent_node= None))
    
    node_queue.put(root_node)
    
    while not node_queue.empty():
        
        current_node = node_queue.get()
        map_node(current_node)
    
    return root_node.value