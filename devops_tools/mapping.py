import typing as t
from dataclasses import dataclass, is_dataclass

from queue import SimpleQueue, Queue

from dataclasses import dataclass, field

import inspect
import logging

T = t.TypeVar("T")


# https://stackoverflow.com/questions/56832881/check-if-a-field-is-typing-optional
def is_optional(field):
    return t.get_origin(field) is t.Union and type(
        None
    ) in t.get_args(field)


def is_generic(destination_type) -> True:
    return t.get_origin(destination_type)


@dataclass
class ImmutableMapReference(t.Generic[T]):
    value: T = field(default= None)
    def __repr__(self):
        return self.value


@dataclass
class MapNodeContext(t.Generic[T]):
    current_queue: SimpleQueue
    parent_node: "MapNode"
    pass


@dataclass
class MapNode(t.Generic[T]):
    context: MapNodeContext[T]
    source: T
    destination_type: t.Type[T]
    reference: ImmutableMapReference|t.Any = None
    dict_key_source: t.Optional[str] = None
    set_reference: t.Callable = field(default=None)


mk_instance_type_map: dict[t.Type, t.Callable] = {
    t.Dict: lambda: dict(),
    t.List: lambda: list(),
    t.Tuple: lambda: tuple(),
}


def mk_reference(type: t.Type) -> t.Any:
    
    return_value = None
    type_origin = t.get_origin(type)

    match type_origin:
        case _ if type_origin is not None : 
            match type_origin:
                case _ if issubclass(type_origin, tuple):
                    return_value = ImmutableMapReference(tuple())
                case _ if issubclass(type_origin, dict):
                    return_value = dict()
                case _ if issubclass(type_origin, list):
                    return_value = list()
        case _ if is_dataclass(type):
            return_value = type()
        case _:
            return_value = ImmutableMapReference(type())
    return return_value


def map_list_as_list(
    node: MapNode, sub_context: MapNodeContext
) -> None:

    logging.debug("mapping source list to origin list type ...")

    for value in node.source:

        (current_list_type,) = t.get_args(node.destination_type)

        logging.debug(
            f"mapping attribute of type {current_list_type} (destination type hint) ..."
        )
        logging.debug(
            f"instanciating {current_list_type} for deep reference..."
        )

        sub_node = MapNode(
            source=value,
            destination_type=current_list_type,
            context=sub_context,
            reference= mk_reference(current_list_type)
        )        
        
        node.reference.append(sub_node.reference)
        node.context.current_queue.put(sub_node)


def map_list_as_tuple(
    node: MapNode, sub_context: MapNodeContext
) -> None:

    logging.debug("mapping source list to origin list type ...")

    arguments = t.get_args(node.destination_type)
    arguments_size = len(arguments)
    
    for current_argument_index in range(0, arguments_size):

        current_argument_value = node.source[current_argument_index]
        current_argument_type = arguments[current_argument_index]

        logging.debug(
            f"mapping attribute of type {current_argument_type} (destination type hint) ..."
        )
        logging.debug(
            f"instanciating {current_argument_type} for deep reference..."
        )

        # tuple_reference = ImmutableMapReference(mk_reference(current_argument_type))
        
        sub_node = MapNode(
            source=current_argument_value,
            destination_type=current_argument_type,
            context=sub_context,
            reference= mk_reference(current_argument_type)
        )
            
        node.reference.value = node.reference.value + (sub_node.reference,)
        
        # because of tuple immutability we use ImmutableMapReference
        # node.reference = tuple_reference
        node.context.current_queue.put(sub_node)
        


def map_untyped_list_to_list(
    node: MapNode, sub_context: MapNodeContext
) -> None:

    logging.debug("untyped list to list mapping for node ...")

    for value in node.source:

        value_type = None

        typing_args = t.get_args(node.destination_type)
        if len(typing_args) == 1:
            value_type, = t.get_args(node.destination_type)
        else:
            value_type = dict

        class_name = type(value)
        logging.debug(f"mapping attribute of type {class_name} ...")
        logging.debug(
            f"instanciating {class_name} for deep reference..."
        )

        sub_node = MapNode(
            source=value,
            destination_type=class_name,
            context=sub_context,
            reference= mk_reference(value_type)
        )
        
        node.reference.append(sub_node.reference)
        node.context.current_queue.put(sub_node)


