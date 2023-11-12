import datetime
import os
import typing as T
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Dict, Optional

from nicegui import ui
from nicegui.element import Element
from objinspect.util import get_enum_choices, get_literal_choices, is_enum, is_literal
from stdl import dt, fs

from interfacy_web.file_picker import LocalFileDialog
from interfacy_web.icons import ICONS
from interfacy_web.util import clean_variable_name, is_valid_date

ui.colors(info="black")

# For multi-line notifications
ui.html("<style>.multi-line-notification { white-space: pre-line; }</style>")

Position = T.Literal[
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "top",
    "bottom",
    "left",
    "right",
    "center",
]

NotificationType = T.Literal["positive", "negative", "warning", "info", "ongoing"]


class Textarea(ui.textarea):
    def __init__(
        self,
        label: Optional[str] = None,
        *,
        placeholder: Optional[str] = None,
        value: str = "",
        rows: int | None = None,
        cols: int | None = None,
        autogrow: bool = False,
        clearable: bool = False,
        filled: bool = False,
        on_change: Optional[Callable[..., Any]] = None,
        validation: Dict[str, Callable[..., bool]] = {},
    ) -> None:
        super().__init__(
            label,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            validation=validation,
        )
        if autogrow:
            self.props(add="autogrow")
        if clearable:
            self.props(add="clearable")
        if filled:
            self.props(add="filled")
        if rows is not None:
            self.props(f"rows={rows}")
        if cols is not None:
            self.props(f"cols={cols}")


class TextareaDialog(Element):
    def __init__(
        self,
        title: str | None = None,
        rows: int = 30,
        cols: int | None = None,
        placeholder: str | None = None,
        autogrow: bool = True,
    ) -> None:
        self.data: str | None = None
        self.rows = rows
        self.cols = cols
        self.title = title
        self.placeholder = placeholder
        self.autogrow = autogrow
        super().__init__()

    async def open(self):
        file_dialog = LocalFileDialog()
        with ui.dialog().classes("w-screen") as dialog, ui.card().classes("w-screen"):
            if self.title:
                with ui.row().classes("items-center"):
                    markdown_heading(self.title, level=3)

            textarea = Textarea(
                rows=self.rows,
                cols=self.cols,
                placeholder=self.placeholder,
                clearable=True,
                autogrow=self.autogrow,
            ).classes("w-full")

            def submit():
                dialog.submit(textarea.value)
                self.data = textarea.value

            def import_file():
                path = file_dialog.open()
                if not path:
                    notification("No file selected", type="warning")
                    return
                if os.path.isfile(path):
                    textarea.value = fs.File(path).read()
                else:
                    notification(f"Invalid file '{path}'", type="warning")

            with ui.row().classes("items-start"):
                ui.button("Done", icon="done", on_click=submit)
                ui.button("From file", icon=ICONS.UPLOAD_FILE, on_click=import_file)
                ui.button(icon=ICONS.CLOSE, on_click=dialog.close)

        selected = await dialog
        self.data = selected


class DatePicker(Element):
    def __init__(
        self,
        label: str = "Date",
        value: datetime.date | str | None = None,
        placeholder: str | None = "YYYY//MM//DD",
        tag: str | None = None,
    ):
        super().__init__(tag=tag)
        if isinstance(value, datetime.date):
            value = value.strftime("%Y-%m-%d")

        validation = {"Invalid date!": is_valid_date}
        with ui.input(
            label, value=value or "", validation=validation, placeholder=placeholder
        ) as self.text_input:
            with self.text_input.add_slot("append"):
                ui.icon("edit_calendar").on("click", lambda: self.menu.open()).classes(
                    "cursor-pointer"
                )
            with ui.menu() as self.menu:
                self.date_picker = ui.date(value=value).bind_value(self.text_input)

    @property
    def value(self) -> datetime.date | None:
        if not self.text_input.value:
            return None
        return dt.parse_datetime_str(self.text_input.value).date()

    @value.setter
    def value(self, value: datetime.date | None):
        if value is None:
            self.text_input.value = ""
            return
        self.text_input.value = value.strftime("%Y-%m-%d")

    def tooltip(self, text: str):
        with self.text_input:
            tooltip(text)
        return self


@dataclass()
class SelectOption:
    name: str
    value: str
    tooltip: str | None = None


