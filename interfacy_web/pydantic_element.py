import typing as T

from nicegui.element import Element
from objinspect import Parameter
from objinspect.constants import EMPTY
from objinspect.parameter import ParameterKind
from pydantic import BaseModel

from interfacy_web.class_element import ClassElement


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


class PydanticModelElement(ClassElement):
    def __init__(
        self,
        cls: T.Type,
        title: bool = True,
        description: bool = False,
        icon: str | None = None,
        icon_size: str = "32px",
        elements_per_row: list[int] | None = None,
        draggable: bool = False,
        extras: list[Element] | None = None,
        add_delete_button: bool = False,
        add_default_button: bool = False,
        expandable: bool = False,
        add_clear_button: bool = False,
        add_button_tooltips: bool = True,
        width_class: str = "w-fit-content",
    ) -> None:
        super().__init__(
            cls,
            title=title,
            description=description,
            icon=icon,
            icon_size=icon_size,
            elements_per_row=elements_per_row,
            draggable=draggable,
            extras=extras,
            add_delete_button=add_delete_button,
            add_default_button=add_default_button,
            add_clear_button=add_clear_button,
            expandable=expandable,
            add_button_tooltips=add_button_tooltips,
            width_class=width_class,
        )

    def get_description(self, description: str | None) -> str | None:
        if not description:
            return None
        if "Usage docs: https:///docs.pyndantic.dev" in description:
            return None
        return description

    def get_init_params(self) -> dict[str, Parameter]:
        return get_pydantic_init_params(self.cls)

    def build(self) -> None:
        self.build_title_row()

        for param in self.get_init_params().values():
            with self.get_current_row():
                self.add_input_element_for_param(param)


__all__ = ["PydanticModelElement"]
