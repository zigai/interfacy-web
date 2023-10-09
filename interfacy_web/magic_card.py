import re

from nicegui import ui
from nicegui.element import Element
from objinspect import Parameter

from interfacy_web.draggable_card import DraggableCard
from interfacy_web.elements import markdown_title, tooltip
from interfacy_web.parser import DEFAULT_VALUES


class MagicCard(DraggableCard):
    width_class = "w-fit-content"

    def __init__(
        self,
        elements_per_row: list[int],
        title: str | None = None,
        description: str | None = None,
        icon: str | None = None,
        icon_size: str = "32px",
        draggable: bool = False,
        expandable: bool = False,
        add_delete_button: bool = True,
        add_default_button: bool = True,
        add_clear_button: bool = True,
        add_button_tooltips: bool = True,
    ) -> None:
        self._title_text = title
        self._icon_name = icon
        self._icon_size = icon_size
        self._description_text = description
        self._expandable = expandable
        self._row_index = 0
        self._add_delete_button = add_delete_button
        self._add_default_button = add_default_button
        self._add_clear_button = add_clear_button
        self._elements_per_row: list[int] = elements_per_row
        self._add_button_tooltips = add_button_tooltips
        self.rows: list[ui.row] = []
        self.init_fields: dict[str, Element] = {}

        super().__init__(drag_enabled=draggable)
        self.build_extras()
        self.build_extra_buttons()

    def new_row(self) -> ui.row:
        if self._expandable:
            with self.top_row:
                return ui.row().classes("items-center")
        return ui.row().classes("items-center")

    def add_extra_element(self, element: Element) -> None:
        with self:
            element.move(self.get_current_row())

    def get_current_row(self) -> ui.row:
        try:
            space_left = self._elements_per_row[self._row_index]
        except IndexError:
            self._elements_per_row.append(1)
            space_left = 1

        if space_left == 0:
            self._row_index += 1
            try:
                space_left = self._elements_per_row[self._row_index]
            except IndexError:
                self._elements_per_row.append(1)
                space_left = 1

        self._elements_per_row[self._row_index] -= 1
        if len(self.rows) <= self._row_index:
            self.rows.append(self.new_row())
        return self.rows[self._row_index]

    def format_label(self, label: str) -> str:
        return label.replace("_", " ").capitalize()

    def format_title(self, title: str) -> str:
        matches = re.finditer(".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", title)
        words = [m.group(0).capitalize() for m in matches]
        return " ".join(words)

    def build_title_row(self) -> None:
        if not self._icon_name or not self._title_text:
            return

        if self._expandable:
            with ui.expansion(self._title_text, icon=self._icon_name).classes(
                "w-60"
            ) as self.top_row:
                if self._description_text:
                    ui.tooltip(self._description_text)
            return

        with self.new_row() as self.top_row:
            if self._icon_name:
                self.icon = ui.icon(self._icon_name, size=self._icon_size)
            if self._title_text:
                self.title = markdown_title(self._title_text, size=4)
                if self._description_text:
                    with self.title:
                        ui.tooltip(self._description_text)

    def build_extra_buttons(self):
        with self:
            with ui.row():
                if self._add_delete_button:
                    self.button_delete = ui.button(icon="delete", on_click=self.del_from_col)
                    if self._add_button_tooltips:
                        with self.button_delete:
                            tooltip("Delete")
                if self._add_default_button:
                    self.button_to_defaults = ui.button(
                        icon="refresh", on_click=self.reset_to_defaults
                    )
                    if self._add_button_tooltips:
                        with self.button_to_defaults:
                            tooltip("Reset to defaults")
                if self._add_clear_button:
                    self.button_clear = ui.button(icon="backspace", on_click=self.clear_fields)
                    if self._add_button_tooltips:
                        with self.button_clear:
                            tooltip("Clear fields")

    def build_extras(self, extras: list[Element] | None = None):
        if not extras:
            return
        with self.get_current_row():
            for element in extras:
                element.move(self.get_current_row())

    def clear_fields(self):
        for k, v in self.init_fields.items():
            default_val = DEFAULT_VALUES.get(type(v), None)  # type: ignore
            if default_val is not None:
                v.value = default_val  # type: ignore

    def reset_to_defaults(self):
        init_params = self.get_init_params()
        if not init_params:
            return

        for element_field_name, element in self.init_fields.items():
            param = init_params[element_field_name]
            if not param.is_required:
                element.value = param.default  # type:ignore
            else:
                default_val = DEFAULT_VALUES.get(type(element), None)  # type:ignore
                if default_val is not None:
                    element.value = default_val  # type:ignore

    def build(self):
        raise NotImplementedError

    def get_init_params(self) -> dict[str, Parameter]:
        raise NotImplementedError


__all__ = ["MagicCard"]
