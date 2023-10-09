import os
import tkinter as tk
from tkinter import filedialog

from nicegui import ui
from stdl import fs

from interfacy_web.icons import ICONS
from interfacy_web.logger import logger

_TKINTER_ROOT = tk.Tk()  # For file dialogs
_TKINTER_ROOT.withdraw()


class FileType:
    """A collection of common file type filters for file dialog."""

    ALL_FILES = ("All files", "*.*")
    TEXT_FILES = ("Text files", "*.txt")
    PYTHON_FILES = ("Python files", "*.py")
    IMAGE_FILES = ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff")
    PDF_FILES = ("PDF files", "*.pdf")
    WORD_DOCUMENTS = ("Word documents", "*.doc;*.docx")
    EXCEL_SPREADSHEETS = ("Excel spreadsheets", "*.xls;*.xlsx")
    POWERPOINT_PRESENTATIONS = ("PowerPoint presentations", "*.ppt;*.pptx")
    AUDIO_FILES = ("Audio files", "*.mp3;*.wav;*.flac;*.ogg;*.m4a")
    VIDEO_FILES = ("Video files", "*.mp4;*.mkv;*.avi;*.mov;*.wmv")
    ARCHIVE_FILES = ("Archive files", "*.zip;*.rar;*.tar;*.gz;*.bz2")
    DATA_FILES = ("Data files", "*.csv;*.json;*.xml;*.yaml;*.yml")

    @staticmethod
    def get_types(*types: str) -> list[tuple[str, str]]:
        """Get a list of file type filters by name.

        Args:
            *types (str): The names of the file type filters to get.

        Returns:
            list[tuple[str, str]]: A list of file type filters.

        Examples:
            >>> FILE_TYPE.get_types("all", "text", "python")
            [("All files", "*.*"), ("Text files", "*.txt"), ("Python files", "*.py")]
        """
        type_dict = {
            "all": FileType.ALL_FILES,
            "text": FileType.TEXT_FILES,
            "python": FileType.PYTHON_FILES,
            "image": FileType.IMAGE_FILES,
            "pdf": FileType.PDF_FILES,
            "word": FileType.WORD_DOCUMENTS,
            "excel": FileType.EXCEL_SPREADSHEETS,
            "powerpoint": FileType.POWERPOINT_PRESENTATIONS,
            "audio": FileType.AUDIO_FILES,
            "video": FileType.VIDEO_FILES,
            "archive": FileType.ARCHIVE_FILES,
        }
        return [type_dict[type] for type in types]


class FileDialog:
    """
    A wrapper around tkinter.filedialog
    """

    def __init__(
        self,
        select="file",
        multiple: bool = False,
        title: str | None = None,
        filetypes: list[tuple[str, str]] = [("All files", "*.*")],
        initial_directory: str | None = None,
        open_at_last_dir: bool = True,
    ):
        self.select = select
        if self.select not in ["file", "dir"]:
            raise ValueError("Invalid selection type. Choose 'file' or 'dir'.")

        self.multiple = multiple
        self.title = (
            title or f"Select file{'s' if multiple else ''}"
            if select == "file"
            else "Select directory"
        )
        self.filetypes = filetypes
        self.open_at_last_dir = open_at_last_dir

        self.logger = logger.bind(title=self.__class__.__name__)
        self.last_dir = ""
        self.chosen = None
        self.initial_dir = initial_directory or os.getcwd()

    def _get_dir(self):
        if not self.open_at_last_dir:
            return self.initial_dir
        return self.last_dir or self.initial_dir

    def open_dialog_hidden(self):
        options = {
            "initialdir": self._get_dir(),
            "title": self.title,
        }

        if self.select == "file":
            options["filetypes"] = self.filetypes
            if self.multiple:
                options["multiple"] = True  # type: ignore
            filename = filedialog.askopenfilename(**options)  # type: ignore
        elif self.select == "dir":
            filename = filedialog.askdirectory(**options)  # type: ignore
        else:
            raise ValueError("Invalid selection type. Choose 'file' or 'dir'.")
        if filename:  # type: ignore
            self.last_dir = os.path.dirname(filename[0] if self.multiple else filename)

        _TKINTER_ROOT.update()  # To make the dialog close completely before the next line of code is run
        if filename:
            self.chosen = filename  # type: ignore
            return filename  # type: ignore
        return None

    def open_dialog(self):
        _TKINTER_ROOT.lift()  # Bring the root window to the front
        _TKINTER_ROOT.attributes("-topmost", True)  # Make the root window always appear on top
        filename = self.open_dialog_hidden()
        _TKINTER_ROOT.attributes("-topmost", False)  # Reset the topmost attribute
        self.logger.debug(f"Chosen file: {filename}")
        return filename

    @property
    def chosen_contents(self):
        if self.chosen is None:
            return None
        if self.select == "file":
            return fs.File(self.chosen).read()
        elif self.select == "dir":
            raise NotImplementedError("Not implemented for directories")


class FilePicker:
    def __init__(
        self,
        select="file",
        title: str | None = None,
        filetypes=[FileType.ALL_FILES],
        initial_directory: str | None = None,
        open_at_last_dir: bool = True,
        input_width_class="w-80",
    ) -> None:
        self.open_file_dialog = FileDialog(
            select=select,
            multiple=False,
            title=title,
            filetypes=filetypes,
            initial_directory=initial_directory,
            open_at_last_dir=open_at_last_dir,
        )
        self.logger = logger.bind(title=self.__class__.__name__)
        self.auto_complete = []
        self.filepath: str | None = None
        with ui.row().classes("items-center"):
            self.path_input = (
                ui.input(
                    placeholder="No file selected",
                    autocomplete=self.auto_complete,
                    on_change=self.on_input_change,
                )
                .classes(input_width_class)
                .classes("font-mono")
            )
            self.valid_file_label = ui.label("⚫")
            self.button_open_file_dialog = ui.button(
                icon=ICONS.FOLDER_OPEN, on_click=self.open_dialog
            )

    def open_dialog(self):
        filename = self.open_file_dialog.open_dialog()
        if filename:
            self.filepath = filename
            self.path_input.value = filename
            self.auto_complete.append(filename)
            self.path_input.set_autocomplete(self.auto_complete)
        else:
            self.logger.warning("No file selected")
        return filename

    def on_input_change(self):
        value = self.path_input.value
        if not value:
            self.valid_file_label.text = "⚫"
            return
        if fs.exists(value):
            self.valid_file_label.text = "🟢"
            self.auto_complete.append(value)
            self.path_input.set_autocomplete(self.auto_complete)
        else:
            self.valid_file_label.text = "🔴"

    @property
    def value(self):
        return self.path_input.value


__all__ = ["FileType", "FileDialog", "FilePicker"]
