from __future__ import annotations

from tkinter import Canvas, Misc, Text
from tkinter.font import Font


class TkLineNumbers(Canvas):
    def __init__(self, master: Misc, editor: Text, font: tuple) -> None:
        self.textwidget = editor
        self.master = master
        Canvas.__init__(
            self, master, width=40, highlightthickness=0, borderwidth=2, relief="ridge"
        )
        self.textwidget.bind(
            "<<ContentChanged>>", lambda event: self.redraw(), add=True
        )
        self.font = Font(family=font[0], size=font[1])
        self.set_to_ttk_style()

    def redraw(self, *args) -> None:
        self.resize()
        self.delete("all")
        first_line, last_line = int(self.textwidget.index("@0,0").split(".")[0]), int(
            self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        )
        for lineno in range(first_line, last_line + 1):
            if (dlineinfo := self.textwidget.dlineinfo(f"{lineno}.0")) is None:
                continue
            self.create_text(
                0,
                dlineinfo[1] + 2,
                text=f" {lineno:<4}",
                anchor="nw",
                font=self.font,
                fill=self.foreground,
            )

    def resize(self) -> None:
        end = self.textwidget.index("end").split(".")[0]
        self.config(width=self.font.measure(" 1234 ")) if int(
            end
        ) < 1001 else self.config(width=self.font.measure(f" {end} "))

    def set_to_ttk_style(self) -> None:
        ttk_bg = self.tk.eval("ttk::style lookup TLineNumbers -background")
        self.foreground = self.tk.eval("ttk::style lookup TLineNumbers -foreground")
        self["bg"] = ttk_bg

    def reload(self, font: tuple) -> None:
        self.font = Font(family=font[0], size=font[1])
        self.set_to_ttk_style()
        self.redraw()
