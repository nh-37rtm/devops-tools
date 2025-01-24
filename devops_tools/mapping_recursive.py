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
class MapNode(t.Generic[T]):
    source: T
    destination_type: t.Type[T]


def map_list_as_list(node: MapNode) -> None:

    logging.debug("mapping source list to origin list type ...")

    wrapped_node = list()

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
        )

        sub_wrapped_node = wrap_node(sub_node)
        wrapped_node.append(sub_wrapped_node)

    return wrapped_node


def map_list_as_tuple(node: MapNode) -> None:

    logging.debug("mapping source list to origin list type ...")

    wrapped_node = tuple()

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
        )

        sub_wrapped_node = wrap_node(sub_node)

        wrapped_node = wrapped_node + (
            sub_wrapped_node,
        )

    return wrapped_node


def map_dict_to_dict(node: MapNode) -> None:

    wrapped_node = dict()

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
        )

        wrapped_node[key] = wrap_node(sub_node)

        logging.debug(
            f"instanciating {value_type} for deep reference..."
        )

    return wrapped_node


def map_dict_to_dataclass(node: MapNode) -> None:

    wrapped_node = node.destination_type()

    for (
        field_name,
        field,
    ) in node.destination_type.__dataclass_fields__.items():
        # assert(field_name in source)
        if not field_name in node.source:
            setattr(wrapped_node, field_name, None)
            continue

        sub_node = MapNode(
            source=node.source[field_name],
            destination_type=field.type,
        )
        
        sub_wrapped_node = wrap_node(sub_node)
        setattr(wrapped_node, field_name, sub_wrapped_node)

    return wrapped_node


def list_mapping_dispatcher(node: MapNode) -> None:

    destination_type_origin = t.get_origin(node.destination_type)

    wrapped_node = None

    match destination_type_origin:
        case _ if destination_type_origin is not None and issubclass(
            destination_type_origin, list
        ):
            wrapped_node = map_list_as_list(node)

        case _ if destination_type_origin is not None and issubclass(
            destination_type_origin, tuple
        ):
            wrapped_node = map_list_as_tuple(node)

        case _ if inspect.isclass(
            node.destination_type
        ) and issubclass(node.destination_type, list):
            # untyped is not wrapped
            wrapped_node = node.source

    return wrapped_node


def dict_mapping_dispatcher(node: MapNode) -> None:

    destination_type_origin = t.get_origin(node.destination_type)
    wrapped_node = None

    match destination_type_origin:
        case _ if destination_type_origin is not None and issubclass(
            destination_type_origin, dict
        ):

            wrapped_node = map_dict_to_dict(node)

        case _ if is_dataclass(node.destination_type):
            wrapped_node = map_dict_to_dataclass(node)

    return wrapped_node

def walk_through(node: MapNode) -> None:

    wrapped_node = None

    match node.source:
        case _ if isinstance(node.source, list):
            wrapped_node = list_mapping_dispatcher(node)

        case _ if isinstance(node.source, dict):
            wrapped_node = dict_mapping_dispatcher(node)

        case _ if isinstance(node.source, tuple):
            wrapped_node = list_mapping_dispatcher(node)
        case _:
            wrapped_node = node.source

    return wrapped_node


def wrap_node(node: MapNode) -> None:

    sub_node = None
    wrapped_node = None

    if is_optional(node.destination_type):
        
        destination_type=t.get_args(node.destination_type)[0]
        sub_node = MapNode(
            source= node.source,
            destination_type= destination_type
        )
        wrapped_node = wrap_node(sub_node)
    else:
        destination_type = node.destination_type
        
        node = MapNode(
            source=node.source,
            destination_type=destination_type
        )

        wrapped_node = walk_through(node)
        
    return wrapped_node


def type_wrap(
    source: dict | list | tuple, destination_type: t.Type[T]
) -> T:

    node = MapNode(source=source, destination_type=destination_type)
    return wrap_node(node)
