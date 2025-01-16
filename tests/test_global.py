from pytest import fixture
import devops_tools.mapping as m
import logging

import typing as t

from dataclasses import dataclass

from pydantic_partial import create_partial_model

import pydantic


@dataclass
class ClassB:

    def __init__(self):
        pass

    b_a: str
    b_b: str


@dataclass
class ClassC:

    def __init__(self):
        pass

    c_a: str
    c_b: str


@dataclass
class ClassA:

    def __init__(self):
        pass

    a: str
    o_a: t.Optional[str]

    b: str
    o_b: t.Optional[str]

    ab: t.List[ClassB]
    o_ab: t.Optional[t.List[ClassB]]

    ac: ClassC
    o_ac: t.Optional[ClassC]

    t: t.Tuple[str, str, str]


@fixture(name="logger")
def fix0() -> logging.Logger:
    return logging.getLogger()


@fixture(name="source_data")
def fix01() -> dict:
    return {
        "a": "a value",
        "o_a": "a value",
        "b": "b value",
        "o_b": "b value",
        "c": "c value",
        "o_c": "c value",
        "ab": [
            {"b_a": "a string 0", "b_b": "another string 0"},
            {"b_a": "a string 1", "b_b": "another string 1"},
        ],
        "o_ab": [
            {"b_a": "a string 0", "b_b": "another string 0"},
            {"b_a": "a string 1", "b_b": "another string 1"},
        ],
        "ac": {"c_a": "a c string", "c_b": "another c string"},
        "o_ac": {"c_a": "a c string", "c_b": "another c string"},
        "t": ["1", "2", "3"],
    }


@fixture(name="source_data2")
def fix03() -> t.Tuple:
    return (
        "toto",
        None,
        {
            "ab": [
                {"b_a": "a string 0", "b_b": "another string 0"},
                {"b_a": "a string 1", "b_b": "another string 1"},
            ],
            "o_ab": [
                {"b_a": "a string 0", "b_b": "another string 0"},
                {"b_a": "a string 1", "b_b": "another string 1"},
            ],
            "ac": {"c_a": "a c string", "c_b": "another c string"},
            "o_ac": {"c_a": "a c string", "c_b": "another c string"},
            "t": ["1", "2", "3"],
        },
    )


@fixture(name="source_data_list")
def fix02(source_data: dict) -> t.List:
    return [source_data, source_data, source_data]


def test_basic(logger: logging.Logger):
    logger.info("starting tests ...")


def test_map(logger: logging.Logger, source_data: dict):
    logger.info("starting tests ...")

    logger.info(source_data)

    m.deep_map_from_raw(source_data, ClassA)


def test_map_dict(logger: logging.Logger, source_data: dict):

    logger.info("starting tests ...")
    result = m.deep_map_from_raw({"a": "a_value"}, t.Dict)

    pass


def test_map_list(logger: logging.Logger, source_data_list: dict):
    logger.info("starting tests ...")

    logger.info(source_data_list)

    result = m.deep_map_from_raw(source_data_list, t.List[ClassA])
    logging.info(result)

    pass


# def test_pydantic_partial(logger: logging.Logger, source_data2: dict):

#     logger.info("starting test ...")

#     partial = create_partial_model(t.List[ClassA])
#     test = partial.model_validate(source_data_list)

def test_map_tuple(logger: logging.Logger, source_data2: dict):
    logger.info("starting tests ...")

    pass
    logger.info(source_data2)

    result = m.deep_map_from_raw(source_data2, t.Tuple[str, str, ClassA])
    pass
    logging.info(result)

    pass
