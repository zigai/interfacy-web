import datetime
import typing as T
from functools import lru_cache

from nicegui import ui
from nicegui.element import Element
from strto import get_parser

from interfacy_web.elements import DatePicker

INPUT_ELEMENTS = {
    int: ui.number,
    str: ui.input,
    float: ui.number,
    bool: ui.checkbox,
    list: ui.textarea,
    tuple: ui.textarea,
    datetime.date: DatePicker,
}

DEFAULT_VALUES = {
    ui.number: 0,
    ui.input: "",
    ui.checkbox: False,
    ui.textarea: "",
    DatePicker: None,
}


STR_PARSER = get_parser()


@lru_cache()
def element_for_type(t: T.Type) -> Element:
    if t in INPUT_ELEMENTS:
        return INPUT_ELEMENTS[t]
    if args := T.get_args(t):
        for i in args:
            if i in INPUT_ELEMENTS:
                return INPUT_ELEMENTS[i]
    raise ValueError(f"No input element for type {t}")
