from __future__ import annotations

import platform
from tkinter import Canvas, Event, Misc, Text
from tkinter.font import Font

system: str = str(platform.system())
if system == "Darwin":
    scroll_inversion: int = -1
else:
    scroll_inversion: int = 1


class TkLineNumError(Exception):
    ...


class TkLineNumbers(Canvas):
    """
    Creates a line number widget for a text widget. Options are the same as a tkinter Canvas widget and add the following:
        * -justify (str): The justification of the line numbers. Can be "left", "right", or "center". Default is "left".
        * -font (tuple | Font | str | None): The font of the line numbers. Default is the text widget's font.
        * -editor (Text): The text widget to attach the line numbers to. (Required) (Second argument after master)

    Methods to be used outside externally:
        * .redraw(): Redraws the widget
        * .resize(): Calculates the required width of the widget and resizes it according to the text widget's font and the number of lines
        * .set_to_ttk_style(): Sets the foreground and background colors to the ttk style of the text widget
        * .reload_font(): Reloads the font of the widget (Requires font as argument)
    """

    def __init__(
        self,
        master: Misc,
        editor: Text,
        font: tuple | Font | str | None = None,
        justify: str = "left",
        *args,
        **kwargs,
    ) -> None:
        """Initializes the widget -- Internal use only"""
        self.textwidget = editor
        self.master = master
        self.justify = justify
        Canvas.__init__(
            self,
            master,
            width=40 if kwargs.get("width") is None else kwargs.get("width"),
            highlightthickness=0
            if kwargs.get("highlightthickness") is None
            else kwargs.get("highlightthickness"),
            borderwidth=2
            if kwargs.get("borderwidth") is None
            else kwargs.get("borderwidth"),
            relief="ridge" if kwargs.get("relief") is None else kwargs.get("relief"),
            *args,
            **kwargs,
        )
        self.set_font(font)
        self.set_to_ttk_style()

        self.bind("<MouseWheel>", self.mouse_scroll, add=True)
        self.bind("<Button-1>", self.click_see, add=True)
        self.bind("<ButtonRelease-1>", self.unclick, add=True)
        self.bind("<Double-Button-1>", self.double_click, add=True)
        self.bind("<Button1-Motion>", self.drag, add=True)

        self.click_pos: None = None

    def redraw(self, *args) -> None:
        """Redraws the widget"""
        self.resize()
        self.delete("all")
        first_line, last_line = int(self.textwidget.index("@0,0").split(".")[0]), int(
            self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        )
        for lineno in range(first_line, last_line + 1):
            if (dlineinfo := self.textwidget.dlineinfo(f"{lineno}.0")) is None:
                continue
            self.create_text(
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

    def mouse_scroll(self, event: Event) -> None:
        """Scrolls the text widget when the mouse wheel is scrolled -- Internal use only"""
        if system == "Darwin":
            self.textwidget.yview_scroll(scroll_inversion * event.delta, "units")
        else:
            self.textwidget.yview_scroll(int(scroll_inversion * (event.delta / 120)), "units")
        self.redraw()

    def click_see(self, event: Event) -> None:
        """When clicking on a line number it scrolls to that line -- Internal use only"""
        # Add shift click
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.mark_set(
            "insert",
            f"{self.textwidget.index(f'@{event.x},{event.y}').split('.')[0]}.0",
        )
        self.textwidget.see("insert")
        first_visible_line, last_visible_line = int(
            self.textwidget.index("@0,0").split(".")[0]
        ), int(
            self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        )
        if (insert := int(self.textwidget.index("insert").split(".")[0])) == first_visible_line:
            self.textwidget.yview_scroll(-1, "units")
        elif insert == last_visible_line:
            self.textwidget.yview_scroll(1, "units")
        self.click_pos = self.textwidget.index("insert")

    def unclick(self, event: Event) -> None:
        """When the mouse button is released it removes the selection -- Internal use only"""
        self.click_pos: None = None

    def double_click(self, event: Event) -> None:
        """Selects the line when double clicked -- Internal use only"""
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.tag_add("sel", "insert", "insert + 1 line")

    def drag(self, event: Event) -> None:
        """When click dragging it selects the text -- Internal use only"""
        if self.click_pos is None:
            return
        start, end = self.textwidget.index("insert"), self.click_pos
        if self.textwidget.compare("insert", ">", self.click_pos):
            start, end = end, start
        self.textwidget.mark_set("insert", f"@0,{event.y}")
        self.textwidget.tag_remove("sel", "1.0", "end")
        self.textwidget.tag_add("sel", start, end)
        first_line, last_line = self.textwidget.index("@0,0").split(".")[0], self.textwidget.index(f"@0,{self.textwidget.winfo_height()}").split(".")[0]
        if end.split(".")[0] == last_line and event.y > self.winfo_y():
            self.textwidget.yview_scroll(1, "units") if system == "Darwin" else self.textwidget.yview_scroll((1 / 120), "units")
            self.textwidget.tag_add("sel", start, str(float(end)+1))
            self.textwidget.mark_set("insert", str(float(end)+1))
            return None
        elif start.split(".")[0] == first_line and event.y < self.winfo_y() + self.winfo_height():
            self.textwidget.yview_scroll(-1, "units") if system == "Darwin" else self.textwidget.yview_scroll((-1 / 120), "units")
            self.textwidget.tag_add("sel", str(float(start)-1), end)
            self.textwidget.mark_set("insert", str(float(start)-1))
            return None
        self.redraw()


    def resize(self) -> None:
        """Resizes the widget to fit the text widget"""
        end = self.textwidget.index("end").split(".")[0]
        self.config(width=self.font.measure(" 1234 ")) if int(
            end
        ) <= 1000 else self.config(width=self.font.measure(f" {end} "))

    def set_to_ttk_style(self) -> None:
        """Sets the widget to the ttk style"""
        self["bg"] = self.tk.eval("ttk::style lookup TLineNumbers -background")
        self.foreground = self.tk.eval("ttk::style lookup TLineNumbers -foreground")

    def reload(self, font: tuple | Font | str = "TkFixedFont") -> None:
        """Reloads the widget with a new font"""
        self.set_font(font)
        self.set_to_ttk_style()
        self.redraw()

    def set_font(self, font: tuple | Font | str | None) -> None:
        """Sets the font of the widget"""
        if isinstance(font, Font):
            self.font: Font = font
        elif isinstance(font, tuple):
            self.font: Font = Font(family=font[0], size=font[1])
        elif isinstance(font, str):
            self.font: Font = Font(name=font, exists=True)
        else:
            self.font: Font = Font(
                family=" ".join(
                    (
                        font := self.textwidget["font"]
                        .replace("{", "")
                        .replace("}", "")
                        .split(" ")
                    )[:-1]
                ),
                size=font[-1],
            )


if __name__ == "__main__":
    from tkinter import Text, Tk
    import platform
    from tkinter.font import Font
    from tkinter.ttk import Style

    system = str(platform.system())

    if system == "Darwin":
        contmand = "Command"
    else:
        contmand = "Control"

    root = Tk()

    style = Style()
    style.configure("TLineNumbers", background="#ffffff", foreground="#2197db")

    text = Text(root, wrap="char", font=("Courier New bold", 15))
    text.pack(side="right")
    text.focus()

    for i in range(500):
        text.insert("end", f"Line {i+1}\n")

    linenums = TkLineNumbers(root, text)
    linenums.pack(fill="y", side="left", expand=True)

    text.bind("<Key>", lambda event: root.after_idle(linenums.redraw), add=True)
    text.bind(f"<BackSpace>", lambda event: root.after_idle(linenums.redraw), add=True)
    text.bind(
        f"<{contmand}-v>", lambda event: root.after_idle(linenums.redraw), add=True
    )
    text["yscrollcommand"] = linenums.redraw

    root.mainloop()
