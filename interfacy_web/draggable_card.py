from __future__ import annotations

import random

from nicegui import ui

_dragged: DraggableCard | None = None


class Column(ui.column):
    def get_draggable_children(self) -> list[DraggableCard]:
        children = []
        for i in self.default_slot.children:
            if issubclass(i.__class__, DraggableCard):
                if i.drag_enabled:  # type:ignore
                    children.append(i)
        return children

    def shuffle(self) -> None:
        children = self.get_draggable_children()
        random.shuffle(children)
        for i in children:
            i.move(target_index=0)


class Row(ui.row):
    def get_draggable_children(self) -> list[DraggableCard]:
        children = []
        for i in self.default_slot.children:
            if issubclass(i.__class__, DraggableCard):
                if i.drag_enabled:  # type:ignore
                    children.append(i)
        return children

    def shuffle(self) -> None:
        children = self.get_draggable_children()
        random.shuffle(children)
        for i in children:
            i.move(target_index=0)


class DraggableCard(ui.card):
    highlight_border = "border-2 border-blue-300"
    dragged_background = "bg-transparent"

    def __init__(self, drag_enabled: bool = True, width_class="w-fit-content") -> None:
        super().__init__()
        self.drag_enabled = drag_enabled
        self.width_class = width_class

        with self.props("draggable").classes(f"cursor-pointer").classes(self.width_class).style(
            "box-shadow: none;"
        ):
            self.build()

        self.on("dragstart", self.on_dragstart)
        self.on("dragenter", self.on_dragenter)
        self.on("dragleave", self.on_dragleave)
        self.on("dragover.prevent", self.on_dragover_prevent)
        self.on("drop", self.on_drop)

        if not self.drag_enabled:
            self.disable_drag()

    def disable_drag(self) -> None:
        self.drag_enabled = False
        self.classes(remove="cursor-pointer")
        self.props(remove="draggable")

    def enable_drag(self) -> None:
        self.drag_enabled = True
        self.classes(add="cursor-pointer")
        self.props(add="draggable")

    def get_parent(self) -> Column | None:
        return self.parent_slot.parent  # type:ignore

    def del_from_col(self) -> None:
        parent = self.get_parent()
        if parent is not None:
            parent.remove(self)

    def build(self) -> None:
        """Override this method to build the draggable card"""

    def on_dragstart(self) -> None:
        if not self.drag_enabled:
            return

        self.classes(add=self.dragged_background)

        global _dragged
        _dragged = self

    def on_dragenter(self) -> None:
        if not self.drag_enabled:
            return

        self.classes(add=self.highlight_border)

    def on_dragleave(self) -> None:
        if not self.drag_enabled:
            return

        self.classes(remove=self.highlight_border)

    def on_drop(self) -> None:
        if not self.drag_enabled:
            return

        global _dragged
        if not _dragged:
            return

        parent = self.get_parent()
        if parent is None:
            return

        children = parent.get_draggable_children()
        try:
            self_index = children.index(self)
        except ValueError:
            return

        _dragged.move(target_index=self_index)
        self.on_dragleave()
        _dragged.classes(remove=self.dragged_background)

    def on_dragover_prevent(self):
        """Prevent default dragover event to allow drop event"""
        return


__all__ = ["DraggableCard", "Column"]
