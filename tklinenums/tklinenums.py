from __future__ import annotations

import platform
from tkinter import Canvas, Event, Misc, Text
from tkinter.font import Font

system = str(platform.system())


class TkLineNumbers(Canvas):
    def __init__(
        self, master: Misc, editor: Text, font: tuple | Font, justify: str = "left"
    ) -> None:
        self.textwidget = editor
        self.master = master
        self.justify = justify
        Canvas.__init__(
            self, master, width=40, highlightthickness=0, borderwidth=2, relief="ridge"
        )
        if isinstance(font, Font):
            self.font = font
        else:
            self.font = Font(family=font[0], size=font[1])
        self.set_to_ttk_style()

        self.bind("<MouseWheel>", self.mouse_scroll)

    def redraw(self, *args) -> None:
        self.resize()
        self.delete("all")
        self.unbind_all("Button-1")
        first_line, last_line = int(self.textwidget.index("@0,0").split(".")[0]), int(
            self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        )
        for lineno in range(first_line, last_line + 1):
            if (dlineinfo := self.textwidget.dlineinfo(f"{lineno}.0")) is None:
                continue
            num = self.create_text(
                0
                if self.justify == "left"
                else int(self["width"])
                if self.justify == "right"
                else int(self["width"]) / 2,
                dlineinfo[1],
                text=f" {lineno} " if self.justify != "center" else f"{lineno}",
                anchor={"left": "nw", "right": "ne", "center": "n"}[self.justify],
                font=self.font,
                fill=self.foreground,
            )
            self.tag_bind(num, "<Button-1>", self.click_see)

    def mouse_scroll(self, event: Event) -> None:
        if system == "Darwin":
            self.textwidget.yview_scroll(event.delta, "units")
            self.redraw()
        else:
            self.textwidget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            self.redraw()

    def click_see(self, *args) -> None:
        self.textwidget.mark_set(
            "insert", self.textwidget.index(f"@{args[0].x},{args[0].y}")
        )

    def resize(self) -> None:
        end = self.textwidget.index("end").split(".")[0]
        self.config(width=self.font.measure(" 1234 ")) if int(
            end
        ) <= 1000 else self.config(width=self.font.measure(f" {end} "))

    def set_to_ttk_style(self) -> None:
        ttk_bg = self.tk.eval("ttk::style lookup TLineNumbers -background")
        self.foreground = self.tk.eval("ttk::style lookup TLineNumbers -foreground")
        self["bg"] = ttk_bg

    def reload(self, font: tuple | Font) -> None:
        if isinstance(font, Font):
            self.font = font
        else:
            self.font = Font(family=font[0], size=font[1])
        self.set_to_ttk_style()
        self.redraw()