async def select_popup(
    options: list[SelectOption],
    title: str | None = None,
    one_per_row: bool = False,
    width_class="w-screen",
):
    if not options:
        raise ValueError("Selection data must not be empty")

    with ui.dialog().classes("items-center").classes(width_class) as dialog, ui.card().classes(
        "items-center"
    ).classes(width_class):
        if title:
            markdown_heading(title, level=4)

        def submit(value):
            dialog.submit(value)

        def make_button():
            button = ui.button(opt.name, on_click=partial(submit, value=opt.value))
            if opt.tooltip:
                with button:
                    tooltip(opt.tooltip)

        with ui.row().classes("items-center"):
            for opt in options:
                if one_per_row:
                    with ui.column().classes("items-center"):
                        make_button()
                else:
                    make_button()

    selected = await dialog
    return selected


def markdown_heading(
    value: str,
    level: int = 1,
    center: bool = False,
    *,
    background: str | None = None,
    margin: int = 0,
    border_radius: int = 0,
    unit: str = "px",
    tooltip_text: str | None = None,
):
    """
    Create a markdown title.

    Args:
        value (str): The title text.
        size (int, optional): The title size. Defaults to 1. Must be between 1 and 6. See https://www.markdownguide.org/basic-syntax/#headings.
        center (bool, optional): Whether to center the title. Defaults to False.
        background (str, optional): The background color. Defaults to None.
        margin (int, optional): The margin. Defaults to 0.
        border_radius (int, optional): The border radius. Defaults to 0.
        unit (str, optional): The unit for margin and border_radius. Defaults to "px".
        tooltip_text (str, optional): The tooltip text. Defaults to None.


    """
    if level not in range(1, 7):
        raise ValueError("Size must be between 1 and 6")

    level = "#" * level  # type: ignore
    mdtitle = ui.markdown(f"{level} {value}")

    if center:
        mdtitle = mdtitle.classes("text-center")
    if background:
        mdtitle = mdtitle.style(f"background-color: {background};")

    mdtitle = mdtitle.style(f"margin: {margin}{unit};").style(
        f"border-radius: {border_radius}{unit};"
    )
    if tooltip_text:
        tooltip(tooltip_text)

    return mdtitle


def list_popup(
    items: list[T.Any],
    item_display_fn: T.Callable | None = None,
    title: str | None = None,
    width_class="w-screen",
):
    if not item_display_fn:
        item_display_fn = lambda item: ui.markdown(f"- {item}")

    with ui.dialog().classes(width_class) as dialog, ui.card().classes(width_class):
        if title:
            markdown_heading(title, level=4)
        for item in items:
            with ui.row().classes("items-center"):
                item_display_fn(item)

    return dialog


def select_from_type_hint(
    hint,
    *,
    label: str | None = None,
    value: T.Any = None,
    on_change: T.Callable | None = None,
    with_input: bool = False,
    multiple: bool = False,
    clearable: bool = False,
    width_class="w-40",
):
    if is_enum(hint):
        choices = get_enum_choices(hint)
    elif is_literal(hint):
        choices = get_literal_choices(hint)
    else:
        raise ValueError(f"Type {type(hint)} not supported. Must be Enum or Literal")

    options = {i: clean_variable_name(i) for i in choices}

    if value:
        if value not in options.keys():
            raise ValueError(f"Value '{value}' not in options")

    return ui.select(
        options,
        label=label,
        value=value,
        on_change=on_change,
        with_input=with_input,
        multiple=multiple,
        clearable=clearable,
    ).classes(width_class)


def notification(
    text: str,
    type: NotificationType | None = "info",
    position: Position = "bottom-left",
    *,
    multi_line: bool = False,
    close_button: str | T.Literal[False] = "✖",
    progress: bool = True,
    **kwargs,
):
    extra = {}
    if multi_line:
        extra["classes"] = "multi-line-notification"
    ui.notify(
        message=text,
        type=type,
        position=position,
        close_button=close_button,  # type: ignore
        progress=progress,
        **extra,
        **kwargs,
    )


def tooltip(message: str, large: bool = True, dark_mode: bool = True, mono_font: bool = True):
    element = ui.tooltip(message)
    if dark_mode:
        element.classes("bg-grey-2").classes("text-black")
    else:
        element.classes("bg-grey-10").classes("text-white")
    if mono_font:
        element.classes("font-mono")
    if large:
        element.classes("text-body2")
    return element