def map_dict_to_dict(
    node: MapNode, sub_context: MapNodeContext
) -> None:

    for key, value in node.source.items():
        
        value_type = None

        typing_args = t.get_args(node.destination_type)
        if len(typing_args) == 2:
            key_type, value_type = t.get_args(node.destination_type)
        else:
            value_type = dict

        logging.debug(f"mapping attribute of type {value_type} ...")

        sub_node = MapNode(
            source=value,
            destination_type=value_type,
            context=sub_context,
            dict_key_source=key,
            reference= mk_reference(value_type)
        )
        
        node.reference[key] = sub_node.reference

        logging.debug(
            f"instanciating {value_type} for deep reference..."
        )

        node.context.current_queue.put(sub_node)

def map_dict_to_dataclass(
    node: MapNode, sub_context: MapNodeContext
) -> None:

    for (
        field_name,
        field,
    ) in node.destination_type.__dataclass_fields__.items():
        # assert(field_name in source)
        if not field_name in node.source:
            setattr(node.reference, field_name, None)
            continue

        sub_node = MapNode(
            source=node.source[field_name],
            destination_type=field.type,
            context=sub_context,
            dict_key_source=field_name,
            reference=mk_reference(field.type)
        )

        setattr(node.reference, field_name, sub_node.reference)
        node.context.current_queue.put(sub_node)


def list_mapping_dispatcher(
    node: MapNode, sub_context: MapNodeContext
) -> None:

    destination_type_origin = t.get_origin(node.destination_type)

    match destination_type_origin:
        case _ if destination_type_origin is not None and issubclass(
            destination_type_origin, list
        ):

            map_list_as_list(node, sub_context)

        case _ if destination_type_origin is not None and issubclass(
            destination_type_origin, tuple
        ):
            #assert isinstance( node.reference, ImmutableMapReference )            
            map_list_as_tuple(node, sub_context)

        case _ if inspect.isclass(
            node.destination_type
        ) and issubclass(node.destination_type, list):

            map_untyped_list_to_list(node, sub_context)


def dict_mapping_dispatcher(
    node: MapNode, sub_context: MapNodeContext
) -> None:

    destination_type_origin = t.get_origin(node.destination_type)

    match destination_type_origin:
        case _ if destination_type_origin is not None and issubclass(
            destination_type_origin, dict
        ):

            map_dict_to_dict(node, sub_context)

        case _ if is_dataclass(
            node.destination_type
        ):
            map_dict_to_dataclass(node, sub_context)

def walk_through(node: MapNode) -> None:

    sub_context = MapNodeContext(node.context.current_queue, node)

    match node.source:
        case _ if isinstance(node.source, list):
            list_mapping_dispatcher(node, sub_context)

        case _ if isinstance(node.source, dict):
            dict_mapping_dispatcher(node, sub_context)
            
        case _ if isinstance(node.source, tuple):
            list_mapping_dispatcher(node, sub_context)
            
        case _ if isinstance( node.reference, ImmutableMapReference ):
                logging.info(f"setting immutable reference value to {node.source}")
                node.reference.value = node.source
        case _:
            # other types are not supported and affected as is
            logging.info(f"setting raw value to {node.source}")
            node.reference = node.source

    # populate_parent(node)


def map_node(node: MapNode) -> None:

    if is_optional(node.destination_type):
        node.context.current_queue.put(
            MapNode(
                node.context,
                node.source,
                t.get_args(node.destination_type)[0],
                node.reference,
                node.dict_key_source,
            )
        )

        return

    walk_through(node)


def deep_map_from_raw(
    source: dict | list | tuple, destination_type: t.Type[T]
) -> T:
    node_queue = SimpleQueue[MapNode]()

    root_node = MapNode(
        source=source,
        destination_type=destination_type,
        context=MapNodeContext(
            current_queue=node_queue, parent_node=None
        ),
        reference= mk_reference(destination_type)
    )

    node_queue.put(root_node)

    while not node_queue.empty():

        current_node = node_queue.get()
        map_node(current_node)

    return root_node.reference
