import typing as T
from functools import lru_cache

from nicegui.element import Element
from objinspect import Class, Parameter
from objinspect.constants import EMPTY
from objinspect.parameter import ParameterKind
from objinspect.util import type_to_str
from pydantic import BaseModel
from stdl import dt, st


def is_valid_date(string: str) -> bool:
    try:
        dt.parse_datetime_str(string)
        return True
    except ValueError:
        return False


def err_message_missing_param(param: Parameter) -> str:
    return f"Missing required argument '{param.name}' with type '{type_to_str(param.type)}'"


def clean_var_name(name: str) -> str:
    return st.snake_case(name).replace("_", " ").title()


def get_pydantic_init_params(model: T.Type[BaseModel]) -> dict[str, Parameter]:
    """
    Args:
        model: Type of the Pydantic model.

    Returns:
        A dictionary where keys are field names and values are tuples
        containing (type hint, default value).
    """

    params = {}
    for name in model.model_fields:
        param = Parameter(
            name=name,
            kind=ParameterKind.POSITIONAL_OR_KEYWORD,
            type=model.__annotations__[name],
            default=model.model_fields[name].default
            if not model.model_fields[name].is_required()
            else EMPTY,
            description=None,
            infer_type=False,
        )
        params[name] = param
    return params


def is_type(val: T.Any, t: T.Type) -> bool:
    if T.get_origin(t) is None:
        return type(val) is t
    else:
        origin = T.get_origin(t)
        args = T.get_args(t)
        return isinstance(val, origin) and all(isinstance(arg, type) for arg in args)


@lru_cache()
def element_takes_label(e: Element) -> bool:
    obj = Class(e)
    init_method = obj.init_method
    if not init_method:
        return False
    for i in init_method.params:
        if i.name == "label":
            return True
    return False
